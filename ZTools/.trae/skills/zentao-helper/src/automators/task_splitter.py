"""
任务创建器
从需求创建任务，支持交互式输入需求信息
"""

import sys
from typing import Optional, List

from .base import BaseAutomator
from ..utils.response import ApiResponse, ErrorCode, ErrorMessage
from ..utils.logger import get_logger
from ..utils.interactive_input import InteractiveInput
from ..utils.story_title_updater import StoryTitleUpdater


class TaskSplitter(BaseAutomator):
    """
    任务创建器
    支持交互式输入需求信息，自动更新需求标题
    """

    def __init__(self, api_client):
        super().__init__(api_client)
        self.logger = get_logger()
        self.interactive_input = InteractiveInput()
        self.title_updater = StoryTitleUpdater()

    def execute(
        self,
        story_id: str = None,
        user_input: str = None,
        grade: str = None,
        priority: str = None,
        online_time: str = None,
        assigned_to: str = None,
        task_hours: float = None,
        deadline: str = None,
        **kwargs
    ) -> ApiResponse:
        """
        从需求创建任务

        流程：
        1. 用户输入信息
        2. 变更需求标题
        3. 把需求关联到项目
        4. 创建任务

        Args:
            story_id: 需求ID
            user_input: 原始用户输入
            grade: 需求等级 (非交互模式)
            priority: 需求优先级 (非交互模式)
            online_time: 需求上线时间 (非交互模式)
            assigned_to: 任务执行人 (非交互模式)
            task_hours: 任务时长 (非交互模式)
            deadline: 任务截至时间 (非交互模式)
            **kwargs: 其他参数

        Returns:
            创建结果
        """
        if not story_id:
            return ApiResponse.error_response(
                ErrorCode.MISSING_PARAMETER,
                "请指定要拆解的需求ID，例如：拆解需求#123"
            )

        # 从需求创建任务
        story_result = self.api_client.get_story(int(story_id))
        if not story_result.success:
            return ApiResponse.error_response(
                ErrorCode.STORY_NOT_FOUND,
                f"需求 #{story_id} 不存在"
            )

        story = story_result.data
        self.logger.debug(f"开始从需求 #{story_id} 创建任务: {story.get('title', '')}")

        # 判断是否为非交互模式
        non_interactive = any([grade, priority, online_time, assigned_to, task_hours, deadline])
        
        if non_interactive:
            # 非交互模式：使用参数
            task_info = self.interactive_input.collect_task_info_non_interactive(
                story_title=story.get('title', ''),
                grade=grade or 'A',
                priority=priority or '非紧急',
                online_time=online_time or '下周周一',
                assigned_to=assigned_to,
                task_hours=task_hours,
                deadline=deadline or '本周周五'
            )
        else:
            # 交互模式：收集任务创建信息
            task_info = self.interactive_input.collect_task_info(story.get('title', ''))
            if not task_info:
                return ApiResponse.error_response(
                    ErrorCode.USER_CANCELLED,
                    "已取消任务创建"
                )

        # 从 task_info 获取更新后的需求标题
        updated_title = task_info['updated_title']
        
        # 步骤2: 调用 API 更新禅道中的需求标题
        self.logger.debug(f"正在更新需求 #{story_id} 的标题为: {updated_title}")
        update_result = self.api_client.update_story_title(int(story_id), updated_title)
        if not update_result.success:
            error_msg = f"更新需求标题失败: {update_result.error.message if update_result.error else '未知错误'}"
            self.logger.error(error_msg)
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"步骤2失败：{error_msg}，任务创建已中止"
            )
        else:
            self.logger.info(f"✓ 需求标题已更新: {updated_title}")

        # 步骤2.5: 评审需求（变更后状态会变成"已变更"，需要评审改回"已激活"）
        self.logger.debug(f"正在评审需求 #{story_id}")
        # 注意：评审时不修改指派人，保持原指派人不变
        # 如果传入 assigned_to，需求会被指派给新的人，导致原责任人看不到需求
        review_result = self.api_client.review_story(
            int(story_id),
            result='pass',
            assigned_to=None,  # 不修改指派人
            estimate=task_info.get('task_hours'),
            comment='需求已拆解并评审通过，准备开发'
        )
        if review_result.success:
            self.logger.info(f"✓ 需求已评审通过")
        else:
            # 评审失败不阻断流程，只记录警告
            self.logger.debug(f"需求评审失败: {review_result.error.message if review_result.error else '未知错误'}")

        # 步骤3: 选择项目
        self.logger.debug(f"正在选择项目")
        select_result = self._select_project()
        if not select_result.success:
            error_msg = f"选择项目失败: {select_result.error.message if select_result.error else '未知错误'}"
            self.logger.error(error_msg)
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"步骤3失败：{error_msg}，任务创建已中止"
            )
        else:
            execution_id = select_result.data.get('execution_id', 0)
            self.logger.info(f"✓ 已选择项目 #{execution_id}")

        # 步骤4: 创建任务
        return self._perform_create(
            int(story_id),
            task_info,
            updated_title,
            execution_id
        )

    def _select_project(self) -> ApiResponse:
        """
        选择项目

        获取配置的默认项目ID，或让用户选择项目

        Returns:
            选择结果，包含 execution_id
        """
        # 获取配置的默认项目名称
        config = self.interactive_input.config.get_zentao_config()
        default_project_name = config.get('task_creation', {}).get('default_project_name')

        # 获取所有可用的项目
        executions_result = self.api_client.get_executions()
        if not executions_result.success:
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"获取项目列表失败: {executions_result.error.message if executions_result.error else '未知错误'}"
            )

        executions = executions_result.data

        # 选择项目
        selected_execution_id = self.interactive_input.select_execution(
            executions,
            default_project_name=default_project_name
        )

        if not selected_execution_id:
            return ApiResponse.error_response(
                ErrorCode.USER_CANCELLED,
                "未选择项目，已取消任务创建"
            )

        return ApiResponse.success_response({
            'execution_id': selected_execution_id,
            'message': '已选择项目'
        })

    def _perform_create(self, story_id: int, task_info: dict, updated_title: str, execution_id: int) -> ApiResponse:
        """
        执行实际的任务创建操作

        Args:
            story_id: 需求ID
            task_info: 任务信息
            updated_title: 更新后的需求标题
            execution_id: 执行/项目ID

        Returns:
            创建结果
        """
        self.logger.debug(f"从需求 #{story_id} 创建任务")
        
        # 获取更新后的需求标题
        final_updated_title = task_info.get('updated_title', updated_title)
        
        # 生成任务标题（使用更新后的需求标题）
        # final_updated_title 已经包含：【等级】【标签1】【标签2】【标签N】YYMMDD 原标题
        task_title = f"【研发】{final_updated_title}"
        
        try:
            # 计算截止日期
            deadline = self._calculate_deadline(task_info['deadline'])

            # 创建任务
            result = self.api_client.create_task(
                execution_id=execution_id,
                name=task_title,  # 使用生成的任务标题作为任务名称
                assigned_to=task_info['assigned_to'] if task_info['assigned_to'] else None,
                estimate=task_info['task_hours'] if task_info['task_hours'] else 0,
                deadline=deadline,
                story_id=story_id  # 关联到需求
            )

            if result.success:
                created_task = result.data
                self.logger.info(f"✓ 成功创建任务 #{created_task.get('id')}")
                
                return ApiResponse.success_response({
                    'story_id': story_id,
                    'updated_title': updated_title,
                    'task_info': task_info,
                    'created_task': {
                        'id': created_task.get('id'),
                        'name': task_title,
                    },
                    'message': f'成功从需求 #{story_id} 创建任务，任务标题已更新为: {updated_title}'
                })
            else:
                error_msg = result.error.message if result.error else '未知错误'
                self.logger.error(f"创建任务失败: {error_msg}")
                return ApiResponse.error_response(
                    ErrorCode.API_ERROR,
                    f"创建任务失败: {error_msg}"
                )

        except Exception as e:
            self.logger.error(f"创建任务异常: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"创建任务失败: {str(e)}"
            )

    def _calculate_deadline(self, deadline_choice: str) -> Optional[str]:
        """
        计算截止日期

        Args:
            deadline_choice: 用户选择的截止日期（本周周五/下周周五）

        Returns:
            格式化的日期字符串 (YYYY-MM-DD) 或 None
        """
        from datetime import datetime, timedelta

        if not deadline_choice:
            return None

        today = datetime.now()
        weekday = today.weekday()  # 0=周一, 6=周日

        if deadline_choice == '本周周五':
            # 计算到本周五的天数
            days_to_friday = (4 - weekday) % 7
            if days_to_friday == 0:
                days_to_friday = 7  # 如果今天就是周五，则到下周五
            target_date = today + timedelta(days=days_to_friday)
        elif deadline_choice == '下周周五':
            # 计算到下周五的天数
            days_to_friday = (4 - weekday) % 7 + 7
            target_date = today + timedelta(days=days_to_friday)
        else:
            return None

        return target_date.strftime('%Y-%m-%d')

    def format_display(self, data: dict) -> str:
        """
        格式化显示创建结果

        Args:
            data: 创建结果数据

        Returns:
            格式化的显示文本
        """
        if not data:
            return "任务创建完成"

        lines = []
        lines.append("=" * 60)
        lines.append("任务创建成功")
        lines.append("=" * 60)

        # 显示需求信息
        if 'story_id' in data:
            lines.append(f"需求ID: #{data['story_id']}")

        # 显示更新后的需求标题
        if 'updated_title' in data:
            lines.append(f"需求标题: {data['updated_title']}")

        # 显示创建的任务
        if 'created_task' in data:
            task = data['created_task']
            lines.append("-" * 60)
            lines.append(f"任务ID: #{task.get('id', 'N/A')}")
            lines.append(f"任务标题: {task.get('name', 'N/A')}")

        lines.append("=" * 60)

        return "\n".join(lines)
