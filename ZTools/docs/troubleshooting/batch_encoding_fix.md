# 批处理文件中文编码问题解决方案

## 问题描述

在 Windows 环境下创建包含中文的批处理文件（.bat）时，遇到以下问题：

1. **编码问题**：直接写入中文会导致文件被错误解析
2. **换行符丢失**：所有内容显示在同一行
3. **`>` 符号被错误解析**：如 `chcp 65001 >nul` 被拆分解析
4. **命令找不到错误**：如 `'65001' 不是内部或外部命令`

## 问题原因

1. 批处理文件需要特定的编码（GBK 或 UTF-8）
2. 批处理文件需要 Windows 风格的换行符（CRLF）
3. 在 IDE/Terminal 环境中写入文件时，编码处理不当导致问题

## 解决方案

### 方法：使用 Python 脚本生成批处理文件

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

content = """@echo off\r
cd /d "%~dp0"\r
chcp 65001 >nul\r
title ZenTao Helper - 禅道自动化工具\r
python zentao-tools.py\r
pause\r
"""

with open('zentao-tools.bat', 'wb') as f:
    f.write(content.encode('utf-8'))

print("Done - created zentao-tools.bat")
```

### 关键点

1. **使用 `\r` 显式添加回车符**（CRLF 换行）
2. **使用 `wb` 二进制模式写入**，避免编码转换问题
3. **`chcp 65001 >nul`** 设置 UTF-8 编码
4. **`cd /d "%~dp0"`** 确保在批处理文件所在目录执行

## 经验总结

1. **不要直接在 IDE 中编辑批处理文件的中文内容**
2. **使用 Python 脚本生成批处理文件**，确保编码正确
3. **显式使用 `\r\n` 或 `\r` 处理换行符**
4. **使用二进制写入模式** `wb` 避免编码问题
5. **生成后测试**，确保双击能正常运行

## 备选方案

如果批处理文件编码问题无法解决，可以：

1. **使用 Python 脚本替代批处理文件**（如 `zentao-tools.py`）
2. **批处理文件只负责调用 Python 脚本**

```batch
@echo off
cd /d "%~dp0"
python zentao-tools.py
pause
```
