"""
配置加载器
从 YAML 文件加载配置
"""

import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_path: str = None):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径，默认为 config/settings.yaml
        """
        if config_path is None:
            self.config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
        else:
            self.config_path = Path(config_path)

        self.config = None

    def load(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        return self.config

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'zentao.base_url'
            default: 默认值

        Returns:
            配置值
        """
        if self.config is None:
            self.load()

        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_zentao_config(self) -> Dict[str, Any]:
        """获取禅道配置"""
        return self.get('zentao', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get('logging', {})

    def get_nlp_config(self) -> Dict[str, Any]:
        """获取 NLP 配置"""
        return self.get('nlp', {})

    def get_session_config(self) -> Dict[str, Any]:
        """获取会话配置"""
        return self.get('session', {})


# 全局配置实例
_config_loader = None


def get_config() -> ConfigLoader:
    """获取全局配置实例"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader