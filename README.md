# Spider

个人兴趣项目，用于爬取各种网站数据并进行数据分析。本项目包含多个独立的爬虫模块，针对不同的平台和服务。

> **免责声明**: 本项目仅用于学习和研究目的。请遵守目标网站的 robots.txt 规则和服务条款。如有任何侵权问题，请联系我删除相关内容。

## 项目特性

- 🕷️ **多平台支持**: 支持社交媒体、电商平台、教育系统等多个中文平台
- 🚀 **现代化工具**: 使用 uv 包管理器，支持 Python 3.13+
- 🔧 **模块化设计**: 每个平台独立模块，便于维护和扩展
- 📊 **数据处理**: 内置数据清洗、转换和分析功能
- 🛡️ **安全考虑**: 支持代理轮换、用户代理伪装等反爬虫措施

## 项目结构

```
Spider/
├── main.py                 # 主入口文件
├── config.py              # 配置管理
├── settings.toml          # 环境配置
├── pyproject.toml         # 项目依赖配置
├── utils/                 # 工具函数
│   ├── __init__.py
│   └── get_ip.py         # IP获取工具
├── 社交媒体/
│   ├── 微博/              # 微博数据爬取
│   ├── FaceBook/          # Facebook数据获取
│   └── 知乎/              # 知乎数据爬取
├── 电商平台/
│   ├── 猫眼/              # 猫眼电影数据
│   ├── 懂车帝/            # 汽车数据
│   └── 艺恩/              # 影视数据
├── 教育平台/
│   ├── 今日校园/          # 校园信息系统
│   ├── 学习通/            # 在线学习平台
│   ├── 教务系统/          # 教学管理系统
│   └── 校友邦/            # 实习管理平台
├── 音乐娱乐/
│   ├── 网易云/            # 网易云音乐
│   ├── 爱奇艺/            # 爱奇艺视频
│   └── 豆瓣/              # 豆瓣电影
└── 工具模块/
    ├── ipzan/             # 代理IP管理
    ├── Google/            # Google搜索
    ├── Bing/              # Bing搜索
    └── Weather/           # 天气数据
```

## 安装和设置

### 环境要求

- Python 3.13+
- 推荐使用 uv 包管理器

### 安装依赖

**使用 uv (推荐):**

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

**使用 pip:**

```bash
# 安装依赖
pip install -r requirements.txt
```

### 配置设置

1. 复制配置文件模板:

```bash
cp settings.toml.example settings.toml  # 如果存在模板
```

2. 编辑 `settings.toml` 文件配置环境参数:

```toml
[development]
DEBUG = true
PORT = 8080
DATABASE_URL = "sqlite:///development.db"
```

3. 敏感信息配置 (可选):

```bash
# 创建 .secrets.toml 文件存储敏感信息
echo "API_KEY = 'your_api_key'" > .secrets.toml
```

## 使用方法

### 运行单个爬虫模块

每个模块都可以独立运行，直接进入对应目录执行主程序：

```bash
# 运行 Hacker News 爬虫
python hacknews/main.py

# 运行网易云音乐爬虫
python 网易云/评论/main.py

# 运行猫眼电影数据爬虫
python 猫眼/main.py

# 运行IP检测工具
python utils/get_ip.py
```

### 主要模块介绍

#### 🔥 热门模块

- **Hacker News** (`hacknews/`) - 异步爬取 Hacker News 热门新闻，支持关键词筛选
- **网易云音乐** (`网易云音乐/`) - 获取音乐排行榜、歌词、评论等数据
- **微博** (`微博/`) - 微博用户评论和内容分析
- **懂车帝** (`懂车帝/`) - 汽车销售数据和城市车辆信息
- **猫眼电影** (`猫眼/`) - 电影票房和评分数据

#### 📚 教育平台模块

- **今日校园** - 校园信息系统数据获取
- **学习通** - 在线学习平台数据
- **教务系统** - 教学管理系统登录和数据获取
- **校友邦** - 实习管理平台数据

#### 🛠️ 工具模块

- **Google 搜索** - Google 搜索结果获取
- **IP 代理** - 代理 IP 管理和轮换
- **天气数据** - 天气信息获取和处理
- **CSV 工具** - 数据格式转换和处理

### 示例用法

#### 1. Hacker News 爬虫

```bash
cd hacknews
python main.py
# 输出：AI相关的热门新闻和链接
```

#### 2. 网易云音乐评论

```bash
cd 网易云/评论
python main.py
# 获取歌曲评论数据并保存为JSON
```

#### 3. IP 检测工具

```bash
python utils/get_ip.py
# 输出：Your external IP is: xxx.xxx.xxx.xxx
```

### 数据输出格式

大部分模块支持多种数据输出格式：

- **JSON** - 结构化数据存储
- **CSV** - 表格数据，便于 Excel 处理
- **数据库** - 部分模块支持 SQLite 存储

## 开发指南

### 添加新模块

1. **创建模块目录**:
```bash
mkdir 新模块名称
cd 新模块名称
```

2. **创建主程序文件**:
```python
# main.py
import requests
from loguru import logger

def main():
    logger.info("开始爬取数据...")
    # 你的爬虫逻辑
    pass

if __name__ == "__main__":
    main()
```

3. **添加依赖** (如果需要):
```bash
# 编辑 pyproject.toml 添加新依赖
```

### 代码规范

- 使用 `loguru` 进行日志记录
- 优先使用 `httpx` 进行异步请求
- 错误处理要完善，避免程序崩溃
- 遵守目标网站的 robots.txt 规则
- 添加适当的延迟，避免对目标服务器造成压力

### 配置管理

项目使用 Dynaconf 进行配置管理：

```python
from config import settings

# 使用配置
api_key = settings.API_KEY
debug_mode = settings.DEBUG
```

### 反爬虫策略

- **用户代理轮换**: 使用 `fake-useragent`
- **代理IP**: 使用 `ipzan` 模块管理代理
- **请求延迟**: 添加随机延迟避免被封
- **会话管理**: 使用 `requests.Session` 保持连接

## 许可证

本项目仅供学习和研究使用，请勿用于商业用途。

## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues
- Email: [你的邮箱]

## 免责声明

- 本项目仅用于学习和研究目的
- 请遵守目标网站的服务条款和 robots.txt 规则
- 使用本项目造成的任何后果，开发者不承担责任
- 如有侵权问题，请联系删除相关内容
