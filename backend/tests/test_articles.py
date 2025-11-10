"""
Task 5 - 文章管理 API 的单元测试
测试所有文章 API 端点的功能、错误处理和边界情况
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.main import app
from app.database import get_db
from app.models import AdminUser, Platform, Article
from app.services.auth_service import AuthService
from app.services.platform_service import PlatformService
from app.schemas.admin import AdminCreate
from app.schemas.platform import PlatformCreate
from app.schemas.article import ArticleCreate
from app.utils.security import create_access_token


# ==================== Fixtures ====================

@pytest.fixture
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def admin_user(db_session):
    """创建测试管理员用户"""
    admin_data = AdminCreate(
        username="admin_article",
        email="admin_article@test.com",
        password="test_password_123",
        full_name="Test Admin"
    )
    admin = AuthService.create_admin_user(db_session, admin_data)
    return admin


@pytest.fixture
def admin_token(admin_user):
    """创建管理员 JWT token"""
    return create_access_token({"sub": admin_user.username})


@pytest.fixture
def platform(db_session):
    """创建测试平台"""
    platform_data = PlatformCreate(
        name="Test Platform",
        description="Test Platform for Articles",
        rating=4.5,
        rank=1,
    )
    db_platform = Platform(**platform_data.model_dump())
    db_session.add(db_platform)
    db_session.commit()
    db_session.refresh(db_platform)
    return db_platform


@pytest.fixture
def sample_article(db_session, admin_user, platform):
    """创建示例文章"""
    article = Article(
        title="Sample Article",
        slug="sample-article",
        content="This is a sample article content",
        summary="Sample summary",
        category="教程",
        tags="test,sample",
        author_id=admin_user.id,
        platform_id=platform.id,
        is_published=True,
        published_at=datetime.utcnow(),
        view_count=100,
        like_count=50,
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)
    return article


@pytest.fixture
def sample_articles(db_session, admin_user, platform):
    """创建多个示例文章"""
    articles_data = [
        {
            "title": "Bitcoin 初学者指南",
            "slug": "bitcoin-beginners-guide",
            "content": "Bitcoin introduction content...",
            "summary": "Learn about Bitcoin",
            "category": "教程",
            "tags": "bitcoin,cryptocurrency,beginner",
            "author_id": admin_user.id,
            "platform_id": platform.id,
            "is_published": True,
            "published_at": datetime.utcnow(),
            "like_count": 150,
        },
        {
            "title": "Ethereum 智能合约开发",
            "slug": "ethereum-smart-contracts",
            "content": "Smart contract development guide...",
            "summary": "Guide to Ethereum smart contracts",
            "category": "开发",
            "tags": "ethereum,smart-contract,development",
            "author_id": admin_user.id,
            "platform_id": platform.id,
            "is_published": True,
            "published_at": datetime.utcnow() - timedelta(days=1),
            "like_count": 200,
        },
        {
            "title": "交易策略分析",
            "slug": "trading-strategy-analysis",
            "content": "Trading strategy content...",
            "summary": "Analyze trading strategies",
            "category": "交易",
            "tags": "trading,strategy,analysis",
            "author_id": admin_user.id,
            "platform_id": platform.id,
            "is_published": False,  # 未发布
            "like_count": 50,
        },
        {
            "title": "精选：行业动态",
            "slug": "featured-industry-news",
            "content": "Industry news and updates...",
            "summary": "Latest industry updates",
            "category": "新闻",
            "tags": "news,industry,update",
            "author_id": admin_user.id,
            "platform_id": platform.id,
            "is_published": True,
            "published_at": datetime.utcnow() - timedelta(hours=2),
            "is_featured": True,
            "like_count": 300,
        },
    ]
    
    articles = []
    for data in articles_data:
        article = Article(**data)
        db_session.add(article)
        articles.append(article)
    
    db_session.commit()
    for a in articles:
        db_session.refresh(a)
    
    return articles


# ==================== 测试: 获取文章列表 ====================

class TestGetArticles:
    """获取文章列表的测试类"""
    
    def test_list_articles_empty(self, client):
        """测试获取空文章列表"""
        response = client.get("/api/articles")
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["total"] == 0
    
    def test_list_articles_with_data(self, client, sample_articles):
        """测试获取有数据的文章列表"""
        response = client.get("/api/articles")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
    
    def test_list_articles_pagination(self, client, sample_articles):
        """测试分页功能"""
        response = client.get("/api/articles?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 4
    
    def test_list_articles_search_by_title(self, client, sample_articles):
        """测试按标题搜索"""
        response = client.get("/api/articles?search=bitcoin")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1
        assert any("Bitcoin" in a["title"] for a in data["data"])
    
    def test_list_articles_filter_by_category(self, client, sample_articles):
        """测试按分类过滤"""
        response = client.get("/api/articles?category=开发")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1
        assert all(a["category"] == "开发" for a in data["data"])
    
    def test_list_articles_filter_published(self, client, sample_articles):
        """测试过滤已发布文章"""
        response = client.get("/api/articles?is_published=true")
        assert response.status_code == 200
        data = response.json()
        assert all(a["is_published"] for a in data["data"])
    
    def test_list_articles_filter_featured(self, client, sample_articles):
        """测试过滤精选文章"""
        response = client.get("/api/articles?is_featured=true")
        assert response.status_code == 200
        data = response.json()
        assert all(a["is_featured"] for a in data["data"])
    
    def test_list_articles_sort_by_likes(self, client, sample_articles):
        """测试按点赞数排序"""
        response = client.get("/api/articles?sort_by=like_count&sort_order=desc&is_published=true")
        assert response.status_code == 200
        data = response.json()
        if len(data["data"]) > 1:
            assert data["data"][0]["like_count"] >= data["data"][1]["like_count"]
    
    def test_list_articles_sort_by_date_asc(self, client, sample_articles):
        """测试按日期升序排序"""
        response = client.get("/api/articles?sort_by=created_at&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) > 0


# ==================== 测试: 创建文章 ====================

class TestCreateArticle:
    """创建文章的测试类"""
    
    def test_create_article_success(self, client, admin_user, admin_token, platform):
        """测试成功创建文章"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "title": "New Article",
            "content": "Article content here",
            "summary": "Article summary",
            "category": "教程",
            "tags": "tag1,tag2",
        }
        response = client.post(f"/api/articles?platform_id={platform.id}", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Article"
        assert data["slug"] is not None
        assert data["author_id"] == admin_user.id
        assert data["platform_id"] == platform.id
    
    def test_create_article_auto_slug_generation(self, client, admin_user, admin_token, platform):
        """测试自动生成 slug"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "title": "Article With Special Characters!@#",
            "content": "Content",
        }
        response = client.post(f"/api/articles?platform_id={platform.id}", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert "article-with-special-characters" in data["slug"].lower()
    
    def test_create_article_without_auth(self, client, platform):
        """测试未授权创建文章"""
        payload = {"title": "Test", "content": "Test"}
        response = client.post(f"/api/articles?platform_id={platform.id}", json=payload)
        assert response.status_code == 403
    
    def test_create_article_invalid_platform(self, client, admin_user, admin_token):
        """测试创建文章关联无效平台"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {"title": "Test", "content": "Test"}
        response = client.post("/api/articles?platform_id=9999", json=payload, headers=headers)
        assert response.status_code == 400


# ==================== 测试: 获取单个文章 ====================

class TestGetSingleArticle:
    """获取单个文章的测试类"""
    
    def test_get_article_success(self, client, sample_article):
        """测试成功获取文章"""
        response = client.get(f"/api/articles/{sample_article.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_article.id
        assert data["title"] == sample_article.title
        # 验证浏览量增加
        assert data["view_count"] == sample_article.view_count + 1
    
    def test_get_article_not_found(self, client):
        """测试获取不存在的文章"""
        response = client.get("/api/articles/9999")
        assert response.status_code == 404


# ==================== 测试: 更新文章 ====================

class TestUpdateArticle:
    """更新文章的测试类"""
    
    def test_update_article_success(self, client, admin_user, admin_token, sample_article):
        """测试成功更新文章"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "title": "Updated Title",
            "summary": "Updated summary",
        }
        response = client.put(f"/api/articles/{sample_article.id}", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["summary"] == "Updated summary"
    
    def test_update_article_partial(self, client, admin_user, admin_token, sample_article):
        """测试部分字段更新"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {"is_featured": True}
        response = client.put(f"/api/articles/{sample_article.id}", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_featured"] == True
        assert data["title"] == sample_article.title  # 其他字段不变
    
    def test_update_article_title_updates_slug(self, client, admin_user, admin_token, sample_article):
        """测试更新标题会更新 slug"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {"title": "Completely New Title"}
        response = client.put(f"/api/articles/{sample_article.id}", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "completely-new-title" in data["slug"].lower()


# ==================== 测试: 删除文章 ====================

class TestDeleteArticle:
    """删除文章的测试类"""
    
    def test_delete_article_success(self, client, admin_user, admin_token, sample_article):
        """测试成功删除文章"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete(f"/api/articles/{sample_article.id}", headers=headers)
        assert response.status_code == 204
        
        # 验证文章已删除
        response = client.get(f"/api/articles/{sample_article.id}")
        assert response.status_code == 404


# ==================== 测试: 发布状态管理 ====================

class TestPublishArticle:
    """发布文章状态管理的测试类"""
    
    def test_publish_article(self, client, admin_user, admin_token, db_session, platform):
        """测试发布文章"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 创建未发布的文章
        article = Article(
            title="Unpublished",
            slug="unpublished",
            content="Content",
            author_id=admin_user.id,
            platform_id=platform.id,
            is_published=False,
        )
        db_session.add(article)
        db_session.commit()
        db_session.refresh(article)
        
        # 发布文章
        response = client.post(f"/api/articles/{article.id}/publish", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_published"] == True
        assert data["published_at"] is not None
    
    def test_unpublish_article(self, client, admin_user, admin_token, sample_article):
        """测试取消发布文章"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(f"/api/articles/{sample_article.id}/unpublish", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_published"] == False


# ==================== 测试: 点赞功能 ====================

class TestLikeArticle:
    """点赞功能的测试类"""
    
    def test_like_article(self, client, sample_article):
        """测试点赞文章"""
        original_likes = sample_article.like_count
        response = client.post(f"/api/articles/{sample_article.id}/like")
        assert response.status_code == 200
        data = response.json()
        assert data["like_count"] == original_likes + 1


# ==================== 测试: 特殊查询 ====================

class TestSpecialArticleQueries:
    """特殊查询的测试类"""
    
    def test_search_articles(self, client, sample_articles):
        """测试搜索文章"""
        response = client.get("/api/articles/search/by-keyword?keyword=bitcoin")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_get_featured_articles(self, client, sample_articles):
        """测试获取精选文章"""
        response = client.get("/api/articles/featured/list")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(a["is_featured"] for a in data)
    
    def test_get_trending_articles(self, client, sample_articles):
        """测试获取热门文章"""
        response = client.get("/api/articles/trending/list")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
    
    def test_get_articles_by_category(self, client, sample_articles):
        """测试按分类获取文章"""
        response = client.get("/api/articles/by-category/教程")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_get_articles_by_platform(self, client, sample_articles, platform):
        """测试按平台获取文章"""
        response = client.get(f"/api/articles/by-platform/{platform.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0


# ==================== 集成测试 ====================

class TestArticleIntegration:
    """文章 API 集成测试"""
    
    def test_full_article_lifecycle(self, client, admin_user, admin_token, platform):
        """测试完整的文章生命周期：创建 → 读取 → 发布 → 点赞 → 删除"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. 创建文章（未发布）
        create_payload = {
            "title": "Lifecycle Article",
            "content": "Article content",
            "category": "教程",
        }
        response = client.post(f"/api/articles?platform_id={platform.id}", json=create_payload, headers=headers)
        assert response.status_code == 201
        article_id = response.json()["id"]
        
        # 2. 获取文章
        response = client.get(f"/api/articles/{article_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Lifecycle Article"
        
        # 3. 发布文章
        response = client.post(f"/api/articles/{article_id}/publish", headers=headers)
        assert response.status_code == 200
        assert response.json()["is_published"] == True
        
        # 4. 点赞文章
        response = client.post(f"/api/articles/{article_id}/like")
        assert response.status_code == 200
        assert response.json()["like_count"] == 1
        
        # 5. 更新文章
        update_payload = {"summary": "New summary"}
        response = client.put(f"/api/articles/{article_id}", json=update_payload, headers=headers)
        assert response.status_code == 200
        
        # 6. 删除文章
        response = client.delete(f"/api/articles/{article_id}", headers=headers)
        assert response.status_code == 204
        
        # 7. 验证删除
        response = client.get(f"/api/articles/{article_id}")
        assert response.status_code == 404


# ==================== 性能测试 ====================

class TestArticlePerformance:
    """性能测试类"""
    
    def test_list_large_dataset(self, client, db_session, admin_user, platform):
        """测试大数据集列表获取"""
        # 创建 1000 个文章
        for i in range(1000):
            article = Article(
                title=f"Article {i}",
                slug=f"article-{i}",
                content=f"Content {i}",
                category=f"Category {i % 10}",
                author_id=admin_user.id,
                platform_id=platform.id,
                is_published=True,
            )
            db_session.add(article)
        db_session.commit()
        
        # 获取列表
        response = client.get("/api/articles?limit=100")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 100
        assert data["total"] == 1000
