# 🌐 部署到 GitHub Pages 教程

## 第一步：注册 GitHub 账号

1. 访问 https://github.com
2. 点击 Sign up 注册
3. 填写用户名、邮箱、密码

## 第二步：创建仓库

1. 登录后，点击右上角 "+" → "New repository"
2. 仓库名称：`douyin-hot`
3. 设为 Public（公开）
4. 点击 "Create repository"

## 第三步：上传 HTML 文件

**方式A：网页上传（简单）**
1. 进入仓库页面
2. 点击 "Add file" → "Upload files"
3. 拖拽 `douyin_hot_20260324_195253.html` 到上传区域
4. 在 "Commit changes" 框里输入提交信息
5. 点击 "Commit changes"

**方式B：Git命令（推荐长期使用）**
```bash
git init
git add douyin_hot_20260324_195253.html
git commit -m "上传抖音热点HTML"
git remote add origin https://github.com/你的用户名/douyin-hot.git
git push -u origin main
```

## 第四步：启用 GitHub Pages

1. 进入仓库页面
2. 点击 "Settings"
3. 左侧菜单找到 "Pages"
4. "Source" 选择 "Deploy from a branch"
5. 分支选择 `main`（或 `main`）
6. 点击 "Save"

等待1-2分钟，GitHub 会生成访问地址：

```
https://你的用户名.github.io/douyin-hot/
```

## 第五步：访问网页

在手机浏览器打开上面的链接，就能看到抖音热点页面！

---

## 🤖️ 每天更新

方法1：手动更新
1. 运行 `generate_douyin_html.py` 生成新的HTML
2. 上传到 GitHub（覆盖旧文件）
3. GitHub Pages 自动更新

方法2：自动更新（高级）
需要配置 GitHub Actions 自动部署，我可以帮你设置。

---

## 💡 示例地址

假设你的用户名是 `haohao`，最终访问地址是：

```
https://haohao.github.io/douyin-hot/douyin_hot_20260324_195253.html
```

手机浏览器输入这个地址，就能直接点热点跳转抖音了！🎉

---

需要我帮你设置自动化部署吗？
