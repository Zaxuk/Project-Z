# -*- coding: utf-8 -*-
"""
进度条工具模块
提供简单进度条和加载动画功能
"""

import sys
import time
import threading
from typing import Optional, Dict, Any


class ProgressBar:
    """
    简单进度条实现
    
    使用示例:
        with ProgressBar(total=100, desc="处理中") as pbar:
            for i in range(100):
                process_item(i)
                pbar.update(1)
                pbar.set_postfix(当前=i)
    """
    
    def __init__(self, total: Optional[int] = None, desc: str = "", unit: str = "项", 
                 bar_width: int = 30, file=sys.stdout):
        """
        初始化进度条
        
        Args:
            total: 总进度（None表示不确定进度）
            desc: 描述文本
            unit: 单位名称
            bar_width: 进度条宽度
            file: 输出流
        """
        self.total = total
        self.desc = desc
        self.unit = unit
        self.bar_width = bar_width
        self.file = file
        self.current = 0
        self.start_time = None
        self.postfix: Dict[str, Any] = {}
        self._closed = False
        
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        
    def start(self):
        """开始进度条"""
        self.start_time = time.time()
        self._print_progress()
        
    def update(self, n: int = 1):
        """
        更新进度
        
        Args:
            n: 增加的进度值
        """
        self.current += n
        self._print_progress()
        
    def set_postfix(self, **kwargs):
        """
        设置后缀信息
        
        Args:
            **kwargs: 键值对形式的后缀信息
        """
        self.postfix.update(kwargs)
        self._print_progress()
        
    def close(self):
        """关闭进度条"""
        if not self._closed:
            self._closed = True
            self.file.write("\n")
            self.file.flush()
            
    def _print_progress(self):
        """打印进度条"""
        if self._closed:
            return
            
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        # 构建进度条字符串
        if self.total:
            # 确定进度
            percent = min(100, int(100 * self.current / self.total))
            filled = int(self.bar_width * self.current / self.total)
            bar = "█" * filled + "░" * (self.bar_width - filled)
            
            # 计算预计剩余时间
            if self.current > 0:
                eta = elapsed * (self.total - self.current) / self.current
                eta_str = self._format_time(eta)
            else:
                eta_str = "??:??"
                
            progress_str = f"\r{self.desc}: {percent}%|{bar}| {self.current}/{self.total} [{self._format_time(elapsed)}<{eta_str}]"
        else:
            # 不确定进度
            spinner = self._get_spinner()
            progress_str = f"\r{self.desc}... {spinner} [{self.current} {self.unit}]"
            
        # 添加后缀信息
        if self.postfix:
            postfix_str = ", ".join(f"{k}={v}" for k, v in self.postfix.items())
            progress_str += f", {postfix_str}"
            
        self.file.write(progress_str)
        self.file.flush()
        
    def _format_time(self, seconds: float) -> str:
        """格式化时间"""
        if seconds < 60:
            return f"{int(seconds):02d}s"
        elif seconds < 3600:
            return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}:{minutes:02d}:{int(seconds % 60):02d}"
            
    def _get_spinner(self) -> str:
        """获取旋转动画字符"""
        spinners = ["◐", "◓", "◑", "◒"]
        idx = int(time.time() * 10) % len(spinners)
        return spinners[idx]


class Spinner:
    """
    加载动画（用于不确定进度的场景）
    
    使用示例:
        spinner = Spinner("正在加载")
        spinner.start()
        try:
            result = long_operation()
            spinner.succeed("加载完成")
        except Exception as e:
            spinner.fail(f"加载失败: {e}")
            raise
    """
    
    def __init__(self, desc: str = "加载中", file=sys.stdout):
        """
        初始化加载动画
        
        Args:
            desc: 描述文本
            file: 输出流
        """
        self.desc = desc
        self.file = file
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._start_time = None
        
    def start(self):
        """开始加载动画"""
        if self._running:
            return
            
        self._running = True
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._animate)
        self._thread.daemon = True
        self._thread.start()
        
    def stop(self, message: Optional[str] = None, success: bool = True):
        """
        停止加载动画
        
        Args:
            message: 停止时显示的消息
            success: 是否成功完成
        """
        if not self._running:
            return
            
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.1)
            
        # 清除当前行
        self.file.write("\r" + " " * 80 + "\r")
        
        # 显示结果
        icon = "✓" if success else "✗"
        msg = message or ("完成" if success else "失败")
        elapsed = time.time() - self._start_time if self._start_time else 0
        
        self.file.write(f"{icon} {self.desc}: {msg} [{self._format_time(elapsed)}]\n")
        self.file.flush()
        
    def succeed(self, message: Optional[str] = None):
        """标记为成功完成"""
        self.stop(message, success=True)
        
    def fail(self, message: Optional[str] = None):
        """标记为失败"""
        self.stop(message, success=False)
        
    def _animate(self):
        """动画循环"""
        spinners = ["◐", "◓", "◑", "◒"]
        idx = 0
        
        while self._running:
            elapsed = time.time() - self._start_time if self._start_time else 0
            spinner = spinners[idx % len(spinners)]
            
            self.file.write(f"\r{spinner} {self.desc}... [{self._format_time(elapsed)}]")
            self.file.flush()
            
            idx += 1
            time.sleep(0.1)
            
    def _format_time(self, seconds: float) -> str:
        """格式化时间"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m{int(seconds % 60)}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h{minutes}m"


class DummyProgressBar:
    """
    虚拟进度条（用于禁用进度条时的回退）
    
    提供与 ProgressBar 相同的接口，但不做任何操作
    """
    
    def __init__(self, *args, **kwargs):
        pass
        
    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        pass
        
    def start(self):
        pass
        
    def update(self, n: int = 1):
        pass
        
    def set_postfix(self, **kwargs):
        pass
        
    def close(self):
        pass


class DummySpinner:
    """
    虚拟加载动画（用于禁用进度条时的回退）
    """
    
    def __init__(self, *args, **kwargs):
        pass
        
    def start(self):
        pass
        
    def stop(self, message: Optional[str] = None, success: bool = True):
        pass
        
    def succeed(self, message: Optional[str] = None):
        pass
        
    def fail(self, message: Optional[str] = None):
        pass


def get_progress_bar(enabled: bool = True, **kwargs) -> ProgressBar:
    """
    获取进度条实例
    
    Args:
        enabled: 是否启用进度条
        **kwargs: 传递给 ProgressBar 的参数
        
    Returns:
        ProgressBar 或 DummyProgressBar 实例
    """
    if enabled:
        return ProgressBar(**kwargs)
    else:
        return DummyProgressBar(**kwargs)


def get_spinner(enabled: bool = True, **kwargs) -> Spinner:
    """
    获取加载动画实例
    
    Args:
        enabled: 是否启用加载动画
        **kwargs: 传递给 Spinner 的参数
        
    Returns:
        Spinner 或 DummySpinner 实例
    """
    if enabled:
        return Spinner(**kwargs)
    else:
        return DummySpinner(**kwargs)
