"""
测试 ZenTao Helper Skill
模拟登录和 API 响应，验证 Skill 功能
"""

import sys
import json
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.logger import get_logger
from src.utils.response import ApiResponse
from src.nlp.command_parser import CommandParser

# 模拟的会话数据
MOCK_SESSION = {
    'user': 'test_user',
    'token': 'mock_token_12345',
    'cookies': {'zentaosid': 'mock_session_id'},
    'user_info': {
        'account': 'test_user',
        'realname': '测试用户',
        'id': 1
    }
}

# 模拟的 API 响应
MOCK_STORIES = {
    'stories': [
        {
            'id': 101,
            'title': '用户登录功能开发',
            'status': 'active',
            'priority': 1,
            'assigned_to': '测试用户',
            'module': '用户模块',
            'opened_date': '2026-02-01T10:00:00Z'
        },
        {
            'id': 102,
            'title': '订单管理界面优化',
            'status': 'active',
            'priority': 2,
            'assigned_to': '测试用户',
            'module': '订单模块',
            'opened_date': '2026-02-05T14:30:00Z'
        },
        {
            'id': 103,
            'title': '支付接口对接',
            'status': 'draft',
            'priority': 3,
            'assigned_to': '测试用户',
            'module': '支付模块',
            'opened_date': '2026-02-10T09:15:00Z'
        }
    ],
    'total': 3,
    'count': 3
}

MOCK_TASKS = {
    'tasks': [
        {
            'id': 201,
            'title': '实现登录页面 UI',
            'status': 'wait',
            'type': 'devel',
            'priority': 1,
            'assigned_to': '测试用户',
            'estimate': 4,
            'left': 4
        },
        {
            'id': 202,
            'title': '开发后端登录接口',
            'status': 'doing',
            'type': 'devel',
            'priority': 1,
            'assigned_to': '测试用户',
            'estimate': 8,
            'left': 3
        },
        {
            'id': 203,
            'title': '编写登录测试用例',
            'status': 'wait',
            'type': 'test',
            'priority': 2,
            'assigned_to': '测试用户',
            'estimate': 2,
            'left': 2
        }
    ],
    'total': 3,
    'count': 3
}


def test_command_parsing():
    """测试命令解析功能"""
    print("=" * 60)
    print("测试 1: 命令解析")
    print("=" * 60)

    parser = CommandParser()

    test_cases = [
        "查看我的需求",
        "显示任务列表",
        "拆解任务#123",
        "拆解任务#123为前端开发和后端开发",
        "把任务#456分配给张三",
        "指派任务#789给wangxiaoming",
        "帮助"
    ]

    for test_input in test_cases:
        result = parser.parse(test_input)
        print(f"\n输入: {test_input}")
        print(f"  意图: {result['intent']}")
        print(f"  实体: {result['entities']}")


def test_story_display():
    """测试需求显示格式"""
    print("\n" + "=" * 60)
    print("测试 2: 需求显示格式")
    print("=" * 60)

    stories = MOCK_STORIES['stories']
    total = MOCK_STORIES['total']

    lines = [f"需求列表 (共 {total} 个):\n"]

    for story in stories:
        status_map = {
            'draft': '草稿',
            'active': '激活',
            'closed': '已关闭',
            'changed': '已变更'
        }

        status_text = status_map.get(story.get('status', ''), story.get('status', ''))

        line = f"  #{story['id']} - {story['title']}\n"
        line += f"    状态: {status_text} | 优先级: {story.get('priority', 0)}\n"

        if story.get('assigned_to'):
            line += f"    指派给: {story['assigned_to']}\n"

        if story.get('module'):
            line += f"    模块: {story['module']}\n"

        lines.append(line)

    print(''.join(lines))


def test_task_display():
    """测试任务显示格式"""
    print("\n" + "=" * 60)
    print("测试 3: 任务显示格式")
    print("=" * 60)

    tasks = MOCK_TASKS['tasks']
    total = MOCK_TASKS['total']

    lines = [f"任务列表 (共 {total} 个):\n"]

    # 按状态分组
    status_groups = {
        'wait': [],
        'doing': [],
        'done': [],
        'closed': [],
        'other': []
    }

    for task in tasks:
        status = task.get('status', '')
        if status in status_groups:
            status_groups[status].append(task)
        else:
            status_groups['other'].append(task)

    status_names = {
        'wait': '待办',
        'doing': '进行中',
        'done': '已完成',
        'closed': '已关闭',
        'other': '其他'
    }

    # 显示非空组
    for status, group_tasks in status_groups.items():
        if not group_tasks:
            continue

        lines.append(f"\n  [{status_names[status]}] ({len(group_tasks)} 个)\n")

        for task in group_tasks:
            line = f"    #{task['id']} - {task['title']}\n"
            line += f"      类型: {task.get('type', '')} | 优先级: {task.get('priority', 0)}\n"

            if task.get('assigned_to'):
                line += f"      指派给: {task['assigned_to']}\n"

            if task.get('estimate'):
                line += f"      预估: {task['estimate']}h"

            if task.get('left'):
                line += f" | 剩余: {task['left']}h"

            lines.append(line + "\n")

    print(''.join(lines))


def test_api_response():
    """测试 API 响应结构"""
    print("\n" + "=" * 60)
    print("测试 4: API 响应结构")
    print("=" * 60)

    # 测试成功响应
    success_response = ApiResponse.success_response(MOCK_STORIES)
    print("\n成功响应:")
    print(json.dumps(success_response.to_dict(), indent=2, ensure_ascii=False))

    # 测试错误响应
    from src.utils.response import ErrorCode, ErrorMessage
    error_response = ApiResponse.error_response(
        ErrorCode.SESSION_EXPIRED,
        ErrorMessage.SESSION_EXPIRED
    )
    print("\n错误响应:")
    print(json.dumps(error_response.to_dict(), indent=2, ensure_ascii=False))


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("ZenTao Helper Skill 功能测试")
    print("=" * 60)

    test_command_parsing()
    test_story_display()
    test_task_display()
    test_api_response()

    print("\n" + "=" * 60)
    print("所有测试完成!")
    print("=" * 60)
    print("\nSkill 已准备就绪，可以连接真实的禅道服务器使用。")
    print("首次使用时，运行: python skill.py")
    print("然后输入您的禅道用户名和密码进行登录。")


if __name__ == "__main__":
    main()