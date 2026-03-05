# -*- coding: utf-8 -*-
"""
测试禅道数据模型
"""

import pytest
from datetime import datetime

from src.zentao.models import User, Story, Task


class TestUser:
    """测试用户模型"""

    def test_user_creation(self):
        """测试创建用户"""
        # Act
        user = User(
            id=1,
            account="test_user",
            realname="测试用户",
            email="test@example.com",
            avatar="http://example.com/avatar.png"
        )

        # Assert
        assert user.id == 1
        assert user.account == "test_user"
        assert user.realname == "测试用户"
        assert user.email == "test@example.com"
        assert user.avatar == "http://example.com/avatar.png"

    def test_user_from_api(self):
        """测试从 API 响应创建用户"""
        # Arrange
        data = {
            'id': 2,
            'account': 'api_user',
            'realname': 'API用户',
            'email': 'api@test.com',
            'avatar': 'http://test.com/avatar.jpg'
        }

        # Act
        user = User.from_api(data)

        # Assert
        assert user.id == 2
        assert user.account == 'api_user'
        assert user.realname == 'API用户'
        assert user.email == 'api@test.com'

    def test_user_from_api_with_defaults(self):
        """测试从 API 响应创建用户（使用默认值）"""
        # Arrange
        data = {
            'id': 3,
            'account': 'minimal'
        }

        # Act
        user = User.from_api(data)

        # Assert
        assert user.id == 3
        assert user.account == 'minimal'
        assert user.realname == ''
        assert user.email is None
        assert user.avatar is None


class TestStory:
    """测试需求模型"""

    def test_story_creation(self):
        """测试创建需求"""
        # Act
        story = Story(
            id=1,
            title="测试需求",
            status="active",
            priority=3,
            estimate=8.0,
            description="需求描述"
        )

        # Assert
        assert story.id == 1
        assert story.title == "测试需求"
        assert story.status == "active"
        assert story.priority == 3
        assert story.estimate == 8.0
        assert story.description == "需求描述"

    def test_story_from_api(self):
        """测试从 API 响应创建需求"""
        # Arrange
        data = {
            'id': 123,
            'title': 'API需求',
            'status': 'active',
            'pri': 2,
            'estimate': 16,
            'spec': '需求规格说明',
            'module': '模块A',
            'product': '产品B'
        }

        # Act
        story = Story.from_api(data)

        # Assert
        assert story.id == 123
        assert story.title == 'API需求'
        assert story.status == 'active'
        assert story.priority == 2
        assert story.estimate == 16
        assert story.description == '需求规格说明'
        assert story.module == '模块A'
        assert story.product == '产品B'

    def test_story_from_api_with_users(self):
        """测试从 API 响应创建需求（带用户信息）"""
        # Arrange
        users = {
            'user1': User(id=1, account='user1', realname='用户1'),
            'user2': User(id=2, account='user2', realname='用户2')
        }
        data = {
            'id': 456,
            'title': '带用户的需求',
            'status': 'active',
            'pri': 1,
            'assignedTo': 'user1',
            'openedBy': 'user2'
        }

        # Act
        story = Story.from_api(data, users)

        # Assert
        assert story.assigned_to is not None
        assert story.assigned_to.realname == '用户1'
        assert story.opened_by is not None
        assert story.opened_by.realname == '用户2'

    def test_story_from_api_with_dates(self):
        """测试从 API 响应创建需求（带日期）"""
        # Arrange
        data = {
            'id': 789,
            'title': '带日期的需求',
            'status': 'active',
            'pri': 3,
            'openedDate': '2024-03-15T10:30:00',
            'assignedDate': '2024-03-16T14:20:00'
        }

        # Act
        story = Story.from_api(data)

        # Assert
        assert story.opened_date is not None
        assert story.assigned_date is not None

    def test_story_from_api_with_invalid_dates(self):
        """测试从 API 响应创建需求（带无效日期）"""
        # Arrange
        data = {
            'id': 999,
            'title': '无效日期需求',
            'status': 'active',
            'pri': 3,
            'openedDate': 'invalid_date',
            'assignedDate': 'also_invalid'
        }

        # Act
        story = Story.from_api(data)

        # Assert
        assert story.opened_date is None
        assert story.assigned_date is None

    def test_story_to_dict(self):
        """测试需求转字典"""
        # Arrange
        story = Story(
            id=1,
            title="测试需求",
            status="active",
            priority=3,
            estimate=8.0,
            module="模块A",
            product="产品B"
        )

        # Act
        result = story.to_dict()

        # Assert
        assert result['id'] == 1
        assert result['title'] == "测试需求"
        assert result['status'] == "active"
        assert result['priority'] == 3
        assert result['estimate'] == 8.0
        assert result['module'] == "模块A"
        assert result['product'] == "产品B"

    def test_story_to_dict_with_users(self):
        """测试需求转字典（带用户）"""
        # Arrange
        assigned_user = User(id=1, account='user1', realname='指派用户')
        opened_user = User(id=2, account='user2', realname='创建用户')
        story = Story(
            id=1,
            title="测试需求",
            status="active",
            priority=3,
            assigned_to=assigned_user,
            opened_by=opened_user
        )

        # Act
        result = story.to_dict()

        # Assert
        assert result['assigned_to'] == '指派用户'
        assert result['opened_by'] == '创建用户'


class TestTask:
    """测试任务模型"""

    def test_task_creation(self):
        """测试创建任务"""
        # Act
        task = Task(
            id=1,
            title="测试任务",
            status="doing",
            priority=2,
            type="devel",
            estimate=4.0,
            consumed=2.0,
            left=2.0
        )

        # Assert
        assert task.id == 1
        assert task.title == "测试任务"
        assert task.status == "doing"
        assert task.priority == 2
        assert task.type == "devel"
        assert task.estimate == 4.0
        assert task.consumed == 2.0
        assert task.left == 2.0

    def test_task_from_api(self):
        """测试从 API 响应创建任务"""
        # Arrange
        data = {
            'id': 123,
            'name': 'API任务',
            'status': 'done',
            'pri': 1,
            'type': 'test',
            'estimate': 8,
            'consumed': 8,
            'left': 0,
            'parent': 0,
            'story': 456,
            'module': '测试模块',
            'desc': '任务描述'
        }

        # Act
        task = Task.from_api(data)

        # Assert
        assert task.id == 123
        assert task.title == 'API任务'
        assert task.status == 'done'
        assert task.priority == 1
        assert task.type == 'test'
        assert task.estimate == 8
        assert task.consumed == 8
        assert task.left == 0
        assert task.story == 456
        assert task.module == '测试模块'
        assert task.description == '任务描述'

    def test_task_from_api_with_users(self):
        """测试从 API 响应创建任务（带用户信息）"""
        # Arrange
        users = {
            'user1': User(id=1, account='user1', realname='执行者'),
            'user2': User(id=2, account='user2', realname='创建者'),
            'user3': User(id=3, account='user3', realname='完成者')
        }
        data = {
            'id': 789,
            'name': '带用户的任务',
            'status': 'done',
            'pri': 3,
            'type': 'devel',
            'assignedTo': 'user1',
            'openedBy': 'user2',
            'finishedBy': 'user3'
        }

        # Act
        task = Task.from_api(data, users)

        # Assert
        assert task.assigned_to is not None
        assert task.assigned_to.realname == '执行者'
        assert task.opened_by is not None
        assert task.opened_by.realname == '创建者'
        assert task.finished_by is not None
        assert task.finished_by.realname == '完成者'

    def test_task_from_api_with_dates(self):
        """测试从 API 响应创建任务（带日期）"""
        # Arrange
        data = {
            'id': 999,
            'name': '带日期的任务',
            'status': 'done',
            'pri': 2,
            'type': 'devel',
            'openedDate': '2024-03-15T09:00:00',
            'finishedDate': '2024-03-16T18:00:00'
        }

        # Act
        task = Task.from_api(data)

        # Assert
        assert task.opened_date is not None
        assert task.finished_date is not None

    def test_task_to_dict(self):
        """测试任务转字典"""
        # Arrange
        task = Task(
            id=1,
            title="测试任务",
            status="doing",
            priority=2,
            type="devel",
            estimate=4.0,
            consumed=2.0,
            left=2.0,
            parent=100,
            story=200
        )

        # Act
        result = task.to_dict()

        # Assert
        assert result['id'] == 1
        assert result['title'] == "测试任务"
        assert result['status'] == "doing"
        assert result['priority'] == 2
        assert result['type'] == "devel"
        assert result['estimate'] == 4.0
        assert result['consumed'] == 2.0
        assert result['left'] == 2.0
        assert result['parent'] == 100
        assert result['story'] == 200

    def test_task_to_dict_with_users(self):
        """测试任务转字典（带用户）"""
        # Arrange
        assigned_user = User(id=1, account='user1', realname='执行者')
        opened_user = User(id=2, account='user2', realname='创建者')
        finished_user = User(id=3, account='user3', realname='完成者')
        task = Task(
            id=1,
            title="测试任务",
            status="done",
            priority=1,
            type="devel",
            assigned_to=assigned_user,
            opened_by=opened_user,
            finished_by=finished_user
        )

        # Act
        result = task.to_dict()

        # Assert
        assert result['assigned_to'] == '执行者'
        assert result['opened_by'] == '创建者'
        assert result['finished_by'] == '完成者'
