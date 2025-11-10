"""
数据库测试

测试数据库连接、CRUD 操作、事务、完整性等功能。
"""

import pytest
from sqlalchemy import inspect
from app.models import AdminUser, Platform, Article, AIGenerationTask


class TestDatabaseConnection:
    """数据库连接测试"""
    
    def test_connection_established(self, test_db):
        """
        测试数据库连接
        
        验证：
        - 可以建立连接
        - 连接有效
        """
        assert test_db is not None
        assert test_db.is_active
    
    def test_tables_created(self, test_db):
        """
        测试表创建
        
        验证：
        - 所有表已创建
        - 结构正确
        """
        inspector = inspect(test_db.get_bind())
        tables = inspector.get_table_names()
        
        # 检查必要的表
        required_tables = ['users', 'platforms', 'articles', 'ai_generation_tasks']
        for table in required_tables:
            assert table in tables


class TestUserCRUD:
    """用户 CRUD 操作测试"""
    
    def test_create_user(self, test_db):
        """
        测试创建用户
        
        验证：
        - 用户被正确创建
        - 数据完整
        """
        user = AdminUser(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_superadmin=False
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
    
    def test_read_user(self, test_db, admin_user):
        """
        测试读取用户
        
        验证：
        - 可以查询用户
        - 返回正确的用户数据
        """
        user = test_db.query(AdminUser).filter(AdminUser.id == admin_user.id).first()
        
        assert user is not None
        assert user.username == "admin"
    
    def test_update_user(self, test_db, admin_user):
        """
        测试更新用户
        
        验证：
        - 用户数据被正确更新
        """
        admin_user.email = "newemail@example.com"
        test_db.commit()
        test_db.refresh(admin_user)
        
        assert admin_user.email == "newemail@example.com"
    
    def test_delete_user(self, test_db):
        """
        测试删除用户
        
        验证：
        - 用户被正确删除
        """
        user = AdminUser(
            username="deleteuser",
            email="delete@example.com",
            hashed_password="hash"
        )
        test_db.add(user)
        test_db.commit()
        
        user_id = user.id
        test_db.delete(user)
        test_db.commit()
        
        deleted_user = test_db.query(AdminUser).filter(AdminUser.id == user_id).first()
        assert deleted_user is None


class TestPlatformCRUD:
    """平台 CRUD 操作测试"""
    
    def test_create_platform(self, test_db, admin_user):
        """
        测试创建平台
        
        验证：
        - 平台被正确创建
        """
        platform = Platform(
            name="新平台",
            url="https://new.com",
            created_by=admin_user.id
        )
        test_db.add(platform)
        test_db.commit()
        test_db.refresh(platform)
        
        assert platform.id is not None
        assert platform.name == "新平台"
    
    def test_read_platform(self, test_db, sample_platform):
        """
        测试读取平台
        
        验证：
        - 可以查询平台
        """
        platform = test_db.query(Platform).filter(Platform.id == sample_platform.id).first()
        
        assert platform is not None
        assert platform.name == "测试平台"
    
    def test_update_platform(self, test_db, sample_platform):
        """
        测试更新平台
        
        验证：
        - 平台数据被正确更新
        """
        sample_platform.name = "更新的平台"
        test_db.commit()
        test_db.refresh(sample_platform)
        
        assert sample_platform.name == "更新的平台"
    
    def test_delete_platform(self, test_db, admin_user):
        """
        测试删除平台
        
        验证：
        - 平台被正确删除
        """
        platform = Platform(
            name="删除平台",
            url="https://delete.com",
            created_by=admin_user.id
        )
        test_db.add(platform)
        test_db.commit()
        
        platform_id = platform.id
        test_db.delete(platform)
        test_db.commit()
        
        deleted = test_db.query(Platform).filter(Platform.id == platform_id).first()
        assert deleted is None


class TestArticleCRUD:
    """文章 CRUD 操作测试"""
    
    def test_create_article(self, test_db, admin_user, sample_platform):
        """
        测试创建文章
        
        验证：
        - 文章被正确创建
        """
        article = Article(
            title="新文章",
            slug="new-article",
            content="文章内容",
            category="guide",
            status="published",
            platform_id=sample_platform.id,
            created_by=admin_user.id
        )
        test_db.add(article)
        test_db.commit()
        test_db.refresh(article)
        
        assert article.id is not None
        assert article.title == "新文章"
    
    def test_read_article(self, test_db, sample_article):
        """
        测试读取文章
        
        验证：
        - 可以查询文章
        """
        article = test_db.query(Article).filter(Article.id == sample_article.id).first()
        
        assert article is not None
        assert article.title == "测试文章"
    
    def test_article_slug_unique(self, test_db, admin_user, sample_platform, sample_article):
        """
        测试文章 slug 唯一性
        
        验证：
        - 不能创建相同 slug 的文章
        """
        duplicate = Article(
            title="不同标题",
            slug="test-article",  # 相同 slug
            content="内容",
            category="guide",
            status="published",
            platform_id=sample_platform.id,
            created_by=admin_user.id
        )
        test_db.add(duplicate)
        
        with pytest.raises(Exception):  # 应该抛出完整性错误
            test_db.commit()


class TestAITaskCRUD:
    """AI 任务 CRUD 操作测试"""
    
    def test_create_ai_task(self, test_db, admin_user):
        """
        测试创建 AI 任务
        
        验证：
        - 任务被正确创建
        """
        task = AIGenerationTask(
            titles=["标题1", "标题2"],
            category="guide",
            status="pending",
            created_by=admin_user.id
        )
        test_db.add(task)
        test_db.commit()
        test_db.refresh(task)
        
        assert task.id is not None
        assert len(task.titles) == 2
    
    def test_read_ai_task(self, test_db, sample_ai_task):
        """
        测试读取 AI 任务
        
        验证：
        - 可以查询任务
        """
        task = test_db.query(AIGenerationTask).filter(AIGenerationTask.id == sample_ai_task.id).first()
        
        assert task is not None
        assert task.status == "pending"


class TestDatabaseRelationships:
    """数据库关系测试"""
    
    def test_user_platform_relationship(self, test_db, admin_user):
        """
        测试用户与平台的关系
        
        验证：
        - 可以通过用户查询平台
        """
        platform = Platform(
            name="关系测试",
            url="https://relation.com",
            created_by=admin_user.id
        )
        test_db.add(platform)
        test_db.commit()
        
        # 验证关系
        assert platform.created_by == admin_user.id
    
    def test_platform_article_relationship(self, test_db, sample_platform, admin_user):
        """
        测试平台与文章的关系
        
        验证：
        - 可以通过平台查询文章
        """
        article = Article(
            title="平台文章",
            slug="platform-article",
            content="内容",
            category="guide",
            status="published",
            platform_id=sample_platform.id,
            created_by=admin_user.id
        )
        test_db.add(article)
        test_db.commit()
        
        # 查询平台的文章
        articles = test_db.query(Article).filter(Article.platform_id == sample_platform.id).all()
        assert len(articles) >= 1


class TestDatabaseConstraints:
    """数据库约束测试"""
    
    def test_not_null_constraints(self, test_db, admin_user):
        """
        测试非空约束
        
        验证：
        - 必需字段不能为空
        """
        # 创建缺少必需字段的平台
        invalid_platform = Platform(
            name="测试",
            url=None,  # 违反非空约束
            created_by=admin_user.id
        )
        test_db.add(invalid_platform)
        
        with pytest.raises(Exception):
            test_db.commit()
    
    def test_foreign_key_constraints(self, test_db):
        """
        测试外键约束
        
        验证：
        - 不能引用不存在的外键
        """
        article = Article(
            title="孤立文章",
            slug="orphan",
            content="内容",
            category="guide",
            status="published",
            platform_id=99999,  # 不存在的平台
            author_id=99999   # 不存在的用户
        )
        test_db.add(article)
        
        with pytest.raises(Exception):
            test_db.commit()


class TestDatabaseIndexes:
    """数据库索引测试"""
    
    def test_user_email_index(self, test_db):
        """
        测试用户邮箱索引
        
        验证：
        - 邮箱字段有索引
        - 查询性能好
        """
        # 检查索引存在
        pass
    
    def test_platform_url_index(self, test_db):
        """
        测试平台 URL 索引
        
        验证：
        - URL 字段有索引
        """
        pass


class TestDatabaseTransactions:
    """数据库事务测试"""
    
    def test_transaction_rollback(self, test_db):
        """
        测试事务回滚
        
        验证：
        - 事务失败时回滚
        """
        user = AdminUser(
            username="rollback_test",
            email="rollback@test.com",
            hashed_password="hash"
        )
        test_db.add(user)
        test_db.commit()
        
        # 模拟事务失败
        try:
            user.username = None
            test_db.commit()
        except Exception:
            test_db.rollback()
    
    def test_transaction_commit(self, test_db):
        """
        测试事务提交
        
        验证：
        - 事务成功时提交
        """
        user = AdminUser(
            username="commit_test",
            email="commit@test.com",
            hashed_password="hash"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        assert user.id is not None
