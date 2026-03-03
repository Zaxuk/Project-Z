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

    def collect_task_info_non_interactive(
        self,
        story_title: str,
        grade: str = 'A',
        priority: str = '非紧急',
        online_time: str = '下周周一',
        assigned_to: str = None,
        task_hours: float = None,
        deadline: str = '本周周五'
    ) -> Optional[Dict]:
        """
        非交互模式：直接使用参数创建任务信息

        Args:
            story_title: 需求标题
            grade: 需求等级 (A-/A/A+/A++/B)
            priority: 需求优先级 (非紧急/紧急)
            online_time: 需求上线时间
            assigned_to: 任务执行人
            task_hours: 任务时长（小时）
            deadline: 任务截至时间

        Returns:
            任务信息字典
        """
        # 验证并规范化等级
        valid_grades = ['A-', 'A', 'A+', 'A++', 'B']
        if grade not in valid_grades:
            self.logger.warning(f"无效的需求等级: {grade}，使用默认值 A")
            grade = 'A'

        # 验证并规范化优先级
        valid_priorities = ['非紧急', '紧急']
        if priority not in valid_priorities:
            self.logger.warning(f"无效的需求优先级: {priority}，使用默认值 非紧急")
            priority = '非紧急'

        # 如果没有提供任务时长，根据等级设置默认值
        if task_hours is None:
            grade_hours = self.config.get_zentao_config().get('task_creation', {}).get('grade_hours', {})
            task_hours = grade_hours.get(grade, 2)

        # 获取默认执行人
        if not assigned_to:
            assigned_to = self.config.get_zentao_config().get('task_creation', {}).get('default_assigned_to', '')
            if not assigned_to:
                assigned_to = None

        # 生成更新后的需求标题
        from .story_title_updater import StoryTitleUpdater
        title_updater = StoryTitleUpdater()
        updated_title = title_updater.update_title(story_title, grade, online_time)

        self.logger.info(f"非交互模式: 等级={grade}, 优先级={priority}, 上线时间={online_time}, 执行人={assigned_to}, 时长={task_hours}, 截止={deadline}")

        return {
            'grade': grade,
            'priority': priority,
            'online_time': online_time,
            'assigned_to': assigned_to,
            'task_hours': task_hours,
            'deadline': deadline,
            'updated_title': updated_title,
            'task_title': None
        }

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

        # 7. 生成更新后的需求标题（用于生成任务标题，不需要单独确认）
        from .story_title_updater import StoryTitleUpdater
        title_updater = StoryTitleUpdater()
        updated_title = title_updater.update_title(story_title, grade, online_time)

        # 8. 确认所有信息（包含需求标题和任务标题）
        if not self._confirm_all_info(grade, priority, online_time, assigned_to, task_hours, deadline, updated_title):
            print("\n已取消任务创建")
            return None

        return {
            'grade': grade,
            'priority': priority,
            'online_time': online_time,
            'assigned_to': assigned_to,
            'task_hours': task_hours,
            'deadline': deadline,
            'updated_title': updated_title,
            'task_title': None  # 任务标题将根据updated_title自动生成
        }

    def _input_grade(self) -> str:
        """
        输入需求等级

        Returns:
            需求等级（A-/A/A+/A++/B），默认A
        """
        while True:
            try:
                print("\n需求等级：")
                print("  1. A-")
                print("  2. A (默认)")
                print("  3. A+")
                print("  4. A++")
                print("  5. B")
                choice = input("请选择 (1-5, 直接回车使用默认A): ").strip()

                if not choice:
                    return 'A'

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
            需求优先级（非紧急/紧急），默认非紧急
        """
        while True:
            try:
                print("\n需求优先级：")
                print("  1. 非紧急 (默认)")
                print("  2. 紧急")
                choice = input("请选择 (1-2, 直接回车使用默认非紧急): ").strip()

                if not choice or choice == '1':
                    return '非紧急'
                elif choice == '2':
                    return '紧急'
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
                print("  2. 下周周四")
                print("  3. 下下周周一")
                print("  4. 下下周周四")
                print("  5. 自定义日期")
                print(f"  默认: {default_text}")
                choice = input("请选择 (1-5, 直接回车使用默认): ").strip()

                if not choice:
                    return default_text

                if choice == '1':
                    return '下周周一'
                elif choice == '2':
                    return '下周周四'
                elif choice == '3':
                    return '下下周周一'
                elif choice == '4':
                    return '下下周周四'
                elif choice == '5':
                    # 自定义日期输入
                    custom_date = self._input_custom_date()
                    if custom_date:
                        return custom_date
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
        # 默认本周周五
        default_rule = 'this_friday'
        default_text = '本周周五'

        while True:
            try:
                print(f"\n任务截至时间：")
                print("  1. 本周周五 (默认)")
                print("  2. 下周周五")
                choice = input("请选择 (1-2, 直接回车使用默认本周周五): ").strip()

                if not choice or choice == '1':
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

        格式：【研发】【等级】【标签1】【标签2】【标签N】YYMMDD 剩余原标题

        Args:
            story_title: 原需求标题
            grade: 需求等级
            online_time: 上线时间（将被转换为YYMMDD格式）

        Returns:
            任务标题
        """
        from .story_title_updater import StoryTitleUpdater
        title_updater = StoryTitleUpdater()
        
        # 生成更新后的需求标题格式（包含等级、标签、YYMMDD）
        updated_title = title_updater.update_title(story_title, grade, online_time)
        
        # 任务标题格式：【研发】+ 更新后的需求标题
        return f"【研发】{updated_title}"

    def _confirm_all_info(self, grade: str, priority: str, online_time: str,
                         assigned_to: Optional[str], task_hours: Optional[float],
                         deadline: str, updated_title: str) -> bool:
        """
        确认所有任务信息

        Returns:
            是否确认
        """
        print("\n" + "=" * 60)
        print("请确认所有信息：")
        print("=" * 60)
        print(f"需求等级: {grade}")
        print(f"需求优先级: {priority}")
        print(f"需求上线时间: {online_time}")
        print(f"任务执行人: {assigned_to if assigned_to else '未设置'}")
        print(f"任务时长: {task_hours} 小时" if task_hours else "任务时长: 未设置")
        print(f"任务截至时间: {deadline}")
        print(f"需求标题: {updated_title[:60]}..." if len(updated_title) > 60 else f"需求标题: {updated_title}")
        print(f"任务标题: 【研发】{updated_title[:50]}..." if len(updated_title) > 50 else f"任务标题: 【研发】{updated_title}")
        print("=" * 60)

        while True:
            try:
                choice = input("\n确认以上信息？(直接回车或y确认，n取消): ").strip().lower()
                if not choice or choice in ['y', 'yes']:
                    # 回车或 y/yes 都认为是确认
                    return True
                elif choice in ['n', 'no']:
                    return False
                else:
                    print("请输入 y 直接回车确认，或 n 取消")
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

    def _input_custom_date(self) -> Optional[str]:
        """
        输入自定义日期

        Returns:
            自定义日期字符串，格式为 YYMMDD
        """
        date_pattern = r'^\d{6}$'
        
        while True:
            try:
                date_input = input("请输入自定义日期 (格式: YYMMDD, 如 260331): ").strip()
                
                if not date_input:
                    print("未输入日期，返回上级菜单")
                    return None
                
                # 验证日期格式
                if not re.match(date_pattern, date_input):
                    print("日期格式错误，请使用 YYMMDD 格式（如 260331 表示 2026年3月31日）")
                    continue
                
                # 验证日期有效性（自动补全年份为20XX）
                try:
                    full_year_date = f"20{date_input}"
                    datetime.strptime(full_year_date, '%Y%m%d')
                except ValueError:
                    print("无效的日期，请检查日期是否正确")
                    continue
                
                return date_input
            except (EOFError, KeyboardInterrupt):
                print("\n输入已取消")
                return None

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

    def select_execution(self, executions: List[Dict], default_project_name: str = None) -> Optional[int]:
        """
        选择执行/项目

        Args:
            executions: 执行/项目列表
            default_project_name: 默认项目名称（来自配置），支持部分匹配

        Returns:
            选中的执行ID，如果用户取消返回 None
        """
        if not executions:
            print("\n未找到可用的执行/项目")
            return None

        # 如果配置了默认项目名称，检查是否在列表中（支持部分匹配）
        if default_project_name:
            for exec_data in executions:
                exec_name = exec_data.get('name', '')
                # 支持部分匹配：配置 "都江堰" 可以匹配 "都江堰项目"
                if default_project_name.lower() in exec_name.lower():
                    print(f"\n使用配置的默认项目: {exec_name} (ID: {exec_data.get('id')})")
                    return exec_data.get('id')
            print(f"\n配置的默认项目名称 '{default_project_name}' 未找到匹配的项目")

        print("\n" + "=" * 60)
        print("请选择要关联的执行/项目：")
        print("=" * 60)

        # 显示执行列表
        for i, exec_data in enumerate(executions, 1):
            status = exec_data.get('status', '')
            status_text = f" [{status}]" if status else ""
            print(f"  {i}. {exec_data.get('name')} (ID: {exec_data.get('id')}){status_text}")

        print("=" * 60)

        while True:
            try:
                choice = input("\n请选择 (输入序号，直接回车取消): ").strip()

                if not choice:
                    print("已取消项目选择")
                    return None

                choice_num = int(choice)
                if 1 <= choice_num <= len(executions):
                    selected = executions[choice_num - 1]
                    print(f"\n已选择: {selected.get('name')} (ID: {selected.get('id')})")
                    return selected.get('id')
                else:
                    print(f"无效选择，请输入 1-{len(executions)} 之间的数字")
            except ValueError:
                print("请输入有效的数字")
            except (EOFError, KeyboardInterrupt):
                print("\n已取消")
                return None
