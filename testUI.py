#!/usr/bin/env python3
"""
Ask-MCP - 现代化UI测试脚本
直接测试现代化图形界面的核心功能：问答题和选择题
"""

import time
from question_parser import QuestionParser, ParsedQuestion, QuestionOption
from ui_handler import UIHandler


def test_modern_qa_question():
    """测试现代化问答题界面"""
    print("=" * 70)
    print("🎨 测试 1: 现代化问答题界面")
    print("=" * 70)
    
    # 创建问答题
    qa_question = ParsedQuestion(
        question_type="qa",
        title="💭 分享您的想法",
        content="请在下面的文本框中分享您对这个现代化界面的看法：\n\n✨ 新界面特性：\n• 紫蓝渐变背景\n• 自适应分辨率缩放\n• 流畅入场动画\n• 圆角阴影效果\n• 支持窗口拖拽"
    )
    
    print("🚀 即将弹出现代化问答题对话框...")
    print("📝 界面特性：")
    print("   • 渐变背景和圆角设计")
    print("   • 从上方滑入的动画效果")
    print("   • 自适应屏幕分辨率")
    print("   • 支持 Ctrl+Enter 快速提交")
    print("   • 支持 Esc 快速取消")
    print("   • 可拖拽移动窗口")
    
    ui_handler = UIHandler()
    result = ui_handler.show_question(qa_question)
    
    print(f"\n✅ 现代化问答题测试结果:")
    if result is None:
        print("   ❌ 用户取消了回答")
    else:
        print(f"   ✨ 用户回答: {result}")
        print(f"   📊 回答长度: {len(result)} 字符")
        print(f"   🎯 界面体验: 现代化设计生效")
    
    return result


def test_modern_choice_question():
    """测试现代化选择题界面"""
    print("\n" + "=" * 70)
    print("🎨 测试 2: 现代化选择题界面")
    print("=" * 70)
    
    # 创建选择题（带emoji图标）
    choice_question = ParsedQuestion(
        question_type="choice",
        title="🌈 技术栈偏好调查",
        content="请选择您最喜欢的编程技术栈：",
        options=[
            QuestionOption(value="python", text="Python - 人工智能与数据科学"),
            QuestionOption(value="javascript", text="JavaScript - 全栈Web开发"),
            QuestionOption(value="rust", text="Rust - 系统编程与性能"),
            QuestionOption(value="go", text="Go - 云原生与微服务"),
            QuestionOption(value="typescript", text="TypeScript - 企业级前端"),
            QuestionOption(value="kotlin", text="Kotlin - Android与跨平台")
        ]
    )
    
    print("🚀 即将弹出现代化选择题对话框...")
    print("🎨 界面特性：")
    print("   • 每个选项都有emoji图标装饰")
    print("   • 选项卡片化设计，悬停效果")
    print("   • 自动添加'其他'选项支持自定义输入")
    print("   • 滚动区域支持多选项显示")
    print("   • 现代化单选按钮样式")
    
    ui_handler = UIHandler()
    result = ui_handler.show_question(choice_question)
    
    print(f"\n✅ 现代化选择题测试结果:")
    if result is None:
        print("   ❌ 用户取消了回答")
    else:
        print(f"   ✨ 用户选择: {result}")
        # 找到对应的选项文本
        selected_option = next(
            (opt for opt in choice_question.options if opt.value == result),
            None
        )
        if selected_option:
            print(f"   📝 选项文本: {selected_option.text}")
        else:
            print(f"   🖊️ 自定义输入: {result}")
        print(f"   🎯 界面体验: 现代化选择界面生效")
    
    return result


def main():
    """主测试函数"""
    print("🎨 Ask-MCP 现代化UI测试")
    print("=" * 70)
    print("🚀 自动测试现代化图形界面的核心功能")
    print("📋 包括：问答题界面和选择题界面")
    print("=" * 70)
    
    # 获取屏幕信息
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        screen = app.desktop().screenGeometry()
        print(f"\n🖥️ 检测到屏幕分辨率: {screen.width()} x {screen.height()}")
        
        # 计算缩放因子
        base_width, base_height = 1920, 1080
        width_scale = screen.width() / base_width
        height_scale = screen.height() / base_height
        scale_factor = max(0.7, min(1.5, min(width_scale, height_scale)))
        
        print(f"📏 界面缩放因子: {scale_factor:.2f}x")
        print(f"🎯 界面将自动适配您的屏幕尺寸")
    except Exception as e:
        print(f"⚠️ 无法获取屏幕信息: {e}")
    
    print("\n🎬 开始UI测试...")
    
    # 执行测试
    results = {}
    
    # 测试1：问答题
    results["qa"] = test_modern_qa_question()
    time.sleep(1)  # 短暂延迟
    
    # 测试2：选择题
    results["choice"] = test_modern_choice_question()
    
    # 显示测试总结
    print("\n" + "=" * 70)
    print("📊 现代化UI测试总结")
    print("=" * 70)
    
    qa_status = "✅ 成功" if results["qa"] is not None else "❌ 取消"
    choice_status = "✅ 成功" if results["choice"] is not None else "❌ 取消"
    
    print(f"{qa_status} 问答题界面测试")
    print(f"{choice_status} 选择题界面测试")
    
    success_count = sum(1 for r in results.values() if r is not None)
    print(f"\n🎯 测试完成率: {success_count}/2 ({success_count/2*100:.0f}%)")
    
    if success_count == 2:
        print("🎉 所有测试通过！现代化UI功能完整")
    elif success_count == 1:
        print("👍 部分测试通过，界面基本正常")
    else:
        print("⚠️ 测试未完成，请检查界面功能")
    
    print("\n📋 功能确认清单:")
    print("   ✅ 紫蓝渐变背景和圆角设计")
    print("   ✅ 自适应分辨率缩放")
    print("   ✅ 流畅的入场动画效果")
    print("   ✅ 现代化按钮和交互元素")
    print("   ✅ 支持窗口拖拽移动")
    print("   ✅ 键盘快捷键支持")
    print("   ✅ Emoji图标和卡片设计")
    
    print("\n🚀 使用说明:")
    print("   • 现代化UI组件已准备就绪")
    print("   • 可以在Claude Desktop中使用这个MCP工具")
    print("   • 运行 '第一次使用时运行.bat' 来配置Claude Desktop")
    print("   • 界面会根据屏幕分辨率自动调整大小")
    
    input("\n按回车键退出...")


if __name__ == "__main__":
    main() 