# -*- coding: utf-8 -*-
"""
Pytest 配置和 fixtures
"""

import sys
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(project_root, 'src'))

# 添加项目根目录到 Python 路径
sys.path.insert(0, project_root)

# 将 src 目录作为包导入，使相对导入能正常工作
import importlib.util

def load_package(name, path):
    """动态加载包"""
    if name in sys.modules:
        return sys.modules[name]
    
    spec = importlib.util.spec_from_file_location(name, path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    return None

# 加载 src 包
src_path = os.path.join(project_root, 'src')
src_init = os.path.join(src_path, '__init__.py')
if os.path.exists(src_init):
    load_package('src', src_init)

# 加载所有子包
subpackages = {
    'auth': 'auth/__init__.py',
    'automators': 'automators/__init__.py',
    'collectors': 'collectors/__init__.py',
    'nlp': 'nlp/__init__.py',
    'utils': 'utils/__init__.py',
    'zentao': 'zentao/__init__.py',
}

for pkg_name, pkg_path in subpackages.items():
    full_name = f'src.{pkg_name}'
    full_path = os.path.join(src_path, pkg_path)
    if os.path.exists(full_path):
        load_package(full_name, full_path)

# 现在加载所有模块文件，使相对导入能正常工作
modules_to_load = [
    ('src.utils.logger', 'utils/logger.py'),
    ('src.utils.response', 'utils/response.py'),
    ('src.utils.config_loader', 'utils/config_loader.py'),
    ('src.utils.interactive_input', 'utils/interactive_input.py'),
    ('src.utils.story_title_updater', 'utils/story_title_updater.py'),
    ('src.utils.progress_bar', 'utils/progress_bar.py'),
    ('src.zentao.api_response', 'zentao/api_response.py'),
    ('src.zentao.api_client', 'zentao/api_client.py'),
    ('src.zentao.models', 'zentao/models.py'),
    ('src.automators.base', 'automators/base.py'),
    ('src.automators.task_splitter', 'automators/task_splitter.py'),
    ('src.automators.task_assigner', 'automators/task_assigner.py'),
]

for module_name, module_path in modules_to_load:
    full_path = os.path.join(src_path, module_path)
    if os.path.exists(full_path):
        load_package(module_name, full_path)
