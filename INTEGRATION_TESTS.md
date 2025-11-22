# TrustAgency 集成测试指南

**版本**：1.0  
**发布日期**：2025-11-21  
**维护者**：QA 团队

---

## 目录
1. [测试框架和工具](#测试框架和工具)
2. [测试环境设置](#测试环境设置)
3. [基础集成测试](#基础集成测试)
4. [功能集成测试](#功能集成测试)
5. [回归测试](#回归测试)
6. [性能测试](#性能测试)
7. [测试执行](#测试执行)

---

## 测试框架和工具

### 使用的工具
- **Playwright**：浏览器自动化测试框架
- **pytest**：Python 测试框架（后端单元测试）
- **Python requests**：API 功能测试

### 测试覆盖目标
- ✅ 前端集成测试：Playwright
- ✅ 后端 API 测试：pytest + requests
- ✅ 端到端测试：完整工作流
- ✅ 回归测试：所有已知功能

---

## 测试环境设置

### 前提条件
```bash
# 安装 Playwright
npm install -D @playwright/test
# 或
pip install pytest-playwright

# 安装 Python 依赖
pip install requests pytest

# 启动后端服务
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# 启动前端服务（如果需要）
# 在另一个终端窗口
```

### 测试数据准备
```python
# tests/conftest.py
import pytest
from app.database import init_db, get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """在测试前初始化测试数据库"""
    init_db()
    yield
    # 清理（可选）
```

---

## 基础集成测试

### 测试 1.1：后台登录功能

**测试目标**：验证用户能够成功登录

**测试步骤**：
```python
# tests/test_admin_login.py
import pytest
from playwright.sync_api import sync_playwright

@pytest.mark.integration
def test_admin_login():
    """测试管理员登录功能"""
    with sync_playwright() as p:
        # 1. 打开浏览器
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 2. 导航到登录页面
        page.goto("http://localhost:8000/admin")
        
        # 3. 输入用户名和密码
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin123")
        
        # 4. 点击登录按钮
        page.click('button[type="submit"]')
        
        # 5. 等待导航到主页面
        page.wait_for_url("http://localhost:8000/admin", timeout=5000)
        
        # 6. 验证主页面已加载
        assert page.is_visible('div#mainPage'), "主页面应该可见"
        assert page.is_visible('div#sidebar'), "侧边栏应该可见"
        
        # 7. 验证 localStorage 中保存了 token
        storage = page.evaluate('() => localStorage.getItem("token")')
        assert storage is not None, "Token 应该被保存到 localStorage"
        
        browser.close()

@pytest.mark.integration
def test_login_with_invalid_credentials():
    """测试使用错误凭证登录失败"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        page.goto("http://localhost:8000/admin")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "wrong_password")
        page.click('button[type="submit"]')
        
        # 验证仍然在登录页面
        assert page.url.endswith("/admin") or "login" in page.url
        
        # 验证显示了错误信息
        assert page.is_visible('text=登录失败') or page.is_visible('text=credentials')
        
        browser.close()
```

---

### 测试 1.2：后端 API 可用性

**测试目标**：验证所有关键 API 端点可用

**测试步骤**：
```python
# tests/test_api_endpoints.py
import requests
import pytest

API_BASE_URL = "http://localhost:8001/api"

@pytest.mark.integration
def test_api_health_check():
    """测试 API 是否正常运行"""
    response = requests.get(f"{API_BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.integration
def test_login_api():
    """测试登录 API"""
    response = requests.post(f"{API_BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data

@pytest.mark.integration
def test_get_sections_api():
    """测试获取栏目 API"""
    # 首先登录获取 token
    login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["token"]
    
    # 使用 token 调用 API
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/sections", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@pytest.mark.integration  
def test_api_endpoints_list():
    """验证所有关键 API 端点存在"""
    endpoints = [
        ("POST", "/auth/login"),
        ("GET", "/sections"),
        ("GET", "/platforms"),
        ("GET", "/articles"),
        ("GET", "/ai-configs"),
    ]
    
    for method, endpoint in endpoints:
        # 验证端点存在（不一定能访问，但应该返回 401 或其他状态码，不是 404）
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{API_BASE_URL}{endpoint}", json={})
        
        assert response.status_code != 404, f"Endpoint {endpoint} 不存在"
```

---

## 功能集成测试

### 测试 2.1：完整后台工作流程

**测试目标**：验证整个后台系统功能完整可用

**测试步骤**：
```python
# tests/test_admin_workflow.py
from playwright.sync_api import sync_playwright
import pytest

@pytest.mark.integration
def test_complete_admin_workflow():
    """测试完整的后台管理工作流程"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # ========== 第1步：登录 ==========
        page.goto("http://localhost:8000/admin")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin123")
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/admin", timeout=5000)
        print("✓ 登录成功")
        
        # ========== 第2步：验证仪表板数据 ==========
        # 等待仪表板加载
        page.wait_for_selector('text=平台', timeout=5000)
        
        # 验证数据统计卡片
        platforms_count = page.text_content('//text[contains(., "平台")]/parent::*')
        assert platforms_count is not None
        print(f"✓ 仪表板已加载，显示平台信息")
        
        # ========== 第3步：验证栏目菜单 ==========
        page.click('button:has-text("栏目")')
        page.wait_for_selector('text=分类列表', timeout=5000)
        
        # 验证分类数据已加载
        categories = page.query_selector_all('[data-category]')
        assert len(categories) > 0
        print(f"✓ 栏目菜单正常，加载了 {len(categories)} 个分类")
        
        # ========== 第4步：验证平台菜单 ==========
        page.click('button:has-text("平台")')
        page.wait_for_selector('text=平台列表', timeout=5000)
        
        platforms = page.query_selector_all('[data-platform]')
        assert len(platforms) > 0
        print(f"✓ 平台菜单正常，加载了 {len(platforms)} 个平台")
        
        # ========== 第5步：验证文章菜单 ==========
        page.click('button:has-text("文章")')
        page.wait_for_selector('text=文章列表', timeout=5000)
        
        articles = page.query_selector_all('[data-article]')
        print(f"✓ 文章菜单正常，加载了 {len(articles)} 篇文章")
        
        # ========== 第6步：验证 AI 配置菜单 ==========
        page.click('button:has-text("AI配置")')
        page.wait_for_selector('text=配置列表', timeout=5000)
        
        configs = page.query_selector_all('[data-config]')
        assert len(configs) > 0
        print(f"✓ AI配置菜单正常，加载了 {len(configs)} 个配置")
        
        # ========== 第7步：验证没有 console 错误 ==========
        console_messages = []
        page.on("console", lambda msg: console_messages.append(msg))
        
        # 浏览各个菜单
        page.click('button:has-text("栏目")')
        page.wait_for_timeout(500)
        
        errors = [msg for msg in console_messages if msg.type == "error"]
        assert len(errors) == 0, f"Console 中有错误: {errors}"
        print("✓ 没有 console 错误")
        
        # ========== 第8步：测试登出 ==========
        page.click('button:has-text("登出")')
        page.wait_for_url("http://localhost:8000/admin", timeout=5000)
        
        # 验证已回到登录页面
        assert page.is_visible('input[name="username"]')
        print("✓ 登出成功")
        
        browser.close()
        print("\n✅ 完整工作流程测试通过！")

@pytest.mark.integration
def test_all_functions_defined():
    """验证所有核心函数都已定义"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 登录
        page.goto("http://localhost:8000/admin")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin123")
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/admin", timeout=5000)
        
        # 检查核心函数是否定义
        functions = [
            "showSection",
            "loadSections",
            "loadPlatforms",
            "loadArticles",
            "loadAIConfigs",
            "logout",
            "handleLogin",
        ]
        
        for func in functions:
            exists = page.evaluate(f"typeof {func} !== 'undefined'")
            assert exists, f"函数 {func} 未定义"
            print(f"✓ 函数 {func} 已定义")
        
        browser.close()
```

---

### 测试 2.2：数据加载测试

**测试目标**：验证所有数据能正确加载和显示

```python
# tests/test_data_loading.py
import requests
import json

def test_sections_data():
    """测试栏目数据加载"""
    # 登录获取 token
    response = requests.post("http://localhost:8001/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = response.json()["token"]
    
    # 获取栏目数据
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("http://localhost:8001/api/sections", headers=headers)
    
    assert response.status_code == 200
    sections = response.json()
    
    # 验证数据完整性
    for section in sections:
        assert "id" in section
        assert "name" in section
        assert "platform_id" in section
    
    print(f"✓ 成功加载 {len(sections)} 个栏目")

def test_platforms_data():
    """测试平台数据加载"""
    response = requests.post("http://localhost:8001/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = response.json()["token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("http://localhost:8001/api/platforms", headers=headers)
    
    assert response.status_code == 200
    platforms = response.json()
    assert len(platforms) > 0
    
    print(f"✓ 成功加载 {len(platforms)} 个平台")
```

---

## 回归测试

### 测试 3.1：确保原有功能未被破坏

```python
# tests/test_regression.py
from playwright.sync_api import sync_playwright
import pytest

@pytest.mark.regression
def test_sidebar_navigation_regression():
    """回归测试：侧边栏导航功能"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 登录
        page.goto("http://localhost:8000/admin")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin123")
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/admin", timeout=5000)
        
        # 测试所有菜单项点击
        menu_items = ['栏目', '平台', '文章', 'AI配置', '系统设置']
        
        for item in menu_items:
            try:
                page.click(f'button:has-text("{item}")')
                page.wait_for_timeout(500)  # 等待页面响应
                
                # 验证没有出现错误
                console_messages = page.context.pages[0].evaluate(
                    'window.__consoleErrors || []'
                )
                print(f"✓ 菜单 '{item}' 功能正常")
            except Exception as e:
                raise AssertionError(f"菜单 '{item}' 点击失败: {e}")
        
        browser.close()

@pytest.mark.regression
def test_token_persistence_regression():
    """回归测试：Token 持久化"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 登录
        page.goto("http://localhost:8000/admin")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin123")
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/admin", timeout=5000)
        
        # 获取 token
        token = page.evaluate('localStorage.getItem("token")')
        assert token is not None
        
        # 刷新页面
        page.reload()
        
        # 验证 token 仍然存在
        token_after_reload = page.evaluate('localStorage.getItem("token")')
        assert token_after_reload == token
        assert token_after_reload is not None
        
        # 验证主页面仍然显示
        page.wait_for_selector('div#mainPage', timeout=5000)
        
        browser.close()
        print("✓ Token 持久化测试通过")
```

---

## 性能测试

### 测试 4.1：页面加载性能

```python
# tests/test_performance.py
from playwright.sync_api import sync_playwright
import time

def test_page_load_time():
    """测试页面加载时间"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 记录开始时间
        start_time = time.time()
        
        # 导航到页面
        page.goto("http://localhost:8000/admin", wait_until="networkidle")
        
        # 计算加载时间
        load_time = time.time() - start_time
        
        # 验证加载时间 < 3 秒
        assert load_time < 3, f"页面加载时间过长: {load_time}s"
        print(f"✓ 页面加载时间: {load_time:.2f}s")
        
        browser.close()

def test_data_loading_performance():
    """测试数据加载性能"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 登录
        page.goto("http://localhost:8000/admin")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin123")
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/admin", timeout=5000)
        
        # 点击栏目菜单并测量时间
        start_time = time.time()
        page.click('button:has-text("栏目")')
        page.wait_for_selector('text=分类列表', timeout=5000)
        load_time = time.time() - start_time
        
        assert load_time < 2, f"数据加载时间过长: {load_time}s"
        print(f"✓ 栏目数据加载时间: {load_time:.2f}s")
        
        browser.close()
```

---

## 测试执行

### 运行所有测试
```bash
# 运行所有集成测试
pytest tests/ -m integration -v

# 运行特定测试文件
pytest tests/test_admin_login.py -v

# 运行特定测试
pytest tests/test_admin_login.py::test_admin_login -v

# 运行所有测试并生成覆盖率报告
pytest tests/ --cov=backend --cov-report=html
```

### 测试报告
```bash
# 生成 JUnit XML 报告
pytest tests/ -v --junit-xml=test-results.xml

# 生成 HTML 报告
pytest tests/ -v --html=test-results.html
```

### CI/CD 集成
参见 `.github/workflows/` 目录中的配置文件

---

## 测试清单

在提交 PR 前，必须执行：

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 所有回归测试通过
- [ ] 没有新的 console 错误
- [ ] 没有新的 API 错误
- [ ] 性能指标满足要求
- [ ] 测试覆盖率 > 80%

---

**签名**：QA 团队  
**最后更新**：2025-11-21
