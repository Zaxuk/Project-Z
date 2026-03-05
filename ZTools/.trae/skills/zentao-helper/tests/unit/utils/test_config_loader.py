# -*- coding: utf-8 -*-
"""
测试配置加载器
"""

import pytest
import yaml
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from src.utils.config_loader import ConfigLoader, get_config


class TestConfigLoader:
    """测试配置加载器"""

    @pytest.fixture
    def config_loader(self, tmp_path):
        """创建配置加载器实例"""
        config_file = tmp_path / "test_config.yaml"
        config_content = """
zentao:
  base_url: "http://test.zentao.com"
  timeout: 30
  retry_times: 3

logging:
  level: "DEBUG"
  format: "json"

nlp:
  model: "gpt-3.5-turbo"
  temperature: 0.7

session:
  timeout: 3600
  encrypt: true
"""
        config_file.write_text(config_content, encoding='utf-8')
        return ConfigLoader(str(config_file))

    def test_init_with_default_path(self):
        """测试默认路径初始化"""
        loader = ConfigLoader()
        assert "config" in str(loader.config_path)
        assert "settings.yaml" in str(loader.config_path)

    def test_init_with_custom_path(self, tmp_path):
        """测试自定义路径初始化"""
        custom_path = tmp_path / "custom.yaml"
        loader = ConfigLoader(str(custom_path))
        assert loader.config_path == custom_path

    def test_load_success(self, config_loader):
        """测试成功加载配置"""
        # Act
        config = config_loader.load()

        # Assert
        assert config is not None
        assert 'zentao' in config
        assert config['zentao']['base_url'] == "http://test.zentao.com"

    def test_load_file_not_found(self):
        """测试文件不存在"""
        # Arrange
        loader = ConfigLoader("/nonexistent/path/config.yaml")

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_get_simple_key(self, config_loader):
        """测试获取简单键"""
        # Arrange
        config_loader.load()

        # Act
        result = config_loader.get('zentao')

        # Assert
        assert result is not None
        assert result['base_url'] == "http://test.zentao.com"

    def test_get_nested_key(self, config_loader):
        """测试获取嵌套键"""
        # Arrange
        config_loader.load()

        # Act
        result = config_loader.get('zentao.base_url')

        # Assert
        assert result == "http://test.zentao.com"

    def test_get_with_default(self, config_loader):
        """测试获取不存在的键返回默认值"""
        # Arrange
        config_loader.load()

        # Act
        result = config_loader.get('nonexistent.key', default='default_value')

        # Assert
        assert result == 'default_value'

    def test_get_auto_load(self, config_loader):
        """测试自动加载配置"""
        # Act - 不调用 load()，直接 get
        result = config_loader.get('zentao.timeout')

        # Assert
        assert result == 30

    def test_get_zentao_config(self, config_loader):
        """测试获取禅道配置"""
        # Act
        result = config_loader.get_zentao_config()

        # Assert
        assert result['base_url'] == "http://test.zentao.com"
        assert result['timeout'] == 30

    def test_get_logging_config(self, config_loader):
        """测试获取日志配置"""
        # Act
        result = config_loader.get_logging_config()

        # Assert
        assert result['level'] == "DEBUG"
        assert result['format'] == "json"

    def test_get_nlp_config(self, config_loader):
        """测试获取 NLP 配置"""
        # Act
        result = config_loader.get_nlp_config()

        # Assert
        assert result['model'] == "gpt-3.5-turbo"
        assert result['temperature'] == 0.7

    def test_get_session_config(self, config_loader):
        """测试获取会话配置"""
        # Act
        result = config_loader.get_session_config()

        # Assert
        assert result['timeout'] == 3600
        assert result['encrypt'] == True


class TestGetConfig:
    """测试获取全局配置实例"""

    def test_get_config_returns_singleton(self):
        """测试返回单例"""
        # 重置全局实例
        import src.utils.config_loader as config_module
        original_config = config_module._config_loader
        config_module._config_loader = None

        try:
            # Act
            config1 = get_config()
            config2 = get_config()

            # Assert
            assert config1 is config2
        finally:
            # 恢复原始配置
            config_module._config_loader = original_config

    def test_get_config_creates_new_instance(self):
        """测试创建新实例"""
        # 重置全局实例
        import src.utils.config_loader as config_module
        original_config = config_module._config_loader
        config_module._config_loader = None

        try:
            # Act
            config = get_config()

            # Assert
            assert isinstance(config, ConfigLoader)
        finally:
            # 恢复原始配置
            config_module._config_loader = original_config
