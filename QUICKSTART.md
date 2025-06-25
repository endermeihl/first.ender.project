# Obsidian文档展示系统 - 快速启动指南

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- pip
- Git

### 2. 安装依赖

```bash
# 克隆项目（如果是从Git仓库）
git clone <repository-url>
cd first.ender.project

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 配置文档库

将您的Obsidian文档库路径配置到环境变量：

```bash
# Windows
set OBSIDIAN_VAULT_PATH=C:\path\to\your\obsidian\vault

# Linux/Mac
export OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
```

或者复制环境变量示例文件并修改：

```bash
cp env.example .env
# 编辑 .env 文件，设置 OBSIDIAN_VAULT_PATH
```

### 4. 启动系统

#### 开发模式
```bash
python start.py
```

#### 生产模式
```bash
python run.py
```

#### Docker部署
```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 5. 访问系统

打开浏览器访问：http://localhost:5000

## 🧪 测试系统

运行系统测试脚本验证安装：

```bash
python test_system.py
```

## 📁 项目结构

```
first.ender.project/
├── app/                    # 主应用
│   ├── __init__.py        # Flask应用初始化
│   ├── routes/            # 路由模块
│   ├── services/          # 业务逻辑服务
│   └── templates/         # HTML模板
├── static/                # 静态资源
├── docs/                  # 示例文档库
├── requirements.txt       # Python依赖
├── run.py                # 生产启动文件
├── start.py              # 开发启动文件
├── test_system.py        # 系统测试
├── Dockerfile            # Docker配置
└── docker-compose.yml    # Docker Compose配置
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OBSIDIAN_VAULT_PATH` | Obsidian文档库路径 | `./docs` |
| `ANALYSIS_SERVICE_URL` | 分析服务URL | `http://localhost:8001` |
| `DEBUG` | 调试模式 | `False` |
| `HOST` | 监听地址 | `127.0.0.1` |
| `PORT` | 监听端口 | `5000` |

### 文档格式

系统支持标准的Markdown格式：

- 标题层级 (# ## ###)
- 列表和表格
- 代码块和语法高亮
- 链接和图片
- Frontmatter元数据

### Frontmatter示例

```yaml
---
title: 文档标题
tags: [标签1, 标签2]
date: 2024-01-01
author: 作者名
---
```

## 🌟 主要功能

### 文档展示
- 自动扫描Markdown文件
- 支持目录结构
- 响应式设计
- 语法高亮

### 文档分析
- 基础统计（字数、句数等）
- 可读性分析
- 关键词提取
- 情感分析
- 文档摘要

### 搜索功能
- 全文搜索
- 标签筛选
- 排序功能

### 统计分析
- 文档数量统计
- 标签分布
- 月度趋势
- 可读性分布

## 🔄 后期扩展

### 性能优化
系统预留了以下扩展接口：

1. **外部分析服务**
   - 当前：Python实现
   - 后期：可替换为C/Rust高性能服务
   - 接口：`/api/documents/{path}/analysis`

2. **全文搜索**
   - 当前：简单文本搜索
   - 后期：集成Elasticsearch
   - 支持：模糊搜索、权重排序

3. **文档关系图谱**
   - 分析文档间的链接关系
   - 可视化展示
   - 推荐相关文档

### 部署选项

#### 单机部署
```bash
python run.py
```

#### Docker部署
```bash
docker-compose up -d
```

#### 生产环境
```bash
gunicorn --config gunicorn.conf.py run:app
```

## 🐛 故障排除

### 常见问题

1. **文档库路径不存在**
   - 检查 `OBSIDIAN_VAULT_PATH` 配置
   - 确保路径包含Markdown文件

2. **依赖安装失败**
   - 升级pip：`pip install --upgrade pip`
   - 使用虚拟环境：`python -m venv venv`

3. **端口被占用**
   - 修改 `PORT` 环境变量
   - 或杀死占用端口的进程

4. **分析服务异常**
   - 检查NLTK数据是否下载
   - 查看日志文件

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# Docker日志
docker-compose logs -f obsidian-docs
```

## 📞 技术支持

如果遇到问题，请：

1. 查看日志文件
2. 运行测试脚本：`python test_system.py`
3. 检查环境配置
4. 提交Issue（如果使用Git）

## �� 许可证

MIT License 