#!/usr/bin/env python3
"""
测试需求11754的查询情况
"""

import sys
import json
from pathlib import Path

# 添加正确的路径
sys.path.insert(0, str(Path(__file__).parent / '.trae' / 'skills' / 'zentao-helper'))

from utils.logger import get_logger
from utils.config_loader import get_config
from auth.session_manager import SessionManager
from zentao.api_client import ZentaoApiClient

# 配置日志
logger = get_logger()
logger.setLevel('DEBUG')

# 加载配置
config = get_config()
print(f"配置的产品: {config.get('zentao.story_query.products', [])}")
print(f"配置的关键字: {config.get('zentao.story_query.keywords', [])}")

# 初始化会话管理器和API客户端
session_manager = SessionManager()
api_client = ZentaoApiClient()

# 加载会话
if session_manager.is_session_valid():
    session_data = session_manager.load_session()
    if session_data:
        cookies = session_data.get('cookies', {})
        token = session_data.get('token')
        if token:
            api_client.session.headers.update({'Token': token})
        api_client.set_cookies(cookies)
        
        # 验证会话
        if api_client.verify_session():
            print("会话验证成功")
        else:
            print("会话验证失败")
            sys.exit(1)
    else:
        print("加载会话失败")
        sys.exit(1)
else:
    print("会话无效")
    sys.exit(1)

# 测试1: 直接获取需求11754的详情
print("\n=== 测试1: 直接获取需求11754详情 ===")
result = api_client.get_story(11754)
if result.success:
    story = result.data
    print(f"需求ID: {story.get('id')}")
    print(f"标题: {story.get('title')}")
    print(f"产品: {story.get('product')}")
    print(f"状态: {story.get('status')}")
    print(f"阶段: {story.get('stage')}")
    print(f"指派给: {story.get('assigned_to')}")
    print(f"创建者: {story.get('opened_by')}")
    print(f"创建时间: {story.get('opened_date')}")
    print(f"优先级: {story.get('priority')}")
    print(f"预计工时: {story.get('estimate')}")
else:
    print(f"获取需求失败: {result.error.message}")

# 测试2: 检查需求11754是否在我的需求列表中
print("\n=== 测试2: 检查需求11754是否在我的需求列表中 ===")
result = api_client.get_my_stories()
if result.success:
    stories = result.data.get('stories', [])
    print(f"总共找到 {len(stories)} 个需求")
    
    # 检查是否包含需求11754
    found = False
    for story in stories:
        if story.get('id') == 11754:
            print(f"找到需求11754: {story.get('title')}")
            print(f"  产品: {story.get('product')}")
            print(f"  阶段: {story.get('stage')}")
            print(f"  状态: {story.get('status')}")
            found = True
            break
    
    if not found:
        print("需求11754不在我的需求列表中")
        
        # 检查产品过滤
        configured_products = config.get('zentao.story_query.products', [])
        if configured_products:
            print(f"当前配置只查询产品: {configured_products}")
        
        # 检查关键字过滤
        configured_keywords = config.get('zentao.story_query.keywords', [])
        if configured_keywords:
            print(f"当前配置只查询包含关键字: {configured_keywords}")
else:
    print(f"获取需求列表失败: {result.error.message}")

# 测试3: 检查需求11754的任务数
print("\n=== 测试3: 检查需求11754的任务数 ===")
task_count = api_client.get_story_task_count(11754)
print(f"需求11754的任务数: {task_count}")
if task_count == 0:
    print("需求11754未创建任务")
else:
    print(f"需求11754已创建 {task_count} 个任务")
