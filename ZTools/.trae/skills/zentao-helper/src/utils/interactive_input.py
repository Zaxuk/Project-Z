"""
交互式输入模块
支持用户交互式输入任务创建相关信息
"""

import sys
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from .logger import get_logger
from .config_loader import get_config


class InteractiveInput:
    """
    交互式输入处理器
    处理任务创建时的交互式输入
    """

    def __init__(self):
        self.logger = get_logger()
        self.config = get_config()

    def collect_task_info(self, story_title: str = None) -> Optional[Dict]:
        """
        收集任务创建所需的信息

        Args:
            story_title: 需求标题（用于提取标签）

        Returns:
            任务信息字典，如果用户取消返回 None
        """
        print("\n" + "=" * 60)
        print("任务创建信息确认")
        print("=" * 60)

        # 1. 需求等级
        grade = self._input_grade()

        # 2. 需求优先级
        priority = self._input_priority()

        # 3. 需求上线时间
        online_time = self._input_online_time()

        # 4. 任务执行人
        assigned_to = self._input_assigned_to()

        # 5. 任务时长
        task_hours = self._input_task_hours(grade)

        # 6. 任务截至时间
        deadline = self._input_deadline(task_hours)

        # 7. 任务标题
        task_title = self._input_task_title(story_title, grade, online_time)

        # 确认信息
        if not self._confirm_info(grade, priority, online_time, assigned_to, task_hours, deadline, task_title):
            print("\n已取消任务创建")
            return None

        return {
            'grade': grade,
            'priority': priority,
            'online_time': online_time,
            'assigned_to': assigned_to,
            'task_hours': task_hours,
            'deadline': deadline,
            'task_title': task_title
        }

    def _input_grade(self) -> str:
        """
        输入需求等级

        Returns:
            需求等级（A-/A/A+/A++/B）
        """
        while True:
            try:
                print("\n需求等级：")
                print("  1. A-")
                print("  2. A")
                print("  3. A+")
                print("  4. A++")
                print("  5. B")
                choice = input("请选择 (1-5): ").strip()

                grade_map = {'1': 'A-', '2': 'A', '3': 'A+', '4': 'A++', '5': 'B'}
                if choice in grade_map:
                    return grade_map[choice]
                else:
                    print("无效选择，请重新输入")
            except (EOFError, KeyboardInterrupt):
                print("\n输入已取消")
                return None

    def _input_priority(self) -> str:
        """
        输入需求优先级

        Returns:
            需求优先级（紧急/非紧急）
        """
        while True:
            try:
                print("\n需求优先级：")
                print("  1. 紧急")
                print("  2. 非紧急")
                choice = input("请选择 (1-2): ").strip()

                if choice == '1':
                    return '紧急'
                elif choice == '2':
                    return '非紧急'
                else:
                    print("无效选择，请重新输入")
            except (EOFError, KeyboardInterrupt):
                print("\n输入已取消")
                return None

    def _input_online_time(self) -> str:
        """
        输入需求上线时间

        Returns:
            上线时间字符串
        """
        default_rule = self.config.get_zentao_config().get('task_creation', {}).get('default_online_time', 'next_monday')
        default_text = self._get_online_time_text(default_rule)

        while True:
            try:
                print(f"\n需求上线时间：")
                print("  1. 下周周一")
                print("  2. 下周周二")
                print("  3. 下周周三")
                print("  4. 下周周四")
                print("  5. 下周周五")
                print(f"  默认: {default_text}")
                choice = input("请选择 (1-5, 直接回车使用默认): ").strip()

                if not choice:
                    return default_text

                time_map = {
                    '1': '下周周一',
                    '2': '下周周二',
                    '3': '下周周三',
                    '4': '下周周四',
                    '5': '下周周五'
                }
                if choice in time_map:
                    return time_map[choice]
                else:
                    print("无效选择，请重新输入")
            except (EOFError, KeyboardInterrupt):
                print("\n输入已取消")
                return None

    def _input_assigned_to(self) -> Optional[str]:
        """
        输入任务执行人

        Returns:
            执行人用户名，为空表示不设置
        """
        default_assigned_to = self.config.get_zentao_config().get('task_creation', {}).get('default_assigned_to', '')

        while True:
            try:
                prompt = f"\n任务执行人 (直接回车使用默认): "
                if default_assigned_to:
                    prompt = f"\n任务执行人 (直接回车使用默认: {default_assigned_to}): "

                assigned_to = input(prompt).strip()

                if not assigned_to:
                    return default_assigned_to if default_assigned_to else None
                else:
                    return assigned_to
            except (EOFError, KeyboardInterrupt):
                print("\n输入已取消")
                return None

    def _input_task_hours(self, grade: str) -> Optional[float]:
        """
        输入任务时长

        Args:
            grade: 需求等级

        Returns:
            任务时长（小时），为空表示不设置
        """
        grade_hours = self.config.get_zentao_config().get('task_creation', {}).get('grade_hours', {})
        default_hours = grade_hours.get(grade)

        while True:
            try:
                prompt = "\n任务时长（小时）"
                if default_hours is not None:
                    prompt = f"\n任务时长（小时，直接回车使用默认: {default_hours}): "

                hours_input = input(prompt).strip()

                if not hours_input:
                    return default_hours

                hours = float(hours_input)
                if hours > 0:
                    return hours
                else:
                    print("任务时长必须大于0")
            except ValueError:
                print("请输入有效的数字")
            except (EOFError, KeyboardInterrupt):
                print("\n输入已取消")
                return None

    def _input_deadline(self, task_hours: Optional[float]) -> str:
        """
        输入任务截至时间

        Args:
            task_hours: 任务时长（小时）

        Returns:
            截至时间字符串
        """
        default_rule = self.config.get_zentao_config().get('task_creation', {}).get('default_deadline', 'this_friday')
        threshold_hours = self.config.get_zentao_config().get('task_creation', {}).get('deadline_threshold_hours', 4)

        # 如果任务时长超过阈值，默认改为下周周五
        if task_hours and task_hours > threshold_hours:
            default_rule = 'next_friday'

        default_text = self._get_deadline_text(default_rule)

        while True:
            try:
                print(f"\n任务截至时间：")
                print("  1. 本周周五")
                print("  2. 下周周五")
                print(f"  默认: {default_text}")
                choice = input("请选择 (1-2, 直接回车使用默认): ").strip()

                if not choice:
                    return default_text

                if choice == '1':
                    return '本周周五'
                elif choice == '2':
                    return '下周周五'
                else:
                    print("无效选择，请重新输入")
            except (EOFError, KeyboardInterrupt):
                print("\n输入已取消")
                return None

    def _input_task_title(self, story_title: str, grade: str, online_time: str) -> str:
        """
        输入任务标题

        Args:
            story_title: 原需求标题
            grade: 需求等级
            online_time: 上线时间

        Returns:
            任务标题
        """
        default_title = self._generate_task_title(story_title, grade, online_time)

        while True:
            try:
                prompt = f"\n任务标题 (直接回车使用默认): "
                if default_title:
                    print(f"默认标题: {default_title[:80]}...")
                    prompt = f"\n任务标题 (直接回车使用默认): "

                title = input(prompt).strip()

                if not title:
                    return default_title
                else:
                    return title
            except (EOFError, KeyboardInterrupt):
                print("\n输入已取消")
                return None

    def _generate_task_title(self, story_title: str, grade: str, online_time: str) -> str:
        """
        生成任务标题

        格式：【任务】当前需求标题

        Args:
            story_title: 原需求标题
            grade: 需求等级
            online_time: 上线时间

        Returns:
            任务标题
        """
        if not story_title:
            return ""

        return f"【任务】{story_title}"

    def _confirm_info(self, grade: str, priority: str, online_time: str,
                    assigned_to: Optional[str], task_hours: Optional[float],
                    deadline: str, task_title: str) -> bool:
        """
        确认任务信息

        Returns:
            是否确认
        """
        print("\n" + "=" * 60)
        print("请确认以下信息：")
        print("=" * 60)
        print(f"需求等级: {grade}")
        print(f"需求优先级: {priority}")
        print(f"需求上线时间: {online_time}")
        print(f"任务执行人: {assigned_to if assigned_to else '未设置'}")
        print(f"任务时长: {task_hours} 小时" if task_hours else "任务时长: 未设置")
        print(f"任务截至时间: {deadline}")
        print(f"任务标题: {task_title[:80]}..." if len(task_title) > 80 else f"任务标题: {task_title}")
        print("=" * 60)

        while True:
            try:
                choice = input("\n确认以上信息？(y/n): ").strip().lower()
                if choice in ['y', 'yes']:
                    return True
                elif choice in ['n', 'no']:
                    return False
                else:
                    print("请输入 y 或 n")
            except (EOFError, KeyboardInterrupt):
                print("\n已取消")
                return False

    def _get_online_time_text(self, rule: str) -> str:
        """
        获取上线时间规则的文本描述

        Args:
            rule: 时间规则

        Returns:
            文本描述
        """
        time_map = {
            'next_monday': '下周周一',
            'next_tuesday': '下周周二',
            'next_wednesday': '下周周三',
            'next_thursday': '下周周四',
            'next_friday': '下周周五'
        }
        return time_map.get(rule, rule)

    def _get_deadline_text(self, rule: str) -> str:
        """
        获取截至时间规则的文本描述

        Args:
            rule: 时间规则

        Returns:
            文本描述
        """
        time_map = {
            'this_friday': '本周周五',
            'next_friday': '下周周五'
        }
        return time_map.get(rule, rule)
