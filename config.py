from dynaconf import Dynaconf

# 初始化 Dynaconf 对象
settings = Dynaconf(
    envvar_prefix="DYNACONF",  # 环境变量前缀
    settings_files=['settings.toml', '.secrets.toml'],  # 配置文件列表
    environments=True  # 启用环境配置
)
