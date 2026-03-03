# -*- coding: utf-8 -*-
"""ZenTao Helper - 禅道自动化工具 (Python版本)"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from skill import ZenTaoHelperSkill


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_menu():
    """显示主菜单"""
    clear_screen()
    print()
    print("=" * 43)
    print("  ZenTao Helper - 禅道自动化工具")
    print("=" * 43)
    print()
    print("  [1] 交互式拆解需求")
    print("  [2] 查看我的需求")
    print("  [3] 查看未分配的需求")
    print("  [4] 查看我的任务")
    print("  [5] 重新登录")
    print("  [0] 退出")
    print()
    print("=" * 43)
    print()


def split_story_interactive(skill):
    """交互式拆解需求"""
    print()
    print("=" * 43)
    print("  交互式拆解需求")
    print("=" * 43)
    print()
    print("提示: 输入 b 或 B 可返回主菜单")
    print()

    # 输入需求ID
    while True:
        story_id = input("请输入需求ID (输入 b 返回): ").strip()
        if story_id.lower() == 'b':
            return
        if story_id:
            break

    # 输入需求等级
    print()
    print("请选择需求等级 (默认: A+):")
    print("  1. A-")
    print("  2. A")
    print("  3. A+ (默认)")
    print("  4. A++")
    print("  5. B")
    print("  b. 返回上一步")
    while True:
        grade_choice = input("选择 (1-5/b, 直接回车=A+): ").strip()
        if grade_choice.lower() == 'b':
            return split_story_interactive(skill)
        if not grade_choice or grade_choice == '1':
            grade = 'A-'
        elif grade_choice == '2':
            grade = 'A'
        elif grade_choice == '3':
            grade = 'A+'
        elif grade_choice == '4':
            grade = 'A++'
        elif grade_choice == '5':
            grade = 'B'
        else:
            print("无效选择，请重新输入")
            continue
        break

    # 输入优先级
    print()
    print("是否紧急 (默认: 否):")
    print("  1. 否 (默认)")
    print("  2. 是")
    print("  b. 返回上一步")
    while True:
        priority_choice = input("选择 (1-2/b, 直接回车=否): ").strip()
        if priority_choice.lower() == 'b':
            return split_story_interactive(skill)
        if not priority_choice or priority_choice == '1':
            priority = '非紧急'
        elif priority_choice == '2':
            priority = '紧急'
        else:
            print("无效选择，请重新输入")
            continue
        break

    # 输入上线时间
    print()
    print("请选择需求上线时间 (默认: 下下周周一):")
    print("  1. 下周周一")
    print("  2. 下周周四")
    print("  3. 下下周周一 (默认)")
    print("  4. 下下周周四")
    print("  b. 返回上一步")
    while True:
        online_choice = input("选择 (1-4/b, 直接回车=下下周周一): ").strip()
        if online_choice.lower() == 'b':
            return split_story_interactive(skill)
        if not online_choice or online_choice == '1':
            online_time = '下周周一'
        elif online_choice == '2':
            online_time = '下周周四'
        elif online_choice == '3':
            online_time = '下下周周一'
        elif online_choice == '4':
            online_time = '下下周周四'
        else:
            print("无效选择，请重新输入")
            continue
        break

    # 输入执行人
    print()
    assigned_to = input("请输入任务执行人 (默认: zhuxu, 输入 b 返回): ").strip()
    if assigned_to.lower() == 'b':
        return split_story_interactive(skill)
    if not assigned_to:
        assigned_to = 'zhuxu'

    # 输入任务时长
    print()
    while True:
        hours = input("请输入任务时长/小时 (默认: 8, 输入 b 返回): ").strip()
        if hours.lower() == 'b':
            return split_story_interactive(skill)
        if not hours:
            hours = '8'
        break

    # 输入截止时间
    print()
    print("请选择截止时间 (默认: 本周周五):")
    print("  1. 本周周五 (默认)")
    print("  2. 下周周五")
    print("  b. 返回上一步")
    while True:
        deadline_choice = input("选择 (1-2/b, 直接回车=本周周五): ").strip()
        if deadline_choice.lower() == 'b':
            return split_story_interactive(skill)
        if not deadline_choice or deadline_choice == '1':
            deadline = '本周周五'
        elif deadline_choice == '2':
            deadline = '下周周五'
        else:
            print("无效选择，请重新输入")
            continue
        break

    # 确认信息
    print()
    print("=" * 43)
    print("  确认信息")
    print("=" * 43)
    print(f"  需求ID: {story_id}")
    print(f"  需求等级: {grade}")
    print(f"  是否紧急: {priority}")
    print(f"  上线时间: {online_time}")
    print(f"  执行人: {assigned_to}")
    print(f"  任务时长: {hours} 小时")
    print(f"  截止时间: {deadline}")
    print("=" * 43)
    print()
    print("  [Y] 确认执行")
    print("  [N] 取消并返回主菜单")
    print("  [B] 返回修改")
    print()

    while True:
        confirm = input("请选择 (Y/N/B): ").strip().upper()
        if confirm == 'Y':
            # 执行拆解
            print()
            print(f"正在拆解需求 #{story_id}...")
            print()
            result = skill.execute(
                f'拆解需求#{story_id}',
                grade=grade,
                priority=priority,
                online_time=online_time,
                assigned_to=assigned_to,
                task_hours=int(hours),
                deadline=deadline
            )
            print(result.get('message', '执行完成'))
            break
        elif confirm == 'N':
            return
        elif confirm == 'B':
            return split_story_interactive(skill)
        else:
            print("无效选择，请重新输入")

    input("\n按回车键继续...")


def query_my_stories(skill):
    """查看我的需求"""
    print()
    print("正在查询我的需求...")
    print()
    result = skill.execute('查看我的需求')
    print(result.get('data', {}).get('message', '执行完成'))
    input("\n按回车键继续...")


def query_unassigned_stories(skill):
    """查看未分配的需求"""
    print()
    print("正在查询未分配的需求...")
    print()
    result = skill.execute('查看未分配的需求')
    print(result.get('data', {}).get('message', '执行完成'))
    input("\n按回车键继续...")


def query_my_tasks(skill):
    """查看我的任务"""
    print()
    print("正在查询我的任务...")
    print()
    result = skill.execute('查看我的任务')
    print(result.get('data', {}).get('message', '执行完成'))
    input("\n按回车键继续...")


def relogin(skill):
    """重新登录"""
    print()
    print("正在重新登录...")
    print()
    result = skill.execute('登录禅道')
    print(result.get('message', '执行完成'))
    input("\n按回车键继续...")


def main():
    """主函数"""
    skill = ZenTaoHelperSkill()

    while True:
        show_menu()
        choice = input("请选择操作 (0-5): ").strip()

        if choice == '1':
            split_story_interactive(skill)
        elif choice == '2':
            query_my_stories(skill)
        elif choice == '3':
            query_unassigned_stories(skill)
        elif choice == '4':
            query_my_tasks(skill)
        elif choice == '5':
            relogin(skill)
        elif choice == '0':
            print()
            print("感谢使用 ZenTao Helper!")
            print()
            break
        else:
            print("无效选择，请重新输入")
            input("\n按回车键继续...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n错误: {e}")
        input("\n按回车键退出...")
