# -*- coding: utf-8 -*-
"""
测试会话管理器
"""

import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, mock_open
from cryptography.fernet import Fernet

from src.auth.session_manager import SessionManager


class TestSessionManager:
    """测试会话管理器"""

    @pytest.fixture
    def mock_config(self):
        """创建 Mock 配置"""
        with patch('src.auth.session_manager.get_config') as mock:
            config = Mock()
            config.get_session_config.return_value = {
                'keyring_service': 'TestService',
                'keyring_username': 'TestUser',
                'session_file': '.test_session.enc'
            }
            mock.return_value = config
            yield mock

    @pytest.fixture
    def mock_logger(self):
        """创建 Mock 日志"""
        with patch('src.auth.session_manager.get_logger') as mock:
            logger = Mock()
            mock.return_value = logger
            yield logger

    @pytest.fixture
    def session_manager(self, mock_config, mock_logger):
        """创建会话管理器实例"""
        with patch('keyring.get_password') as mock_get_pwd, \
             patch('keyring.set_password') as mock_set_pwd:
            # 返回一个有效的密钥
            mock_get_pwd.return_value = Fernet.generate_key().decode()
            sm = SessionManager()
            return sm

    class TestInit:
        """测试初始化"""

        def test_init_creates_cipher(self, mock_config, mock_logger):
            """测试初始化创建加密器"""
            with patch('keyring.get_password') as mock_get_pwd:
                mock_get_pwd.return_value = Fernet.generate_key().decode()
                sm = SessionManager()
                assert sm.cipher is not None

        def test_init_handles_keyring_error(self, mock_config, mock_logger):
            """测试处理 keyring 错误"""
            with patch('keyring.get_password') as mock_get_pwd:
                mock_get_pwd.side_effect = Exception("Keyring error")
                sm = SessionManager()
                assert sm.cipher is None

    class TestSaveSession:
        """测试保存会话"""

        def test_save_session_without_cipher(self, session_manager, mock_logger):
            """测试无加密器时保存失败"""
            # Arrange
            session_manager.cipher = None
            session_data = {'user': 'test_user'}

            # Act
            result = session_manager.save_session(session_data)

            # Assert
            assert result is False
            mock_logger.error.assert_called()

    class TestLoadSession:
        """测试加载会话"""

        def test_load_session_without_cipher(self, session_manager, mock_logger):
            """测试无加密器时加载失败"""
            # Arrange
            session_manager.cipher = None

            # Act
            result = session_manager.load_session()

            # Assert
            assert result is None
            mock_logger.error.assert_called()

    class TestIsSessionValid:
        """测试会话有效性检查"""

        def test_is_session_valid_without_cipher(self, session_manager):
            """测试无加密器时返回无效"""
            # Arrange
            session_manager.cipher = None

            # Act
            result = session_manager.is_session_valid()

            # Assert
            assert result is False

    class TestClearSession:
        """测试清除会话"""

        def test_clear_session_without_file(self, session_manager, mock_logger):
            """测试清除不存在的会话"""
            # Arrange
            with patch('pathlib.Path.exists', return_value=False):
                # Act
                result = session_manager.clear_session()

                # Assert
                assert result is True

    class TestGetCookies:
        """测试获取 Cookies"""

        def test_get_cookies_no_session(self, session_manager):
            """测试无会话时获取 cookies"""
            # Arrange
            with patch.object(session_manager, 'load_session', return_value=None):
                # Act
                result = session_manager.get_cookies()

                # Assert
                assert result is None

    class TestGetUserInfo:
        """测试获取用户信息"""

        def test_get_user_info_no_session(self, session_manager):
            """测试无会话时获取用户信息"""
            # Arrange
            with patch.object(session_manager, 'load_session', return_value=None):
                # Act
                result = session_manager.get_user_info()

                # Assert
                assert result is None

    class TestSaveSession:
        """测试保存会话"""

        def test_save_session_success(self, session_manager):
            """测试成功保存会话"""
            # Arrange
            session_data = {'user': 'test_user'}
            session_manager.cipher = Mock()
            session_manager.cipher.encrypt.return_value = b'encrypted_data'

            with patch('builtins.open', mock_open()) as mock_file:
                # Act
                result = session_manager.save_session(session_data)

                # Assert
                assert result is True
                mock_file.assert_called_once()

        def test_save_session_with_exception(self, session_manager, mock_logger):
            """测试保存会话时发生异常"""
            # Arrange
            session_data = {'user': 'test_user'}
            session_manager.cipher = Mock()
            session_manager.cipher.encrypt.side_effect = Exception("加密失败")

            # Act
            result = session_manager.save_session(session_data)

            # Assert
            assert result is False

    class TestLoadSession:
        """测试加载会话"""

        def test_load_session_success(self, session_manager):
            """测试成功加载会话"""
            # Arrange
            session_manager.cipher = Mock()
            session_manager.cipher.decrypt.return_value = json.dumps({
                'user': 'test_user',
                'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }).encode()

            with patch('pathlib.Path.exists', return_value=True), \
                 patch('builtins.open', mock_open(read_data=b'encrypted')):
                # Act
                result = session_manager.load_session()

                # Assert
                assert result is not None
                assert result['user'] == 'test_user'

        def test_load_session_expired(self, session_manager):
            """测试加载已过期会话"""
            # Arrange
            session_manager.cipher = Mock()
            session_manager.cipher.decrypt.return_value = json.dumps({
                'user': 'test_user',
                'expires_at': (datetime.utcnow() - timedelta(hours=1)).isoformat()  # 已过期
            }).encode()

            with patch('pathlib.Path.exists', return_value=True), \
                 patch('builtins.open', mock_open(read_data=b'encrypted')):
                # Act
                result = session_manager.load_session()

                # Assert
                assert result is None

    class TestIsSessionValid:
        """测试会话有效性检查"""

        def test_is_session_valid_with_session(self, session_manager):
            """测试有会话时返回有效"""
            # Arrange
            session_data = {'user': 'test_user'}
            with patch.object(session_manager, 'load_session', return_value=session_data):
                # Act
                result = session_manager.is_session_valid()

                # Assert
                assert result is True

        def test_is_session_valid_without_session(self, session_manager):
            """测试无会话时返回无效"""
            # Arrange
            with patch.object(session_manager, 'load_session', return_value=None):
                # Act
                result = session_manager.is_session_valid()

                # Assert
                assert result is False

    class TestClearSession:
        """测试清除会话"""

        def test_clear_session_success(self, session_manager):
            """测试成功清除会话"""
            # Arrange
            with patch('pathlib.Path.exists', return_value=True), \
                 patch('pathlib.Path.unlink') as mock_unlink:
                # Act
                result = session_manager.clear_session()

                # Assert
                assert result is True
                mock_unlink.assert_called_once()

        def test_clear_session_with_exception(self, session_manager, mock_logger):
            """测试清除会话时发生异常"""
            # Arrange
            with patch('pathlib.Path.exists', return_value=True), \
                 patch('pathlib.Path.unlink', side_effect=Exception("删除失败")):
                # Act
                result = session_manager.clear_session()

                # Assert
                assert result is False

    class TestGetCookies:
        """测试获取 Cookies"""

        def test_get_cookies_with_session(self, session_manager):
            """测试有会话时获取 cookies"""
            # Arrange
            session_data = {
                'user': 'test_user',
                'cookies': {'session': 'abc123'}
            }
            with patch.object(session_manager, 'load_session', return_value=session_data):
                # Act
                result = session_manager.get_cookies()

                # Assert
                assert result is not None
                assert result['session'] == 'abc123'

        def test_get_cookies_session_no_cookies_key(self, session_manager):
            """测试会话中无 cookies 键"""
            # Arrange
            session_data = {
                'user': 'test_user'
                # 没有 cookies 键
            }
            with patch.object(session_manager, 'load_session', return_value=session_data):
                # Act
                result = session_manager.get_cookies()

                # Assert
                assert result is None

    class TestGetUserInfo:
        """测试获取用户信息"""

        def test_get_user_info_with_session(self, session_manager):
            """测试有会话时获取用户信息"""
            # Arrange
            session_data = {
                'user': 'test_user',
                'user_info': {'id': 1, 'name': '测试用户'}
            }
            with patch.object(session_manager, 'load_session', return_value=session_data):
                # Act
                result = session_manager.get_user_info()

                # Assert
                assert result is not None
                assert result['name'] == '测试用户'

        def test_get_user_info_session_no_user_info_key(self, session_manager):
            """测试会话中无 user_info 键"""
            # Arrange
            session_data = {
                'user': 'test_user'
                # 没有 user_info 键
            }
            with patch.object(session_manager, 'load_session', return_value=session_data):
                # Act
                result = session_manager.get_user_info()

                # Assert
                assert result is None

    class TestEncryptionKey:
        """测试加密密钥管理"""

        def test_get_encryption_key_from_keyring(self, mock_config, mock_logger):
            """测试从 keyring 获取密钥"""
            with patch('keyring.get_password') as mock_get_pwd:
                mock_get_pwd.return_value = Fernet.generate_key().decode()
                sm = SessionManager()
                assert sm.cipher is not None

        def test_get_encryption_key_generates_new(self, mock_config, mock_logger):
            """测试生成新密钥"""
            with patch('keyring.get_password') as mock_get_pwd, \
                 patch('keyring.set_password') as mock_set_pwd:
                mock_get_pwd.return_value = None  # keyring 中没有密钥
                sm = SessionManager()
                assert sm.cipher is not None
                mock_set_pwd.assert_called_once()
                mock_logger.info.assert_called_with("创建新的会话加密密钥")

    class TestSaveSessionSuccess:
        """测试保存会话成功场景"""

        def test_save_session_logs_success(self, session_manager, mock_logger):
            """测试保存会话成功时记录日志"""
            # Arrange
            session_data = {'user': 'test_user'}
            session_manager.cipher = Mock()
            session_manager.cipher.encrypt.return_value = b'encrypted_data'

            with patch('builtins.open', mock_open()):
                # Act
                result = session_manager.save_session(session_data)

                # Assert
                assert result is True
                mock_logger.info.assert_called_with("会话已保存", extra={'user': 'test_user'})

    class TestSaveSessionException:
        """测试保存会话异常场景"""

        def test_save_session_file_write_exception(self, session_manager, mock_logger):
            """测试保存会话时文件写入异常"""
            # Arrange
            session_data = {'user': 'test_user'}
            session_manager.cipher = Mock()
            session_manager.cipher.encrypt.return_value = b'encrypted_data'

            with patch('builtins.open', side_effect=IOError("磁盘已满")):
                # Act
                result = session_manager.save_session(session_data)

                # Assert
                assert result is False
                mock_logger.error.assert_called()

    class TestLoadSessionSuccess:
        """测试加载会话成功场景"""

        def test_load_session_logs_success(self, session_manager, mock_logger):
            """测试加载会话成功时记录日志"""
            # Arrange
            session_manager.cipher = Mock()
            session_manager.cipher.decrypt.return_value = json.dumps({
                'user': 'test_user',
                'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }).encode()

            with patch('pathlib.Path.exists', return_value=True), \
                 patch('builtins.open', mock_open(read_data=b'encrypted')):
                # Act
                result = session_manager.load_session()

                # Assert
                assert result is not None
                mock_logger.info.assert_called_with("会话已加载", extra={'user': 'test_user'})

    class TestClearSessionSuccess:
        """测试清除会话成功场景"""

        def test_clear_session_logs_success(self, session_manager, mock_logger):
            """测试清除会话成功时记录日志"""
            # Arrange
            with patch('pathlib.Path.exists', return_value=True), \
                 patch('pathlib.Path.unlink') as mock_unlink:
                # Act
                result = session_manager.clear_session()

                # Assert
                assert result is True
                mock_logger.info.assert_called_with("会话已清除")

    class TestUpdateSession:
        """测试更新会话"""

        def test_update_session_calls_save_session(self, session_manager):
            """测试更新会话调用保存会话"""
            # Arrange
            session_data = {'user': 'test_user'}
            with patch.object(session_manager, 'save_session', return_value=True) as mock_save:
                # Act
                result = session_manager.update_session(session_data)

                # Assert
                assert result is True
                mock_save.assert_called_once_with(session_data)


