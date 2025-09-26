#!/usr/bin/env python3
import os
from typing import Optional
from pathlib import Path
from datetime import timezone, timedelta
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# pydantic_settings 配置管理
try:

    class AISettings(BaseSettings):
        """AI早报生成器配置"""

        zhipu_api_key: Optional[str] = Field(None, description="智谱AI API密钥")
        zhipu_base_url: str = Field(
            "https://open.bigmodel.cn/api/paas/v4", description="智谱AI API基础URL"
        )
        aibase_list_url: str = Field(
            "https://www.aibase.com/zh/news/", description="AIBase新闻列表URL"
        )
        default_hours: int = Field(24, description="默认抓取小时数")
        default_max_articles: int = Field(40, description="默认最大文章数")
        request_timeout: int = Field(15, description="请求超时时间（秒）")
        batch_size: int = Field(5, description="每批抓取数量")
        min_delay: float = Field(0.5, description="最小请求延迟（秒）")
        max_delay: float = Field(1.5, description="最大请求延迟（秒）")
        min_batch_delay: float = Field(2.0, description="最小批次延迟（秒）")
        max_batch_delay: float = Field(4.0, description="最大批次延迟（秒）")

        model_config = SettingsConfigDict(
            env_file=os.getcwd() + "/.env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )

    class GiteaSettings(BaseSettings):
        """Gitea配置"""

        gitea_base_url: str = Field(
            "https://gitea.waimaogongshe.cn", description="Gitea地址"
        )
        gitea_api_token: str = Field("", description="Gitea API Token")
        gitea_owner: str = Field("moling.wei", description="仓库拥有者")
        gitea_repo: str = Field("AI-api", description="仓库名")
        gitea_author_name: str = Field("moling.wei", description="提交作者名字")
        gitea_author_email: str = Field(
            "moling.wei@waimaogongshe.cn", description="提交作者邮箱"
        )
        gitea_branch: str = Field("main", description="分支名")

        model_config = SettingsConfigDict(
            env_file=os.getcwd() + "/.env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )

    class IpzanSettings(BaseSettings):
        """Iipzan配置"""

        IPZAN_CONFIG_NO: str = Field("", description="IPZAN配置NO")
        IPZAN_CONFIG_LOGIN_PASSWORD: str = Field("", description="IPZAN配置登录密码")
        IPZAN_CONFIG_PACKAGE_KEY: str = Field("", description="IPZAN配置包密钥")
        IPZAN_CONFIG_SIGN_KEY: str = Field("", description="IPZAN配置签名密钥")
        IPZAN_CONFIG_USER_ID: str = Field("", description="IPZAN配置用户ID")

        model_config = SettingsConfigDict(
            env_file=os.getcwd() + "/.env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )

except ImportError:
    # 如果 pydantic_settings 不可用，使用简单的配置类
    class AISettings:
        """简化的配置类"""

        def __init__(self):
            self.zhipu_api_key = ""
            self.zhipu_base_url = "https://open.bigmodel.cn/api/paas/v4"
            self.aibase_list_url = "https://www.aibase.com/zh/news/"
            self.default_hours = 24
            self.default_max_articles = 40
            self.request_timeout = 15
            self.batch_size = 5
            self.min_delay = 0.5
            self.max_delay = 1.5
            self.min_batch_delay = 2.0
            self.max_batch_delay = 4.0

    class IpzanSettings:
        """简化的Ipzan配置类"""

        def __init__(self):
            self.IPZAN_CONFIG_NO = os.getenv("IPZAN_CONFIG_NO", "")
            self.IPZAN_CONFIG_LOGIN_PASSWORD = os.getenv("IPZAN_CONFIG_LOGIN_PASSWORD", "")
            self.IPZAN_CONFIG_PACKAGE_KEY = os.getenv("IPZAN_CONFIG_PACKAGE_KEY", "")
            self.IPZAN_CONFIG_SIGN_KEY = os.getenv("IPZAN_CONFIG_SIGN_KEY", "")
            self.IPZAN_CONFIG_USER_ID = os.getenv("IPZAN_CONFIG_USER_ID", "")

    class GiteaSettings:
        """简化的Gitea配置类"""

        def __init__(self):
            self.gitea_base_url = os.getenv(
                "GITEA_BASE_URL", "https://gitea.waimaogongshe.cn"
            )
            self.gitea_api_token = os.getenv("GITEA_API_TOKEN", "")
            self.gitea_owner = os.getenv("GITEA_OWNER", "moling.wei")
            self.gitea_repo = os.getenv("GITEA_REPO", "AI-api")
            self.gitea_author_name = os.getenv("GITEA_AUTHOR_NAME", "moling.wei")
            self.gitea_author_email = os.getenv(
                "GITEA_AUTHOR_EMAIL", "moling.wei@waimaogongshe.cn"
            )
            self.gitea_branch = os.getenv("GITEA_BRANCH", "main")


# 全局配置实例
settings = AISettings()
gitea_settings = GiteaSettings()
ipzan_settings = IpzanSettings()
# 导出的常量
AIBASE_LIST = settings.aibase_list_url
TZ_OFFSET = 8  # 时区偏移（小时）
TZ_SG = timezone(timedelta(hours=TZ_OFFSET))
