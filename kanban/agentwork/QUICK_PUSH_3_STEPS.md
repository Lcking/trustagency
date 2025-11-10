# 🚀 超级简化版：3 步推送到 GitHub

**时间**: 5 分钟  
**难度**: ⭐ 极简

---

## ⚡ 只需做这 3 件事

### ✅ 第 1 步：打开 GitHub 创建仓库（3 分钟）

1. 访问 https://github.com
2. 登录你的账户（没有就先注册）
3. 右上角点 **"+"** → 选 **"New repository"**
4. 填写：
   - **Repository name**: `trustagency`
   - **Description**: `Project with Docker and bug fixes` (可选)
   - **Public**: 选中
   - 其他都不勾选
5. 点 **"Create repository"** 按钮

👉 **记下屏幕上显示的这三行命令** (后面会用)

---

### ✅ 第 2 步：打开终端（1 分钟）

按 **Command + Space**，输入 `terminal`，回车打开终端

---

### ✅ 第 3 步：复制粘贴执行这 6 条命令（1 分钟）

```bash
cd /Users/ck/Desktop/Project/trustagency
git add -A
git commit -m "Initial commit: trustagency project"
git remote add origin https://github.com/YOUR_USERNAME/trustagency.git
git branch -M main
git push -u origin main
```

⚠️ **重要**: 把 `YOUR_USERNAME` 替换成你的 GitHub 用户名

**例如**: 如果你的用户名是 `john123`，那就是：
```bash
git remote add origin https://github.com/john123/trustagency.git
```

---

## 🎯 执行流程

```
1️⃣ 打开终端

2️⃣ 输入第一条命令：
cd /Users/ck/Desktop/Project/trustagency
回车 ↩️

3️⃣ 输入第二条命令：
git add -A
回车 ↩️

4️⃣ 输入第三条命令：
git commit -m "Initial commit: trustagency project"
回车 ↩️

5️⃣ 输入第四条命令（替换用户名）：
git remote add origin https://github.com/YOUR_USERNAME/trustagency.git
回车 ↩️

6️⃣ 输入第五条命令：
git branch -M main
回车 ↩️

7️⃣ 输入第六条命令：
git push -u origin main
回车 ↩️

8️⃣ 输入密码（粘贴 GitHub Personal Access Token）
回车 ↩️

✅ 完成！
```

---

## 🔐 密码怎么输入？

当看到这样的提示时：
```
Username for 'https://github.com': 
```

### 输入方式：

1. **用户名**: 输入你的 GitHub 用户名，回车
2. **密码**: 不要输入 GitHub 密码！

### 如果提示输入密码：

用这个方法（推荐）:

1. 打开 https://github.com/settings/tokens
2. 点 "Generate new token"  
3. 勾选 `repo`
4. 点 "Generate token"
5. 复制生成的 token
6. 粘贴到终端（Command + V）
7. 回车

✅ 推送完成！

---

## ✅ 怎么知道是否成功？

看终端的最后一行，应该显示：
```
To github.com:your-username/trustagency.git
 * [new branch]      main -> main
```

如果看到这个，恭喜！🎉 **推送成功了！**

---

## 🌐 验证：打开 GitHub 看看

打开 https://github.com/your-username/trustagency

你应该能看到你的所有文件！

---

## ❌ 如果出错了？

### 错误 1："No such file or directory"

❌ 说明目录不对

✅ 检查：
```bash
ls -la /Users/ck/Desktop/Project/trustagency
```

应该看到很多文件和文件夹。

---

### 错误 2："Permission denied"

❌ 说明认证失败

✅ 解决：
```bash
# 创建一个 token（见上面的"密码怎么输入"部分）
# 粘贴 token 而不是密码
```

---

### 错误 3："fatal: not a git repository"

❌ 说明项目没有初始化

✅ 解决：
```bash
git init
git config user.name "Your Name"
git config user.email "your.email@gmail.com"
```

然后重新执行上面的 6 条命令。

---

### 错误 4："fatal: remote origin already exists"

❌ 说明 remote 已经存在

✅ 解决：删除旧的 remote
```bash
git remote remove origin
# 然后重新执行 git remote add... 那一条
```

---

## 💡 额外技巧

### 之后如何更新？

```bash
# 每次修改代码后，重复这 3 个命令：
git add -A
git commit -m "Update: 你的修改说明"
git push origin main
```

### 如何从 GitHub 下载？

```bash
git clone https://github.com/your-username/trustagency.git
```

---

## 🎁 就这么简单！

只需要 5 分钟，你的项目就在 GitHub 云端了！

**现在就做吧！** 🚀

