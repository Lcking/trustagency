# 📋 Task 7 计划 - Celery + Redis 任务队列配置

**预计耗时**: 1.5 小时  
**优先级**: 高 (OpenAI集成的前置条件)  
**状态**: 准备就绪

---

## 🎯 目标

实现异步任务队列系统，支持长时间运行的AI文章生成任务。

---

## 📝 任务分解

### 阶段 1: Celery 配置 (30分钟)

#### 1.1 创建 Celery 应用
**文件**: `app/celery_app.py`

```python
from celery import Celery
import os

app = Celery(
    'trustagency',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟硬限制
    task_soft_time_limit=25 * 60,  # 25分钟软限制
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

#### 1.2 更新 `.env` 文件
```
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_TASK_SERIALIZER=json
```

#### 1.3 验证Celery配置
```bash
celery -A app.celery_app inspect active
celery -A app.celery_app inspect registered
```

---

### 阶段 2: 任务定义 (30分钟)

#### 2.1 创建任务模块
**文件**: `app/tasks/ai_generation.py`

任务包括:
```python
# 基础任务
@task
async def generate_article_batch(batch_id: str, titles: List[str])

# 单篇生成
@task
async def generate_single_article(title: str, category: str)

# 状态更新
@task
def update_task_status(batch_id: str, status: str, progress: int)

# 错误处理
@task
def handle_generation_error(batch_id: str, error: str)
```

#### 2.2 创建任务队列API
**文件**: `app/routes/tasks.py`

端点:
```
POST /api/tasks/generate-articles        - 提交批量生成任务
GET /api/tasks/{task_id}/status          - 查询任务状态
GET /api/tasks/{task_id}/progress        - 查询进度
POST /api/tasks/{task_id}/cancel         - 取消任务
```

#### 2.3 数据库持久化
在 `AIGenerationTask` 模型中添加:
- `celery_task_id` (关联Celery任务)
- `celery_status` (Celery状态同步)
- `last_progress_update` (最后更新时间)

---

### 阶段 3: Worker 配置 (20分钟)

#### 3.1 创建 Worker 启动脚本
**文件**: `start_celery_worker.sh`

```bash
#!/bin/bash
PYTHONPATH=/path/to/backend celery -A app.celery_app worker \
  --loglevel=info \
  --concurrency=4 \
  --pool=prefork
```

#### 3.2 创建 Beat 调度器脚本
**文件**: `start_celery_beat.sh`

```bash
#!/bin/bash
PYTHONPATH=/path/to/backend celery -A app.celery_app beat \
  --loglevel=info \
  --scheduler=redbeat.RedBeatScheduler
```

#### 3.3 健康检查
```bash
celery -A app.celery_app inspect active
celery -A app.celery_app inspect stats
```

---

### 阶段 4: 监控和测试 (20分钟)

#### 4.1 Flower 监控面板
```bash
pip install flower
celery -A app.celery_app flower --port=5555
# 访问 http://localhost:5555
```

#### 4.2 集成测试
```python
# test_celery_tasks.py
def test_task_submission():
    result = generate_article_batch.delay(batch_id, titles)
    assert result.id

def test_task_status():
    status = get_task_status(batch_id)
    assert status in ['pending', 'processing', 'completed']
```

#### 4.3 性能测试
- 单任务执行时间
- 并发处理能力
- 错误恢复能力

---

## 🔌 集成点

### 与 OpenAI 集成 (Task 8)
```python
@task(bind=True)
async def generate_article_batch(self, batch_id, titles):
    # 更新进度
    self.update_state(state='PROGRESS', meta={'current': 0, 'total': len(titles)})
    
    for i, title in enumerate(titles):
        # 调用 OpenAI
        content = openai.create_article(title)
        
        # 保存到数据库
        save_generated_article(title, content)
        
        # 更新进度
        progress = (i + 1) / len(titles) * 100
        self.update_state(state='PROGRESS', meta={'current': i+1, 'total': len(titles), 'progress': progress})
    
    return {'batch_id': batch_id, 'status': 'completed'}
```

### 与前端集成
```javascript
// 提交任务
const response = await fetch('/api/tasks/generate-articles', {
  method: 'POST',
  body: JSON.stringify({ titles: [...], category: 'guide' })
});
const { task_id } = await response.json();

// 轮询进度
setInterval(async () => {
  const progress = await fetch(`/api/tasks/${task_id}/progress`);
  const data = await progress.json();
  updateProgressBar(data.progress);
}, 1000);
```

---

## 📦 依赖确认

```bash
# 已安装
✅ celery==5.3.4
✅ redis==5.0.1

# 推荐安装
pip install flower==2.0.1      # 监控面板
pip install redbeat==0.13.0    # Redis Beat调度器
```

---

## 🚀 启动命令

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
bash start_celery_worker.sh

# Terminal 3: Celery Beat (可选)
bash start_celery_beat.sh

# Terminal 4: Flower 监控 (可选)
celery -A app.celery_app flower

# Terminal 5: FastAPI Backend
bash start_backend_daemon.sh
```

---

## ✅ 验证清单

- [ ] Celery 应用创建
- [ ] Redis 连接验证
- [ ] Worker 进程启动
- [ ] 任务提交成功
- [ ] 进度跟踪正常
- [ ] 错误处理完善
- [ ] Flower 监控可用
- [ ] 集成测试通过

---

## 📊 预期成果

```
完成后的系统架构:

┌─────────────┐
│   FastAPI   │──────┐
└─────────────┘      │
                     ├─→ ┌─────────────┐
                     │   │   Redis     │
                     │   └─────────────┘
                     │          ▲
                     │          │
                     └─→ ┌──────────────┐
                         │   Celery     │
                         │   Workers    │
                         └──────────────┘

可用功能:
- ✅ 异步任务提交
- ✅ 实时进度跟踪
- ✅ 任务状态管理
- ✅ 错误自动重试
- ✅ 任务超时处理
- ✅ 可视化监控
```

---

## 🔗 参考资源

- [Celery 官方文档](https://docs.celeryproject.io/)
- [Redis 官方文档](https://redis.io/docs/)
- [Flower 文档](https://flower.readthedocs.io/)
- [FastAPI + Celery 集成](https://fastapi.tiangolo.com/deployment/concepts/#background-tasks)

---

## 🎓 关键学习点

1. **Celery 架构**: Producer → Broker → Worker → Result Backend
2. **消息序列化**: JSON vs Pickle vs MessagePack
3. **任务重试策略**: 指数退避、最大重试次数
4. **分布式锁**: 防止并发冲突
5. **监控和告警**: Flower、Sentry 集成

---

**准备状态**: ✅ 就绪  
**下一步**: 立即开始 Task 7 实施  
**预计完成**: 2025-11-06 19:20 UTC
