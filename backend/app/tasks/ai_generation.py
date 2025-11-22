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


# Phase 2: 任务定义

@app.task(bind=True, name='tasks.generate_article_batch')
def generate_article_batch(
    self, 
    batch_id: str, 
    titles: List[str], 
    section_id: int,
    category_id: int,
    platform_id: int = None,
    creator_id: int = None
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
    
    Returns:
        dict: 包含生成结果的字典
    
    Raises:
        Exception: 生成失败时抛出异常
    """
    try:
        # 更新任务状态为处理中
        db = SessionLocal()
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
                # 生成单篇文章
                result = generate_single_article.apply_async(
                    args=(
                        title, 
                        section_id,
                        category_id,
                        platform_id,
                        batch_id,
                        creator_id
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
        
        # 更新任务状态为成功
        db.execute(
            sql_update(AIGenerationTask).where(
                AIGenerationTask.batch_id == batch_id
            ).values(
                status='completed',
                celery_status='SUCCESS',
                completed_at=datetime.utcnow(),
                last_progress_update=datetime.utcnow()
            )
        )
        db.commit()
        db.close()
        
        return {
            'batch_id': batch_id,
            'status': 'completed',
            'total': len(titles),
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
    creator_id: int = None
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
    
    Returns:
        dict: 生成的文章信息
    
    Raises:
        Exception: 生成失败时抛出异常
    """
    try:
        print(f"[TASK] Generating article for title: '{title}'")
        
        # 集成 OpenAI API
        try:
            from app.services.openai_service import OpenAIService
            
            print(f"[OPENAI] 调用 OpenAI 生成文章: {title}")
            content = OpenAIService.generate_article(title, f"section_{section_id}")
            
        except ImportError:
            # OpenAI 服务不可用时，使用占位符
            print(f"[PLACEHOLDER] OpenAI 服务不可用，使用占位符")
            content = f"""
# {title}

## 介绍
这是关于 {title} 的文章。

## 内容
这是自动生成的文章内容。
在集成 OpenAI API 后，此处将显示 AI 生成的内容。

## 结论
更多内容将在 OpenAI 集成完成后生成。

生成时间: {datetime.utcnow().isoformat()}
"""
        
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
                is_published=False,  # 默认不发布
                created_at=datetime.utcnow()
            )
            
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
            
        finally:
            db.close()
        
        return result
        
    except Exception as exc:
        print(f"[ERROR] Failed to generate article '{title}': {str(exc)}")
        
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
