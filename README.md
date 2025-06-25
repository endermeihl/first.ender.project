# Obsidian文档展示与分析系统

一个用于展示和分析Obsidian日常文档的Python Web应用。

## 功能特性

- 📚 **文档展示**: 自动读取和展示Obsidian文档
- 🔍 **文档分析**: 提供文档内容分析和总结功能
- 📊 **统计分析**: 文档阅读量、关键词分析等
- 🎨 **现代化UI**: 响应式设计，支持暗色主题
- 🔧 **模块化架构**: 便于后期扩展和性能优化

## 项目结构

```
first.ender.project/
├── app/                    # 主应用目录
│   ├── __init__.py        # Flask应用初始化
│   ├── routes/            # 路由模块
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑服务
│   ├── utils/             # 工具函数
│   └── templates/         # HTML模板
├── static/                # 静态资源
├── docs/                  # Obsidian文档目录
├── config/                # 配置文件
├── tests/                 # 测试文件
├── requirements.txt       # Python依赖
└── run.py                # 应用启动文件
```

## 快速开始

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境**
   ```bash
   cp .env.example .env
   # 编辑.env文件，设置Obsidian文档路径
   ```

3. **启动应用**
   ```bash
   python run.py
   ```

4. **访问应用**
   打开浏览器访问 http://localhost:5000

## 配置说明

- `OBSIDIAN_VAULT_PATH`: Obsidian文档库路径
- `ANALYSIS_SERVICE_URL`: 文档分析服务URL（预留接口）
- `DEBUG`: 调试模式开关

## 后期扩展计划

- 🔄 **性能优化**: 支持C/Rust后端分析服务
- 📈 **高级分析**: 文档关系图谱、主题聚类
- 🔐 **权限管理**: 多用户支持
- 📱 **移动端**: 响应式移动端优化
- 🔍 **全文搜索**: 基于Elasticsearch的搜索功能

## 技术栈

- **后端**: Flask, Python
- **前端**: HTML5, CSS3, JavaScript, Bootstrap
- **文档处理**: Markdown, Frontmatter
- **文本分析**: NLTK, Transformers
- **数据存储**: SQLite (可扩展至PostgreSQL)

## 开发说明

项目采用模块化设计，主要模块：

- `DocumentService`: 文档读取和管理
- `AnalysisService`: 文档分析服务（预留接口）
- `WebInterface`: Web界面展示
- `DataProcessor`: 数据处理和转换

## 许可证

MIT License 