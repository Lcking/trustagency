"""
OpenAI API 集成服务

提供与 OpenAI API 交互的功能，包括文章生成、文本补全等。
"""

import os
from typing import Optional, List
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
import logging

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI API 服务类"""

    # API 配置
    MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1500"))
    TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    # 初始化客户端
    client: Optional[OpenAI] = None

    @classmethod
    def initialize(cls):
        """初始化 OpenAI 客户端"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 环境变量未设置")

        cls.client = OpenAI(api_key=api_key)
        logger.info(f"✅ OpenAI 客户端已初始化，模型: {cls.MODEL}")

    @classmethod
    def generate_article(
        cls,
        title: str,
        category: str = "guide",
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """
        生成文章内容

        Args:
            title: 文章标题
            category: 文章分类
            max_retries: 最大重试次数
            **kwargs: 其他参数

        Returns:
            生成的文章内容

        Raises:
            Exception: 如果生成失败
        """
        if not cls.client:
            cls.initialize()

        # 构建 prompt
        prompt = cls._build_prompt(title, category)

        for attempt in range(max_retries):
            try:
                logger.info(f"[尝试 {attempt + 1}] 生成文章: {title}")

                response = cls.client.chat.completions.create(
                    model=cls.MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个专业的技术文章作者。请用中文生成高质量的技术文章。"
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
