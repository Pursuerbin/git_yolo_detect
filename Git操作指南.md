# Git操作指南

本文档详细说明如何使用Git连接、更新本地内容并上传到远程仓库，适用于绝缘子缺陷检测系统项目。

## 一、初始设置

### 1. 克隆远程仓库

如果尚未克隆仓库到本地，使用以下命令：

```bash
git clone https://github.com/Pursuerbin/git_yolo_detect.git
cd git_yolo_detect
```

### 2. 配置Git用户信息

确保设置了正确的Git用户信息：

```bash
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱"
```

## 二、日常工作流程

### 1. 拉取远程更新

在开始工作前，先拉取远程仓库的最新更新：

```bash
git pull origin main
```

### 2. 查看当前状态

查看工作区和暂存区的状态：

```bash
git status
```

### 3. 添加更改到暂存区

将修改的文件添加到暂存区：

```bash
# 添加指定文件
git add 文件名

# 添加所有更改
git add .
```

### 4. 提交更改

提交暂存区的更改：

```bash
git commit -m "提交信息"
```

提交信息应简明扼要，描述本次更改的内容。

### 5. 推送到远程仓库

将本地提交推送到远程仓库：

```bash
git push origin main
```

## 三、分支管理

### 1. 创建新分支

创建并切换到新分支：

```bash
git checkout -b 分支名
```

### 2. 切换分支

切换到已存在的分支：

```bash
git checkout 分支名
```

### 3. 合并分支

将其他分支合并到当前分支：

```bash
git merge 分支名
```

## 四、常见问题及解决方案

### 1. 推送失败 - 权限问题

**问题**：推送时提示权限被拒绝
**解决方案**：确保你有仓库的写入权限，或使用SSH密钥认证

### 2. 推送失败 - 本地落后于远程

**问题**：推送时提示本地分支落后于远程分支
**解决方案**：先拉取远程更新，解决冲突后再推送

```bash
git pull origin main
# 解决冲突
# 重新添加、提交
# 再次推送
```

### 3. 撤销本地更改

**解决方案**：

```bash
# 撤销未暂存的更改
git restore 文件名

# 撤销已暂存的更改
git restore --staged 文件名

# 撤销最近一次提交（但保留更改）
git reset HEAD~1
```

## 五、最佳实践

1. **定期拉取更新**：每天开始工作前拉取远程更新
2. **小步提交**：将大的更改拆分为多个小的、有意义的提交
3. **清晰的提交信息**：提交信息应准确描述更改内容
4. **分支管理**：使用分支进行功能开发和bug修复
5. **忽略不需要的文件**：使用.gitignore文件忽略临时文件和构建产物
6. **定期备份**：确保远程仓库是最新的，作为备份

## 六、项目特定说明

### 1. 注意事项

- **不要提交大文件**：模型文件、数据集等大型文件应通过其他方式管理
- **不要提交敏感信息**：确保不包含API密钥、密码等敏感信息
- **日志文件**：考虑在.gitignore中添加日志文件，避免提交过大的日志

### 2. 推荐的.gitignore配置

```gitignore
# 日志文件
*.log
logs/

# 模型文件
*.pt
*.pth

# 数据集
datasets/

# 构建产物
dist/
build/
*.egg-info/

# 环境文件
.env
venv/
env/

# IDE相关
.vscode/
.idea/
*.swp
*.swo
*~

# 操作系统相关
Thumbs.db
.DS_Store

# Python缓存
__pycache__/
*.pyc
```

## 七、命令速查表

| 操作 | 命令 |
|------|------|
| 克隆仓库 | `git clone <仓库URL>` |
| 拉取更新 | `git pull origin main` |
| 查看状态 | `git status` |
| 添加更改 | `git add .` |
| 提交更改 | `git commit -m "提交信息"` |
| 推送到远程 | `git push origin main` |
| 查看历史 | `git log` |
| 创建分支 | `git checkout -b <分支名>` |
| 切换分支 | `git checkout <分支名>` |
| 合并分支 | `git merge <分支名>` |

## 八、联系信息

如果在Git操作过程中遇到问题，可以联系项目维护者：
- GitHub: [Pursuerbin](https://github.com/Pursuerbin)

---

**最后更新时间**：2026-02-11
**版本**：1.0.0