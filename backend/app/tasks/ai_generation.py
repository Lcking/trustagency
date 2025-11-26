"""
AI 文章生成任务模块

提供异步任务定义，用于处理 OpenAI 文章生成。
"""

from typing import List, Dict, Any
from datetime import datetime
from app.celery_app import app
from app.database import SessionLocal
from app.models import AIGenerationTask
from sqlalchemy import update as sql_update
from slugify import slugify


def _update_batch_completion(db, batch_id: str, success: bool, article_id: int = None, error_title: str = None):
    """
    更新批次任务的完成计数，并检查是否全部完成
    
    使用 SQL 原子操作防止并发更新时的竞态条件。
    
    Args:
        db: 数据库会话
        batch_id: 批次ID
        success: 是否成功
        article_id: 成功生成的文章ID（可选）
        error_title: 失败的文章标题（可选）
    """
    from sqlalchemy import func
    from sqlalchemy.sql import case
    
    try:
        # 使用原子操作更新计数器（防止竞态条件）
        if success:
            # 原子递增 completed_count
            db.execute(
                sql_update(AIGenerationTask).where(
                    AIGenerationTask.batch_id == batch_id
                ).values(
                    completed_count=AIGenerationTask.completed_count + 1,
                    last_progress_update=datetime.utcnow()
                )
            )
            db.commit()
            
            # 更新 generated_articles 列表（需要锁定行以防止并发问题）
            if article_id:
                # 使用 FOR UPDATE 锁定行
                task = db.query(AIGenerationTask).filter(
                    AIGenerationTask.batch_id == batch_id
                ).with_for_update().first()
                
                if task:
                    current_articles = task.generated_articles or []
                    current_articles.append(article_id)
                    task.generated_articles = current_articles
                    db.commit()
        else:
            # 原子递增 failed_count
            db.execute(
                sql_update(AIGenerationTask).where(
                    AIGenerationTask.batch_id == batch_id
                ).values(
                    failed_count=AIGenerationTask.failed_count + 1,
                    has_error=True,
                    last_progress_update=datetime.utcnow()
                )
            )
            db.commit()
            
            # 更新 failed_titles 列表（需要锁定行以防止并发问题）
            if error_title:
                # 使用 FOR UPDATE 锁定行
                task = db.query(AIGenerationTask).filter(
                    AIGenerationTask.batch_id == batch_id
                ).with_for_update().first()
                
                if task:
                    current_failed = task.failed_titles or []
                    current_failed.append(error_title)
                    task.failed_titles = current_failed
                    db.commit()
        
        # 重新获取更新后的状态
        task = db.query(AIGenerationTask).filter(
            AIGenerationTask.batch_id == batch_id
        ).first()
        
        if not task:
            print(f"[WARNING] Batch {batch_id} not found")
            return
        
        total_count = task.total_count or 0
        completed = task.completed_count or 0
        failed = task.failed_count or 0
        
        # 防止重试导致 failed_count 超过 total_count
        # 只统计实际处理完成的任务数（不重复计算重试）
        total_processed = min(completed + failed, total_count)
        
        # 计算进度（确保不超过 100%）
        progress = min(int((total_processed / total_count) * 100), 100) if total_count > 0 else 0
        
        # 更新进度（使用当前读取的值，因为计数器已经原子更新了）
        update_values = {
            'progress': progress
        }
        
        # 如果 failed_count 超过允许范围，限制它
        if failed > total_count - completed:
            update_values['failed_count'] = total_count - completed
        
        db.execute(
            sql_update(AIGenerationTask).where(
                AIGenerationTask.batch_id == batch_id
            ).values(**update_values)
        )
        
        # 检查是否全部完成（completed + failed 达到 total）
        if total_processed >= total_count:
            # 批次处理完成即标记为 completed（部分失败的信息由 has_error/failed_count/failed_titles 记录）
            db.execute(
                sql_update(AIGenerationTask).where(
                    AIGenerationTask.batch_id == batch_id
                ).values(
                    status='completed',
                    celery_status='SUCCESS',
                    completed_at=datetime.utcnow()
                )
            )
            print(f"[BATCH] Batch {batch_id} completed: {completed}/{total_count} success, {failed} failed")
        
        db.commit()
        
    except Exception as e:
        print(f"[ERROR] Failed to update batch completion: {str(e)}")
        db.rollback()


# Phase 2: 任务定义

@app.task(bind=True, name='tasks.generate_article_batch')
def generate_article_batch(
    self, 
    batch_id: str, 
    titles: List[str], 
    section_id: int,
    category_id: int,
    platform_id: int = None,
    creator_id: int = None,
    auto_publish: bool = False
):
    """
    批量生成文章的异步任务（新逻辑）
    
    Args:
        batch_id: 批次ID，用于关联数据库记录
        titles: 文章标题列表
        section_id: 栏目ID
        category_id: 分类ID
        platform_id: 平台ID (某些栏目需要，可选)
        creator_id: 创建者ID
        auto_publish: 是否直接发布（默认False，保存为草稿）
    
    Returns:
        dict: 包含生成结果的字典
    
    Raises:
        Exception: 生成失败时抛出异常
    """
    try:
        # 获取任务记录以读取 AI 配置
        db = SessionLocal()
        task_record = db.query(AIGenerationTask).filter(
            AIGenerationTask.batch_id == batch_id
        ).first()
        
        ai_config_id = task_record.ai_config_id if task_record else None
        
        # 更新任务状态为处理中
        db.execute(
            sql_update(AIGenerationTask).where(
                AIGenerationTask.batch_id == batch_id
            ).values(
                status='processing',
                celery_status='STARTED',
                celery_task_id=self.request.id,
                started_at=datetime.utcnow(),
                last_progress_update=datetime.utcnow()
            )
        )
        db.commit()
        
        # 初始化进度
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': len(titles),
                'progress': 0,
                'status': '正在初始化...'
            }
        )
        
        results = []
        
        # 逐篇生成文章
        for i, title in enumerate(titles):
            try:
                # 生成单篇文章（传递 AI 配置 ID 和发布选项）
                result = generate_single_article.apply_async(
                    args=(
                        title, 
                        section_id,
                        category_id,
                        platform_id,
                        batch_id,
                        creator_id,
                        ai_config_id,  # 传递 AI 配置 ID
                        auto_publish   # 传递发布选项
                    ),
                    queue='ai_generation'
                )
                results.append({
                    'title': title,
                    'task_id': result.id,
                    'status': 'pending'
                })
                
                # 更新进度
                progress = ((i + 1) / len(titles)) * 100
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': len(titles),
                        'progress': progress,
                        'status': f'已生成 {i + 1}/{len(titles)} 篇'
                    }
                )
                
                # 更新数据库
                db.execute(
                    sql_update(AIGenerationTask).where(
                        AIGenerationTask.batch_id == batch_id
                    ).values(
                        progress=int(progress),
                        last_progress_update=datetime.utcnow()
                    )
                )
                db.commit()
                
            except Exception as e:
                print(f"[ERROR] Failed to submit task for title '{title}': {str(e)}")
                results.append({
                    'title': title,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # 统计提交任务失败的数量（不是子任务执行失败）
        submit_fail_count = sum(1 for r in results if r.get('status') == 'failed')
        
        # 如果所有任务都提交失败，直接标记为失败
        if submit_fail_count == len(titles):
            db.execute(
                sql_update(AIGenerationTask).where(
                    AIGenerationTask.batch_id == batch_id
                ).values(
                    status='failed',
                    celery_status='FAILURE',
                    has_error=True,
                    error_message='所有子任务提交失败',
                    completed_at=datetime.utcnow(),
                    last_progress_update=datetime.utcnow()
                )
            )
        else:
            # 子任务已提交，批次保持 processing 状态
            # 等待子任务完成后由 generate_single_article 更新
            db.execute(
                sql_update(AIGenerationTask).where(
                    AIGenerationTask.batch_id == batch_id
                ).values(
                    celery_status='TASKS_SUBMITTED',
                    last_progress_update=datetime.utcnow()
                )
            )
        
        db.commit()
        db.close()
        
        return {
            'batch_id': batch_id,
            'status': 'processing',  # 子任务仍在执行中
            'total': len(titles),
            'submitted': len(titles) - submit_fail_count,
            'results': results
        }
        
    except Exception as e:
        # 更新任务状态为失败
        try:
            db = SessionLocal()
            db.execute(
                sql_update(AIGenerationTask).where(
                    AIGenerationTask.batch_id == batch_id
                ).values(
                    status='failed',
                    celery_status='FAILURE',
                    has_error=True,
                    error_message=str(e),
                    completed_at=datetime.utcnow(),
                    last_progress_update=datetime.utcnow()
                )
            )
            db.commit()
            db.close()
        except:
            pass
        
        raise Exception(f"Batch generation failed: {str(e)}")


@app.task(bind=True, name='tasks.generate_single_article', max_retries=3)
def generate_single_article(
    self, 
    title: str, 
    section_id: int,
    category_id: int,
    platform_id: int = None,
    batch_id: str = None,
    creator_id: int = None,
    ai_config_id: int = None,
    auto_publish: bool = False
):
    """
    生成单篇文章的异步任务（新逻辑）
    
    Args:
        title: 文章标题
        section_id: 栏目ID
        category_id: 分类ID
        platform_id: 平台ID (可选)
        batch_id: 所属批次ID（可选）
        creator_id: 创建者ID
        ai_config_id: AI配置ID
        auto_publish: 是否直接发布（默认False）
    
    Returns:
        dict: 生成的文章信息
    
    Raises:
        Exception: 生成失败时抛出异常
    """
    try:
        print(f"[TASK] Generating article for title: '{title}'")
        
        # 集成 OpenAI API（使用数据库中的 AI 配置）
        try:
            from app.services.openai_service import OpenAIService
            
            print(f"[OPENAI] 调用 AI 生成文章: {title} (配置ID: {ai_config_id})")
            content = OpenAIService.generate_article(
                title, 
                f"section_{section_id}",
                ai_config_id=ai_config_id  # 传递 AI 配置 ID
            )
            
        except Exception as e:
            # OpenAI 服务不可用时，记录错误并使用占位符
            print(f"[ERROR] AI 服务调用失败: {str(e)}")
            # 重新抛出异常让 Celery 处理重试
            raise Exception(f"AI 生成失败: {str(e)}")
        
        # 保存文章到数据库
        from app.database import SessionLocal
        from app.models import Article
        
        db = SessionLocal()
        
        try:
            # 生成 slug
            slug = slugify(title)
            
            # 检查 slug 唯一性
            existing = db.query(Article).filter(Article.slug == slug).first()
            if existing:
                # 添加时间戳以确保唯一性
                slug = f"{slug}-{datetime.utcnow().timestamp()}"
            
            # 创建文章对象
            article = Article(
                title=title,
                slug=slug,
                content=content,
                section_id=section_id,
                category_id=category_id,
                platform_id=platform_id,  # 可能为 None
                author_id=creator_id or 1,  # 使用传入的creator_id或默认为1
                is_published=auto_publish,  # 根据选项决定是否直接发布
                created_at=datetime.utcnow()
            )
            
            publish_status = "已发布" if auto_publish else "草稿"
            print(f"[ARTICLE] 文章状态: {publish_status}")
            
            db.add(article)
            db.commit()
            db.refresh(article)
            
            print(f"[SUCCESS] Article generated and saved: {title} (ID: {article.id})")
            
            result = {
                'title': title,
                'article_id': article.id,
                'content': content,
                'section_id': section_id,
                'category_id': category_id,
                'platform_id': platform_id,
                'generated_at': datetime.utcnow().isoformat(),
                'task_id': self.request.id,
                'batch_id': batch_id
            }
            
            # 更新批次的 completed_count，并检查是否全部完成
            # 注意：这里单独捕获异常，不让批次更新失败导致整个任务重试
            # 因为文章已经成功创建，重试会导致文章重复
            if batch_id:
                try:
                    _update_batch_completion(db, batch_id, success=True, article_id=article.id)
                except Exception as batch_error:
                    print(f"[WARNING] 批次状态更新失败，但文章已成功创建: {str(batch_error)}")
            
        finally:
            db.close()
        
        return result
        
    except Exception as exc:
        print(f"[ERROR] Failed to generate article '{title}': {str(exc)}")
        
        # 更新批次的 failed_count
        if batch_id:
            db = None
            try:
                from app.database import SessionLocal
                db = SessionLocal()
                _update_batch_completion(db, batch_id, success=False, error_title=title)
            except Exception as update_error:
                print(f"[ERROR] Failed to update batch status: {str(update_error)}")
            finally:
                if db:
                    db.close()
        
        # 重试策略
        try:
            raise self.retry(exc=exc, countdown=60)
        except:
            raise


@app.task(bind=True, name='tasks.update_task_status')
def update_task_status(self, task_id: str, status: str, progress: int = 0):
    """
    更新任务状态到数据库
    
    Args:
        task_id: 任务ID
        status: 任务状态 (pending, processing, completed, failed)
        progress: 进度百分比 (0-100)
    
    Returns:
        dict: 更新结果
    """
    try:
        db = SessionLocal()
        db.execute(
            sql_update(AIGenerationTask).where(
                AIGenerationTask.id == task_id
            ).values(
                celery_status=status,
                last_progress_update=datetime.utcnow()
            )
        )
        db.commit()
        db.close()
        
        return {
            'task_id': task_id,
            'status': status,
            'progress': progress,
            'updated_at': datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"[ERROR] Failed to update task status: {str(e)}")
        raise


@app.task(bind=True, name='tasks.handle_generation_error')
def handle_generation_error(self, task_id: str, error_message: str):
    """
    处理生成错误
    
    Args:
        task_id: 任务ID
        error_message: 错误信息
    
    Returns:
        dict: 处理结果
    """
    try:
        db = SessionLocal()
        db.execute(
            sql_update(AIGenerationTask).where(
                AIGenerationTask.id == task_id
            ).values(
                celery_status='FAILURE',
                last_progress_update=datetime.utcnow()
            )
        )
        db.commit()
        db.close()
        
        print(f"[ERROR HANDLED] Task {task_id}: {error_message}")
        
        return {
            'task_id': task_id,
            'error': error_message,
            'handled_at': datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"[ERROR] Failed to handle error: {str(e)}")
        raise


# Phase 2: 监控任务状态
@app.task(bind=True, name='tasks.monitor_task_progress')
def monitor_task_progress(self, task_id: str):
    """
    监控任务进度
    
    Args:
        task_id: 要监控的任务ID
    
    Returns:
        dict: 任务进度信息
    """
    try:
        db = SessionLocal()
        task = db.query(AIGenerationTask).filter(
            AIGenerationTask.id == task_id
        ).first()
        db.close()
        
        if not task:
            return {'error': f'Task {task_id} not found'}
        
        return {
            'task_id': task_id,
            'celery_status': task.celery_status,
            'celery_task_id': task.celery_task_id,
            'last_update': task.last_progress_update.isoformat() if task.last_progress_update else None
        }
    except Exception as e:
        print(f"[ERROR] Failed to monitor task: {str(e)}")
        raise
