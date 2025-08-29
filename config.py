#!/usr/bin/env python3
"""
AI早报生成器配置管理模块
"""
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


# 全局配置实例
settings = AISettings()

# 导出的常量
AIBASE_LIST = settings.aibase_list_url
TZ_OFFSET = 8  # 时区偏移（小时）
TZ_SG = timezone(timedelta(hours=TZ_OFFSET))
