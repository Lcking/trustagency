"""
OpenAI API 集成服务

提供与 OpenAI API 交互的功能，包括文章生成、文本补全等。
支持从数据库 AI 配置动态初始化。
"""

import os
from typing import Optional, List, Dict, Any
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
import logging

logger = logging.getLogger(__name__)


def normalize_api_endpoint(endpoint: str) -> str:
    """规范化 API 端点 URL"""
    endpoint = endpoint.rstrip('/')
    
    # OpenAI 官方 API - 自动补全路径
    if 'api.openai.com' in endpoint:
        if not endpoint.endswith('/chat/completions') and not endpoint.endswith('/completions'):
            if endpoint.endswith('/v1'):
                return endpoint  # 返回 base_url，OpenAI SDK 会自动处理
            else:
                return endpoint + '/v1'
    
    # DeepSeek
    if 'api.deepseek.com' in endpoint:
        if not endpoint.endswith('/v1'):
            return endpoint + '/v1'
    
    return endpoint


class OpenAIService:
    """OpenAI API 服务类"""

    # 默认 API 配置（从环境变量）
    MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    # 初始化客户端
    client: Optional[OpenAI] = None
    current_config: Optional[Dict[str, Any]] = None

    @classmethod
    def initialize(cls, config: Optional[Dict[str, Any]] = None):
        """
        初始化 OpenAI 客户端
        
        Args:
            config: AI配置字典，包含 api_key, api_endpoint, model_name 等
                   如果为 None，则从环境变量读取
        """
        if config:
            # 从配置字典初始化
            api_key = config.get('api_key')
            api_endpoint = config.get('api_endpoint', 'https://api.openai.com/v1')
            
            if not api_key:
                raise ValueError("AI 配置中缺少 api_key")
            
            # 规范化端点
            base_url = normalize_api_endpoint(api_endpoint)
            
            cls.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            cls.MODEL = config.get('model_name', cls.MODEL)
            cls.MAX_TOKENS = config.get('max_tokens', cls.MAX_TOKENS)
            cls.TEMPERATURE = config.get('temperature', cls.TEMPERATURE)
            cls.current_config = config
            
            logger.info(f"✅ OpenAI 客户端已初始化（来自数据库配置），模型: {cls.MODEL}, 端点: {base_url}")
        else:
            # 从环境变量初始化
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY 环境变量未设置")

            cls.client = OpenAI(api_key=api_key)
            cls.current_config = None
            logger.info(f"✅ OpenAI 客户端已初始化（来自环境变量），模型: {cls.MODEL}")
    
    @classmethod
    def initialize_from_db(cls, ai_config_id: int = None):
        """
        从数据库初始化 AI 配置
        
        Args:
            ai_config_id: AI配置ID，如果为 None 则使用默认配置
        """
        from app.database import SessionLocal
        from app.models import AIConfig
        
        db = SessionLocal()
        try:
            if ai_config_id:
                config = db.query(AIConfig).filter(
                    AIConfig.id == ai_config_id,
                    AIConfig.is_active == True
                ).first()
            else:
                # 获取默认配置
                config = db.query(AIConfig).filter(
                    AIConfig.is_default == True,
                    AIConfig.is_active == True
                ).first()
            
            if not config:
                raise ValueError(f"未找到可用的 AI 配置 (ID: {ai_config_id})")
            
            config_dict = {
                'api_key': config.api_key,
                'api_endpoint': config.api_endpoint,
                'model_name': config.model_name,
                'max_tokens': config.max_tokens,
                'temperature': config.temperature / 10.0 if config.temperature > 1 else config.temperature,  # 处理 0-10 范围的温度值
                'system_prompt': config.system_prompt,
                'name': config.name
            }
            
            cls.initialize(config_dict)
            logger.info(f"✅ 已加载 AI 配置: {config.name}")
            
        finally:
            db.close()

    @classmethod
    def generate_article(
        cls,
        title: str,
        category: str = "guide",
        max_retries: int = 3,
        ai_config_id: int = None,
        **kwargs
    ) -> str:
        """
        生成文章内容

        Args:
            title: 文章标题
            category: 文章分类
            max_retries: 最大重试次数
            ai_config_id: AI配置ID，如果提供则从数据库加载配置
            **kwargs: 其他参数

        Returns:
            生成的文章内容

        Raises:
            Exception: 如果生成失败
        """
        # 如果提供了 ai_config_id，从数据库初始化
        if ai_config_id:
            cls.initialize_from_db(ai_config_id)
        elif not cls.client:
            cls.initialize()

        # 构建 prompt
        prompt = cls._build_prompt(title, category)
        
        # 获取系统提示词（如果配置中有的话）
        system_prompt = "你是一个专业的技术文章作者。请用中文生成高质量的技术文章。"
        if cls.current_config and cls.current_config.get('system_prompt'):
            system_prompt = cls.current_config['system_prompt']

        for attempt in range(max_retries):
            try:
                logger.info(f"[尝试 {attempt + 1}] 生成文章: {title}（模型: {cls.MODEL}）")

                response = cls.client.chat.completions.create(
                    model=cls.MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=cls.TEMPERATURE,
                    max_tokens=cls.MAX_TOKENS,
                    top_p=0.95,
                )

                content = response.choices[0].message.content
                logger.info(f"✅ 文章生成成功: {title} ({len(content)} 字符)")

                return content

            except RateLimitError as e:
                logger.warning(f"⚠️  速率限制，等待后重试: {str(e)}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                raise Exception(f"速率限制错误: {str(e)}")

            except APIConnectionError as e:
                logger.warning(f"⚠️  连接错误，正在重试: {str(e)}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
                    continue
                raise Exception(f"连接错误: {str(e)}")

            except APIError as e:
                logger.error(f"❌ API 错误: {str(e)}")
                raise Exception(f"API 错误: {str(e)}")
            
            except Exception as e:
                logger.error(f"❌ 未知错误: {str(e)}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
                    continue
                raise Exception(f"生成失败: {str(e)}")

        raise Exception(f"生成失败，已重试 {max_retries} 次")

    @classmethod
    def generate_article_batch(
        cls,
        titles: List[str],
        category: str = "guide"
    ) -> List[dict]:
        """
        批量生成多篇文章

        Args:
            titles: 标题列表
            category: 分类

        Returns:
            包含生成结果的字典列表
        """
        results = []

        for i, title in enumerate(titles):
            try:
                logger.info(f"📝 生成第 {i + 1}/{len(titles)} 篇: {title}")

                content = cls.generate_article(title, category)

                results.append({
                    "title": title,
                    "content": content,
                    "category": category,
                    "status": "success"
                })

            except Exception as e:
                logger.error(f"❌ 生成失败: {title} - {str(e)}")

                results.append({
                    "title": title,
                    "error": str(e),
                    "category": category,
                    "status": "failed"
                })

        return results

    @classmethod
    def _build_prompt(cls, title: str, category: str) -> str:
        """
        构建生成提示词

        Args:
            title: 文章标题
            category: 分类

        Returns:
            提示词
        """
        category_descriptions = {
            "guide": "入门指南，包含背景、基础概念、实践步骤和最佳实践",
            "tutorial": "深度教程，包含详细步骤、代码示例、常见问题和解决方案",
            "advanced": "高级内容，面向有经验的开发者，包含原理、优化和架构设计",
            "news": "新闻或更新摘要，包含关键信息、影响和未来展望",
            "comparison": "对比分析，比较不同方案的优缺点、使用场景",
        }

        category_desc = category_descriptions.get(category, "技术文章")

        prompt = f"""请根据以下要求生成一篇高质量的技术文章：

标题: {title}
分类: {category_desc}

要求:
1. 字数: 1000-1500 字
2. 结构: 包含引言、核心内容、实践建议、总结
3. 风格: 专业、清晰、易懂，避免过度冗长
4. 格式: 使用 Markdown 格式，包含标题层级、代码块、列表等
5. 质量: 确保信息准确、实用、有价值

请直接输出文章内容，不需要额外说明。"""

        return prompt

    @classmethod
    def health_check(cls) -> dict:
        """
        健康检查

        Returns:
            包含健康状态的字典
        """
        try:
            if not cls.client:
                return {
                    "status": "not_initialized",
                    "message": "OpenAI 客户端未初始化"
                }

            # 尝试调用 API
            response = cls.client.models.list()

            return {
                "status": "healthy",
                "message": "OpenAI API 连接正常",
                "model": cls.MODEL,
                "models_available": len(response.data) if hasattr(response, 'data') else 0
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"连接错误: {str(e)}",
                "error": str(e)
            }


# 初始化全局服务实例
def initialize_openai_service():
    """初始化 OpenAI 服务"""
    try:
        OpenAIService.initialize()
        logger.info("✅ OpenAI 服务初始化成功")
    except Exception as e:
        logger.warning(f"⚠️  OpenAI 服务初始化失败: {str(e)}")
