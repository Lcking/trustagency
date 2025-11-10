# 📊 后端开发任务执行清单 - 立即行动版

**当前状态**: 前端验收完成 ✅ → 后端开发启动 🚀  
**创建日期**: 2025-11-06  
**目标**: 清晰的任务分工和优先级

---

## 🎯 核心决策

### 选择技术栈

**我的推荐**: Node.js + Express + MySQL

| 方案 | 优点 | 缺点 | 学习曲线 |
|------|------|------|---------|
| **Node.js + Express** (推荐) | 快速开发，生态好，前后端统一 | 需要学习异步编程 | 中等 |
| Python + FastAPI | 代码简洁，AI 友好 | 需要额外学习 | 中等 |
| Django | 功能完整，文档全 | 学习时间长 | 陡峭 |

**决策**: 采用 Node.js + Express + MySQL

---

## 📋 优先级任务清单（按顺序）

### ✅ Week 1: 基础设置（第 1 周）

#### Task 1-1: 后端项目初始化 ⏱️ 4-6 小时

**目标**: 搭建基本的 Node.js 项目框架

**具体步骤**:
```bash
# 1. 创建后端项目目录
mkdir trustagency-backend
cd trustagency-backend

# 2. 初始化 npm 项目
npm init -y

# 3. 安装基础依赖
npm install express dotenv cors helmet morgan
npm install --save-dev nodemon

# 4. 创建项目结构
mkdir -p src/{controllers,routes,models,middleware,utils}
```

**完成标准**:
- [ ] 项目目录结构创建完成
- [ ] package.json 配置正确
- [ ] 基础依赖安装成功
- [ ] 可以启动 Hello World 服务器

**验证命令**:
```bash
npm start
# 输出: Server running on port 3000
```

---

#### Task 1-2: 数据库设计和初始化 ⏱️ 6-8 小时

**目标**: 设计并创建数据库 schema

**数据表**:

```sql
-- 1. 平台表
CREATE TABLE platforms (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  logo_url VARCHAR(255),
  website_url VARCHAR(255),
  min_leverage INT DEFAULT 1,
  max_leverage INT DEFAULT 100,
  commission_rate DECIMAL(5,4),
  risk_level ENUM('low','medium','high') DEFAULT 'medium',
  rating DECIMAL(3,2) DEFAULT 3.0,
  established_year INT,
  regulated BOOLEAN DEFAULT FALSE,
  reviews_count INT DEFAULT 0,
  published BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_slug (slug),
  KEY idx_rating (rating)
);

-- 2. 用户表
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  avatar_url VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_email (email)
);

-- 3. 评论表
CREATE TABLE reviews (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  platform_id INT NOT NULL,
  title VARCHAR(200),
  content TEXT,
  rating INT DEFAULT 5,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (platform_id) REFERENCES platforms(id) ON DELETE CASCADE,
  KEY idx_platform (platform_id),
  KEY idx_user (user_id)
);

-- 4. 文章表
CREATE TABLE articles (
  id INT PRIMARY KEY AUTO_INCREMENT,
  slug VARCHAR(200) UNIQUE NOT NULL,
  title VARCHAR(200) NOT NULL,
  content LONGTEXT,
  category VARCHAR(50),
  published BOOLEAN DEFAULT FALSE,
  view_count INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_slug (slug),
  KEY idx_category (category)
);

-- 插入测试数据
INSERT INTO platforms (name, slug, description, min_leverage, max_leverage, commission_rate, rating, established_year, regulated)
VALUES 
('Alpha Leverage', 'alpha-leverage', '高杠杆、低费率的专业交易平台', 1, 100, 0.001, 4.8, 2018, TRUE),
('Beta Margin', 'beta-margin', '风险管理工具完善的保证金交易平台', 1, 50, 0.0015, 4.5, 2016, TRUE),
('Gamma Trader', 'gamma-trader', '新手友好、教育资源丰富的平台', 1, 30, 0.002, 4.2, 2020, FALSE);
```

**完成标准**:
- [ ] MySQL 数据库创建成功
- [ ] 所有表已创建
- [ ] 测试数据已插入
- [ ] 数据库连接测试通过

**验证**: 
```bash
mysql -u root -p trustagency
SHOW TABLES;
SELECT * FROM platforms;
```

---

#### Task 1-3: 基础 API 框架 ⏱️ 6-8 小时

**目标**: 实现基础的 Express 应用框架和 API 路由

**需要创建的文件**:

```javascript
// src/app.js
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

const app = express();

// 中间件
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());

// 路由
app.use('/api/platforms', require('./routes/platforms'));
app.use('/api/auth', require('./routes/auth'));
app.use('/api/articles', require('./routes/articles'));

// 健康检查
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// 错误处理
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({
    code: 500,
    message: err.message || 'Internal Server Error'
  });
});

module.exports = app;
```

```javascript
// src/server.js
require('dotenv').config();
const app = require('./app');

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

```javascript
// src/utils/database.js
const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'trustagency',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

module.exports = pool;
```

**完成标准**:
- [ ] app.js 创建完成
- [ ] server.js 创建完成
- [ ] 数据库连接池配置成功
- [ ] 服务器可启动并能访问 /health

---

### ✅ Week 1 后半: 用户认证（第 1 周后半）

#### Task 1-4: 用户认证系统 ⏱️ 8-10 小时

**目标**: 实现用户注册、登录、JWT 认证

**需要创建的文件**:

```javascript
// src/routes/auth.js
const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

router.post('/register', authController.register);
router.post('/login', authController.login);
router.post('/logout', authController.logout);

module.exports = router;
```

```javascript
// src/controllers/authController.js
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const db = require('../utils/database');

class AuthController {
  async register(req, res) {
    try {
      const { username, email, password } = req.body;

      // 验证
      if (!username || !email || !password) {
        return res.status(400).json({
          code: 400,
          message: 'Missing required fields'
        });
      }

      // 加密密码
      const password_hash = await bcrypt.hash(password, 10);

      // 插入数据库
      const [result] = await db.query(
        'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
        [username, email, password_hash]
      );

      res.status(201).json({
        code: 201,
        message: 'User created successfully',
        data: {
          id: result.insertId,
          username,
          email
        }
      });
    } catch (error) {
      if (error.code === 'ER_DUP_ENTRY') {
        return res.status(400).json({
          code: 400,
          message: 'Username or email already exists'
        });
      }
      res.status(500).json({
        code: 500,
        message: error.message
      });
    }
  }

  async login(req, res) {
    try {
      const { email, password } = req.body;

      if (!email || !password) {
        return res.status(400).json({
          code: 400,
          message: 'Email and password required'
        });
      }

      // 查询用户
      const [users] = await db.query(
        'SELECT * FROM users WHERE email = ?',
        [email]
      );

      if (users.length === 0) {
        return res.status(401).json({
          code: 401,
          message: 'Invalid credentials'
        });
      }

      const user = users[0];

      // 验证密码
      const passwordMatch = await bcrypt.compare(password, user.password_hash);
      if (!passwordMatch) {
        return res.status(401).json({
          code: 401,
          message: 'Invalid credentials'
        });
      }

      // 生成 JWT token
      const token = jwt.sign(
        { id: user.id, email: user.email },
        process.env.JWT_SECRET || 'your-secret-key',
        { expiresIn: '7d' }
      );

      res.json({
        code: 200,
        message: 'Login successful',
        data: {
          token,
          user: {
            id: user.id,
            username: user.username,
            email: user.email,
            avatar_url: user.avatar_url
          }
        }
      });
    } catch (error) {
      res.status(500).json({
        code: 500,
        message: error.message
      });
    }
  }
}

module.exports = new AuthController();
```

```javascript
// src/middleware/auth.js
const jwt = require('jsonwebtoken');

function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      code: 401,
      message: 'No authorization header'
    });
  }

  const token = authHeader.slice(7);

  try {
    const decoded = jwt.verify(
      token,
      process.env.JWT_SECRET || 'your-secret-key'
    );
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({
      code: 401,
      message: 'Invalid token'
    });
  }
}

module.exports = authMiddleware;
```

**完成标准**:
- [ ] 注册端点可用
- [ ] 登录端点可用
- [ ] JWT token 正确生成
- [ ] 认证中间件工作正常

**测试命令**:
```bash
# 注册
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"123456"}'

# 登录
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456"}'
```

---

### ✅ Week 2: 核心 API（第 2 周）

#### Task 2-1: 平台 API ⏱️ 10-12 小时

**目标**: 实现平台列表、详情、搜索、排序、筛选

```javascript
// src/routes/platforms.js
const express = require('express');
const router = express.Router();
const platformController = require('../controllers/platformController');
const authMiddleware = require('../middleware/auth');

router.get('/', platformController.getPlatforms);
router.get('/:slug', platformController.getPlatform);
router.get('/:id/reviews', platformController.getReviews);
router.post('/:id/reviews', authMiddleware, platformController.submitReview);

// 管理员路由
router.post('/', authMiddleware, platformController.createPlatform);
router.put('/:id', authMiddleware, platformController.updatePlatform);
router.delete('/:id', authMiddleware, platformController.deletePlatform);

module.exports = router;
```

```javascript
// src/controllers/platformController.js
const db = require('../utils/database');

class PlatformController {
  async getPlatforms(req, res) {
    try {
      const limit = Math.min(parseInt(req.query.limit) || 10, 100);
      const offset = (parseInt(req.query.page) || 1 - 1) * limit;
      const sort = req.query.sort || '-rating';
      const risk = req.query.risk;

      let query = 'SELECT * FROM platforms WHERE published = TRUE';
      let countQuery = 'SELECT COUNT(*) as total FROM platforms WHERE published = TRUE';
      const params = [];

      // 风险筛选
      if (risk) {
        query += ' AND risk_level = ?';
        countQuery += ' AND risk_level = ?';
        params.push(risk);
      }

      // 排序
      const sortField = sort.replace('-', '');
      const sortOrder = sort.startsWith('-') ? 'DESC' : 'ASC';
      query += ` ORDER BY ${sortField} ${sortOrder}`;

      // 分页
      query += ' LIMIT ? OFFSET ?';

      const [platforms] = await db.query(query, [...params, limit, offset]);
      const [countResult] = await db.query(countQuery, params);

      res.json({
        code: 200,
        data: platforms,
        pagination: {
          total: countResult[0].total,
          page: Math.floor(offset / limit) + 1,
          limit,
          pages: Math.ceil(countResult[0].total / limit)
        }
      });
    } catch (error) {
      res.status(500).json({
        code: 500,
        message: error.message
      });
    }
  }

  async getPlatform(req, res) {
    try {
      const { slug } = req.params;
      const [platforms] = await db.query(
        'SELECT * FROM platforms WHERE slug = ? AND published = TRUE',
        [slug]
      );

      if (platforms.length === 0) {
        return res.status(404).json({
          code: 404,
          message: 'Platform not found'
        });
      }

      res.json({
        code: 200,
        data: platforms[0]
      });
    } catch (error) {
      res.status(500).json({
        code: 500,
        message: error.message
      });
    }
  }

  async getReviews(req, res) {
    try {
      const { id } = req.params;
      const limit = Math.min(parseInt(req.query.limit) || 10, 100);
      const page = parseInt(req.query.page) || 1;
      const offset = (page - 1) * limit;

      const [reviews] = await db.query(
        `SELECT r.*, u.username FROM reviews r
         JOIN users u ON r.user_id = u.id
         WHERE r.platform_id = ?
         ORDER BY r.created_at DESC
         LIMIT ? OFFSET ?`,
        [id, limit, offset]
      );

      res.json({
        code: 200,
        data: reviews
      });
    } catch (error) {
      res.status(500).json({
        code: 500,
        message: error.message
      });
    }
  }

  async submitReview(req, res) {
    try {
      const { id } = req.params;
      const { title, content, rating } = req.body;
      const userId = req.user.id;

      if (rating < 1 || rating > 5) {
        return res.status(400).json({
          code: 400,
          message: 'Rating must be between 1 and 5'
        });
      }

      const [result] = await db.query(
        `INSERT INTO reviews (user_id, platform_id, title, content, rating)
         VALUES (?, ?, ?, ?, ?)`,
        [userId, id, title, content, rating]
      );

      res.status(201).json({
        code: 201,
        message: 'Review submitted successfully',
        data: {
          id: result.insertId
        }
      });
    } catch (error) {
      res.status(500).json({
        code: 500,
        message: error.message
      });
    }
  }
}

module.exports = new PlatformController();
```

**完成标准**:
- [ ] GET /api/platforms 可用
- [ ] 分页功能正常
- [ ] 排序功能正常
- [ ] 筛选功能正常
- [ ] GET /api/platforms/:slug 可用
- [ ] 评论相关端点可用

---

#### Task 2-2: 对比功能 ⏱️ 8-10 小时

**目标**: 实现平台对比 API

```javascript
// 在 src/routes/platforms.js 中添加
router.post('/compare', platformController.comparePlatforms);
```

```javascript
// src/controllers/platformController.js 中添加
async comparePlatforms(req, res) {
  try {
    const { platform_ids } = req.body;

    if (!platform_ids || !Array.isArray(platform_ids) || platform_ids.length === 0) {
      return res.status(400).json({
        code: 400,
        message: 'platform_ids must be a non-empty array'
      });
    }

    const placeholders = platform_ids.map(() => '?').join(',');
    const [platforms] = await db.query(
      `SELECT * FROM platforms WHERE id IN (${placeholders}) AND published = TRUE`,
      platform_ids
    );

    res.json({
      code: 200,
      data: {
        comparison_fields: [
          'min_leverage',
          'max_leverage',
          'commission_rate',
          'rating',
          'established_year',
          'regulated'
        ],
        platforms: platforms.map(p => ({
          id: p.id,
          name: p.name,
          slug: p.slug,
          values: {
            min_leverage: p.min_leverage,
            max_leverage: p.max_leverage,
            commission_rate: p.commission_rate,
            rating: p.rating,
            established_year: p.established_year,
            regulated: p.regulated
          }
        }))
      }
    });
  } catch (error) {
    res.status(500).json({
      code: 500,
      message: error.message
    });
  }
}
```

---

#### Task 2-3: 文章/知识库 API ⏱️ 8-10 小时

**目标**: 实现 Wiki 和 FAQ API

```javascript
// src/routes/articles.js
const express = require('express');
const router = express.Router();
const articleController = require('../controllers/articleController');

router.get('/', articleController.getArticles);
router.get('/:slug', articleController.getArticle);

module.exports = router;
```

```javascript
// src/controllers/articleController.js
const db = require('../utils/database');

class ArticleController {
  async getArticles(req, res) {
    try {
      const category = req.query.category;
      const limit = Math.min(parseInt(req.query.limit) || 10, 100);
      const page = parseInt(req.query.page) || 1;
      const offset = (page - 1) * limit;

      let query = 'SELECT * FROM articles WHERE published = TRUE';
      const params = [];

      if (category) {
        query += ' AND category = ?';
        params.push(category);
      }

      query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?';

      const [articles] = await db.query(query, [...params, limit, offset]);

      res.json({
        code: 200,
        data: articles
      });
    } catch (error) {
      res.status(500).json({
        code: 500,
        message: error.message
      });
    }
  }

  async getArticle(req, res) {
    try {
      const { slug } = req.params;
      const [articles] = await db.query(
        'SELECT * FROM articles WHERE slug = ? AND published = TRUE',
        [slug]
      );

      if (articles.length === 0) {
        return res.status(404).json({
          code: 404,
          message: 'Article not found'
        });
      }

      const article = articles[0];

      // 增加浏览次数
      await db.query(
        'UPDATE articles SET view_count = view_count + 1 WHERE id = ?',
        [article.id]
      );

      res.json({
        code: 200,
        data: article
      });
    } catch (error) {
      res.status(500).json({
        code: 500,
        message: error.message
      });
    }
  }
}

module.exports = new ArticleController();
```

**完成标准**:
- [ ] GET /api/articles 可用
- [ ] 分类筛选正常
- [ ] GET /api/articles/:slug 可用
- [ ] 浏览次数正确统计

---

### 📋 环境文件配置

```bash
# .env
NODE_ENV=development
PORT=3000

# 数据库
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=trustagency

# JWT
JWT_SECRET=your-secret-key-change-in-production

# API
API_BASE_URL=http://localhost:3000
```

---

## ✅ 验收检查清单

### API 端点验收
- [ ] 注册端点正常
- [ ] 登录端点正常
- [ ] 平台列表端点正常
- [ ] 平台详情端点正常
- [ ] 评论提交端点正常
- [ ] 对比功能端点正常
- [ ] 文章端点正常

### 数据库验收
- [ ] 所有表已创建
- [ ] 测试数据已插入
- [ ] 数据完整性检查通过
- [ ] 索引创建成功

### 功能验收
- [ ] 排序功能正常
- [ ] 筛选功能正常
- [ ] 分页功能正常
- [ ] 认证功能正常

### 安全验收
- [ ] 密码加密存储
- [ ] JWT token 正确验证
- [ ] 输入验证完善
- [ ] CORS 配置正确

---

## 🚀 快速启动指令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 运行测试
npm test

# 构建生产版本
npm run build

# 启动生产服务器
npm start
```

---

**立即开始第一个任务！** 💪

选择 Task 1-1 （项目初始化），用 4-6 小时完成，然后逐步推进！
