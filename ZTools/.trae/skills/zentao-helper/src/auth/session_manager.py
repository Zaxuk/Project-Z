"""
会话管理模块
使用系统 keyring 加密存储会话信息，避免存储密码等敏感信息
"""

import keyring
import json
from pathlib import Path
from typing import Dict, Optional
from cryptography.fernet import Fernet
from datetime import datetime, timedelta

from ..utils.logger import get_logger
from ..utils.config_loader import get_config
from ..utils.response import ErrorCode, ErrorMessage


class SessionManager:
    """
    会话管理器
    负责会话的创建、存储、加载和验证
    """

    def __init__(self):
        self.logger = get_logger()
        self.config = get_config()
        self.cipher = self._init_cipher()
        self.session_file = Path(__file__).parent.parent.parent / self.config.get_session_config().get('session_file', '.session.enc')

    def _init_cipher(self) -> Optional[Fernet]:
        """
        初始化加密器
        使用系统 keyring 存储加密密钥
        """
        try:
            keyring_service = self.config.get_session_config().get('keyring_service', 'ZTools')
            keyring_username = self.config.get_session_config().get('keyring_username', 'zentao-session')

            # 尝试从 keyring 获取密钥
            key = keyring.get_password(keyring_service, keyring_username)

            if not key:
                # 如果密钥不存在，生成新密钥并存储
                key = Fernet.generate_key().decode()
                keyring.set_password(keyring_service, keyring_username, key)
                self.logger.info("创建新的会话加密密钥")

            return Fernet(key.encode())

        except Exception as e:
            self.logger.error(f"初始化加密器失败: {str(e)}")
            return None

    def save_session(self, session_data: Dict) -> bool:
        """
        保存会话信息

        Args:
            session_data: 会话数据，包含 cookies、user_info 等

        Returns:
            是否保存成功
        """
        if not self.cipher:
            self.logger.error("加密器未初始化，无法保存会话")
            return False

        try:
            # 添加过期时间（默认24小时）
            session_data['expires_at'] = (datetime.utcnow() + timedelta(hours=24)).isoformat()

            # 加密会话数据
            session_json = json.dumps(session_data, ensure_ascii=False)
            encrypted_data = self.cipher.encrypt(session_json.encode())

            # 写入文件
            with open(self.session_file, 'wb') as f:
                f.write(encrypted_data)

            self.logger.info("会话已保存", extra={'user': session_data.get('user', 'unknown')})
            return True

        except Exception as e:
            self.logger.error(f"保存会话失败: {str(e)}")
            return False

    def load_session(self) -> Optional[Dict]:
        """
        加载会话信息

        Returns:
            会话数据，如果会话不存在或已过期返回 None
        """
        if not self.cipher:
            self.logger.error("加密器未初始化，无法加载会话")
            return None

        if not self.session_file.exists():
            self.logger.info("会话文件不存在")
            return None

        try:
            # 读取加密数据
            with open(self.session_file, 'rb') as f:
                encrypted_data = f.read()

            # 解密
            decrypted_data = self.cipher.decrypt(encrypted_data)
            session_data = json.loads(decrypted_data.decode())

            # 检查会话是否过期
            expires_at = session_data.get('expires_at')
            if expires_at:
                expire_time = datetime.fromisoformat(expires_at)
                if datetime.utcnow() > expire_time:
                    self.logger.info("会话已过期")
                    return None

            self.logger.info("会话已加载", extra={'user': session_data.get('user', 'unknown')})
            return session_data

        except Exception as e:
            self.logger.error(f"加载会话失败: {str(e)}")
            return None

    def is_session_valid(self) -> bool:
        """
        检查会话是否有效

        Returns:
            会话是否有效
        """
        session = self.load_session()
        return session is not None

    def clear_session(self) -> bool:
        """
        清除会话信息

        Returns:
            是否清除成功
        """
        try:
            if self.session_file.exists():
                self.session_file.unlink()
                self.logger.info("会话已清除")
            return True
        except Exception as e:
            self.logger.error(f"清除会话失败: {str(e)}")
            return False

    def get_cookies(self) -> Optional[Dict]:
        """
        获取会话 cookies

        Returns:
            cookies 字典
        """
        session = self.load_session()
        if session:
            return session.get('cookies')
        return None

    def get_user_info(self) -> Optional[Dict]:
        """
        获取用户信息

        Returns:
            用户信息字典
        """
        session = self.load_session()
        if session:
            return session.get('user_info')
        return None

    def update_session(self, session_data: Dict) -> bool:
        """
        更新会话信息

        Args:
            session_data: 新的会话数据

        Returns:
            是否更新成功
        """
        return self.save_session(session_data)