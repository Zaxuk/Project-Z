"""
禅道数据模型定义
实现防腐层，将禅道 API 原始数据转换为统一的领域模型
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class User:
    """用户模型"""
    id: int
    account: str
    realname: str
    email: Optional[str] = None
    avatar: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict) -> 'User':
        """从 API 响应创建用户对象"""
        return cls(
            id=data.get('id', 0),
            account=data.get('account', ''),
            realname=data.get('realname', ''),
            email=data.get('email'),
            avatar=data.get('avatar')
        )


@dataclass
class Story:
    """需求模型"""
    id: int
    title: str
    status: str
    priority: int
    assigned_to: Optional[User] = None
    opened_by: Optional[User] = None
    opened_date: Optional[datetime] = None
    assigned_date: Optional[datetime] = None
    estimate: Optional[float] = None
    description: Optional[str] = None
    module: Optional[str] = None
    product: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict, users: dict = None) -> 'Story':
        """从 API 响应创建需求对象"""
        users = users or {}

        # 解析用户
        assigned_to_user = None
        if data.get('assignedTo') and str(data.get('assignedTo')) in users:
            assigned_to_user = users[str(data.get('assignedTo'))]

        opened_by_user = None
        if data.get('openedBy') and str(data.get('openedBy')) in users:
            opened_by_user = users[str(data.get('openedBy'))]

        # 解析日期
        opened_date = None
        if data.get('openedDate'):
            try:
                opened_date = datetime.fromisoformat(data.get('openedDate'))
            except:
                pass

        assigned_date = None
        if data.get('assignedDate'):
            try:
                assigned_date = datetime.fromisoformat(data.get('assignedDate'))
            except:
                pass

        return cls(
            id=data.get('id', 0),
            title=data.get('title', ''),
            status=data.get('status', ''),
            priority=data.get('pri', 0),
            assigned_to=assigned_to_user,
            opened_by=opened_by_user,
            opened_date=opened_date,
            assigned_date=assigned_date,
            estimate=data.get('estimate'),
            description=data.get('spec'),
            module=data.get('module'),
            product=data.get('product')
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'status': self.status,
            'priority': self.priority,
            'assigned_to': self.assigned_to.realname if self.assigned_to else None,
            'opened_by': self.opened_by.realname if self.opened_by else None,
            'opened_date': self.opened_date.isoformat() if self.opened_date else None,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'estimate': self.estimate,
            'module': self.module,
            'product': self.product
        }


@dataclass
class Task:
    """任务模型"""
    id: int
    title: str
    status: str
    priority: int
    type: str
    assigned_to: Optional[User] = None
    opened_by: Optional[User] = None
    finished_by: Optional[User] = None
    opened_date: Optional[datetime] = None
    finished_date: Optional[datetime] = None
    estimate: Optional[float] = None
    consumed: Optional[float] = None
    left: Optional[float] = None
    parent: Optional[int] = None
    story: Optional[int] = None
    module: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict, users: dict = None) -> 'Task':
        """从 API 响应创建任务对象"""
        users = users or {}

        # 解析用户
        assigned_to_user = None
        if data.get('assignedTo') and str(data.get('assignedTo')) in users:
            assigned_to_user = users[str(data.get('assignedTo'))]

        opened_by_user = None
        if data.get('openedBy') and str(data.get('openedBy')) in users:
            opened_by_user = users[str(data.get('openedBy'))]

        finished_by_user = None
        if data.get('finishedBy') and str(data.get('finishedBy')) in users:
            finished_by_user = users[str(data.get('finishedBy'))]

        # 解析日期
        opened_date = None
        if data.get('openedDate'):
            try:
                opened_date = datetime.fromisoformat(data.get('openedDate'))
            except:
                pass

        finished_date = None
        if data.get('finishedDate'):
            try:
                finished_date = datetime.fromisoformat(data.get('finishedDate'))
            except:
                pass

        return cls(
            id=data.get('id', 0),
            title=data.get('name', ''),
            status=data.get('status', ''),
            priority=data.get('pri', 0),
            type=data.get('type', ''),
            assigned_to=assigned_to_user,
            opened_by=opened_by_user,
            finished_by=finished_by_user,
            opened_date=opened_date,
            finished_date=finished_date,
            estimate=data.get('estimate'),
            consumed=data.get('consumed'),
            left=data.get('left'),
            parent=data.get('parent'),
            story=data.get('story'),
            module=data.get('module'),
            description=data.get('desc')
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'status': self.status,
            'priority': self.priority,
            'type': self.type,
            'assigned_to': self.assigned_to.realname if self.assigned_to else None,
            'opened_by': self.opened_by.realname if self.opened_by else None,
            'finished_by': self.finished_by.realname if self.finished_by else None,
            'opened_date': self.opened_date.isoformat() if self.opened_date else None,
            'finished_date': self.finished_date.isoformat() if self.finished_date else None,
            'estimate': self.estimate,
            'consumed': self.consumed,
            'left': self.left,
            'parent': self.parent,
            'story': self.story,
            'module': self.module
        }


@dataclass
class TaskListResult:
    """任务列表查询结果"""
    tasks: List[Task]
    total: int
    page: int
    page_size: int

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'tasks': [task.to_dict() for task in self.tasks],
            'total': self.total,
            'page': self.page,
            'page_size': self.page_size
        }


@dataclass
class StoryListResult:
    """需求列表查询结果"""
    stories: List[Story]
    total: int
    page: int
    page_size: int

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'stories': [story.to_dict() for story in self.stories],
            'total': self.total,
            'page': self.page,
            'page_size': self.page_size
        }