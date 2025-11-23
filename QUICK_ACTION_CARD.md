# 🎯 后续工作行动计划卡

**格式**: 快速参考 | **打印版**: 可以打印贴在办公室 | **更新**: 2025-11-23

---

## 📍 当前位置
- **分支**: `refactor/admin-panel-phase4`
- **状态**: Phase 4 完成 ✅ | 5个Bug验收通过 ✅
- **下一步**: Phase 5 系统稳定性加固

---

## 🚀 每天开始工作 (3步)

```bash
# 1️⃣  系统检查 (2分钟)
bash daily_check.sh

# 2️⃣  启动后端 (30秒)
bash start-backend-simple.sh

# 3️⃣  打开浏览器
open http://localhost:8001/admin/
# 登录: admin / admin123
```

✅ 如果都通过了，开始工作  
❌ 如果有问题，按提示修复

---

## ⚠️ 重要规则

### 修改代码前 ✅ DO
```bash
# 1. 创建备份
cp trustagency.db backups/backup_$(date +%Y%m%d_%H%M%S).db

# 2. 创建分支
git checkout -b feature/your-feature-name

# 3. 进行修改和测试
```

### 修改代码后 ✅ DO
```bash
# 1. 运行检查
bash daily_check.sh

# 2. 提交代码
git add .
git commit -m "feat: 描述你的改动"

# 3. 推送分支
git push origin feature/your-feature-name
```

### 不要做 ❌ DON'T
- ❌ 不要跳过检查直接改代码
- ❌ 不要一次性改太多文件
- ❌ 不要在 main 分支上直接修改
- ❌ 不要忽视警告信息
- ❌ 不要让没有备份的代码上线

---

## 📊 性能告警阈值

| 指标 | 绿色✅ | 黄色⚠️ | 红色❌ |
|------|--------|--------|--------|
| 内存占用 | <300MB | 300-500MB | >500MB |
| API响应 | <500ms | 500ms-1s | >1s |
| 数据库大小 | <100MB | 100-200MB | >200MB |
| 页面加载 | <3s | 3-5s | >5s |

**超过黄色/红色阈值**: 立即停止，运行诊断

---

## 🆘 应急处理

### 后端卡顿或无响应
```bash
# 强制重启
pkill -9 -f uvicorn
sleep 2
bash start-backend-simple.sh
```

### 数据库出错
```bash
# 立即备份破损版本
cp trustagency.db trustagency.db.broken_$(date +%s)

# 恢复最近的备份
cp backups/backup_*.db trustagency.db
# 或恢复基准版本
cp backups/baseline_*.db trustagency.db
```

### 前端功能失效
```bash
# 恢复HTML文件
git checkout backend/site/admin/index.html

# 硬刷新浏览器 (Mac)
Cmd+Shift+R

# 如果还是不行
rm -rf ~/.config/Google/Chrome/Default/Cache/*
# 重新打开浏览器
```

### 系统严重故障
```bash
# 1. 停止所有服务
pkill -9 -f "uvicorn\|python"

# 2. 检查最后一个正常的git提交
git log --oneline | head -5

# 3. 回退到上一个版本
git reset --hard HEAD~1

# 4. 恢复数据库
cp backups/baseline_*.db trustagency.db

# 5. 重新启动
bash start-backend-simple.sh
```

---

## 📝 快速命令

```bash
# 查看后端日志
tail -f /tmp/backend.log

# 查看数据库内容
sqlite3 trustagency.db ".mode column" "SELECT * FROM sections;"

# 检查备份
ls -lh backups/

# 查看git日志
git log --oneline -10

# 查看改动
git diff HEAD~1

# 查看当前分支
git branch

# 创建新分支
git checkout -b feature/xxx

# 切换分支
git checkout main

# 强制推送 (谨慎!)
git push origin feature/xxx -f
```

---

## 🗺️ Phase 5-8 总览

| Phase | 目标 | 周期 | 优先级 | 状态 |
|-------|------|------|--------|------|
| **5** | 系统稳定加固 | 2-3周 | ⭐⭐⭐ | ⏳ 待开始 |
| **6** | 功能完善优化 | 3-4周 | ⭐⭐ | ⏳ 待开始 |
| **7** | 生产环境部署 | 2周 | ⭐⭐ | ⏳ 待开始 |
| **8** | 测试质量保证 | 贯穿 | ⭐⭐⭐ | 🔄 进行中 |

**目标**: 12月22日前生产环境就绪 🎯

---

## 📚 重要文档位置

```
项目根目录/
├── NEXT_PHASE_ROADMAP.md      ← 完整规划 (详细)
├── PLANNING_SUMMARY.md         ← 执行总结 (概览)
├── DAILY_CHECKLIST.md          ← 检查清单 (参考)
├── daily_check.sh              ← 检查脚本 (执行)
├── START_HERE.md               ← 快速开始
├── OPTIMIZATION_PLAN.md        ← 优化方案
└── PHASE4_FINAL_SUMMARY.md     ← Phase 4总结
```

**快速阅读**:
```bash
# 1. 了解总体规划 (3分钟)
cat PLANNING_SUMMARY.md

# 2. 理解详细任务 (15分钟)
less NEXT_PHASE_ROADMAP.md

# 3. 学习日常流程 (5分钟)
cat DAILY_CHECKLIST.md

# 4. 每天执行检查 (2分钟)
bash daily_check.sh
```

---

## 💡 关键要点

1. **稳定性第一** - 宁慢毋快，宁缓毋急
2. **备份救你** - 备份就像保险，关键时刻救命
3. **小步快速** - 避免一次性大改动
4. **测试覆盖** - 改代码就要测试
5. **及早告警** - 监控让问题无所遁形

---

## 📞 一句话指南

> 每天早上 `bash daily_check.sh`，有问题立即备份恢复，大改动前建分支，小步快速测试推送。

---

## ✨ 成功标志

**Phase 5 成功** ✅
- [ ] 系统连续运行72小时无卡顿
- [ ] 所有API响应 < 500ms
- [ ] 内存占用 < 300MB
- [ ] 前端加载 < 3s
- [ ] 监控系统正常运作
- [ ] 自动备份正常运行

**Phase 6 成功** ✅
- [ ] AI任务系统完全可用
- [ ] 文章编辑流程完整
- [ ] 用户权限管理就位

**Phase 7 成功** ✅
- [ ] Docker镜像构建通过
- [ ] Nginx配置完成
- [ ] 生产环境测试通过

**Phase 8 成功** ✅
- [ ] 测试覆盖率 > 80% (后端) / 70% (前端)
- [ ] 性能基准测试通过
- [ ] E2E验收测试100%通过

**最终成功** 🎉
- [ ] 12月22日前生产部署完成
- [ ] 系统稳定性达到企业级标准
- [ ] 完善的运维监控体系
- [ ] 清晰的故障恢复流程

---

**祝你工作愉快！** 🚀

*最后更新: 2025-11-23 | 维护者: GitHub Copilot*

