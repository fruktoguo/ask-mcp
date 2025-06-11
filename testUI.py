#!/usr/bin/env python3
"""
YuoMCP Interactive Query Tool - UI测试脚本
测试图形界面的弹出和数据返回功能
"""

import time
from question_parser import QuestionParser, ParsedQuestion, QuestionOption
from ui_handler import UIHandler


def test_qa_question():
    """测试问答题界面"""
    print("=" * 60)
    print("测试 1: 问答题界面")
    print("=" * 60)
    
    # 创建问答题
    qa_question = ParsedQuestion(
        question_type="qa",
        title="问答题测试",
        content="请在下面的文本框中输入你的想法或建议：\n\n这是一个测试问答题，你可以输入任何内容来测试界面功能。"
    )
    
    print("即将弹出问答题对话框...")
    print("请在对话框中输入一些测试文本，然后点击确定。")
    print("你也可以点击取消来测试取消功能。")
    
    ui_handler = UIHandler()
    result = ui_handler.show_question(qa_question)
    
    print(f"\n✓ 问答题测试结果:")
    if result is None:
        print("  用户取消了回答")
    else:
        print(f"  用户回答: {result}")
        print(f"  回答长度: {len(result)} 字符")
    
    return result


def test_choice_question():
    """测试选择题界面"""
    print("\n" + "=" * 60)
    print("测试 2: 选择题界面")
    print("=" * 60)
    
    # 创建选择题
    choice_question = ParsedQuestion(
        question_type="choice",
        title="选择题测试",
        content="请从以下选项中选择你最喜欢的编程语言：",
        options=[
            QuestionOption(value="python", text="Python - 简洁优雅"),
            QuestionOption(value="javascript", text="JavaScript - 无处不在"),
            QuestionOption(value="rust", text="Rust - 安全高效"),
            QuestionOption(value="go", text="Go - 简单快速"),
            QuestionOption(value="other", text="其他语言")
        ]
    )
    
    print("即将弹出选择题对话框...")
    print("请选择一个选项，然后点击确定。")
    print("你也可以点击取消来测试取消功能。")
    
    ui_handler = UIHandler()
    result = ui_handler.show_question(choice_question)
    
    print(f"\n✓ 选择题测试结果:")
    if result is None:
        print("  用户取消了回答")
    else:
        print(f"  用户选择: {result}")
        # 找到对应的选项文本
        selected_option = next(
            (opt for opt in choice_question.options if opt.value == result),
            None
        )
        if selected_option:
            print(f"  选项文本: {selected_option.text}")
    
    return result


def test_complex_choice_question():
    """测试复杂选择题界面"""
    print("\n" + "=" * 60)
    print("测试 3: 复杂选择题界面")
    print("=" * 60)
    
    # 创建复杂选择题
    complex_question = ParsedQuestion(
        question_type="choice",
        title="项目偏好调查",
        content="假设你要开始一个新的软件项目，你最看重以下哪个方面？\n\n请根据你的实际情况选择：",
        options=[
            QuestionOption(value="performance", text="性能优化 - 追求极致的运行效率"),
            QuestionOption(value="maintainability", text="可维护性 - 代码清晰易于维护"),
            QuestionOption(value="scalability", text="可扩展性 - 支持业务快速增长"),
            QuestionOption(value="security", text="安全性 - 保护数据和系统安全"),
            QuestionOption(value="usability", text="易用性 - 提供良好的用户体验"),
            QuestionOption(value="cost", text="成本控制 - 降低开发和运维成本")
        ]
    )
    
    print("即将弹出复杂选择题对话框...")
    print("这个对话框包含更多选项和更长的文本。")
    
    ui_handler = UIHandler()
    result = ui_handler.show_question(complex_question)
    
    print(f"\n✓ 复杂选择题测试结果:")
    if result is None:
        print("  用户取消了回答")
    else:
        print(f"  用户选择: {result}")
        selected_option = next(
            (opt for opt in complex_question.options if opt.value == result),
            None
        )
        if selected_option:
            print(f"  选项文本: {selected_option.text}")
    
    return result


def test_xml_parsing_and_ui():
    """测试XML解析和UI的完整流程"""
    print("\n" + "=" * 60)
    print("测试 4: XML解析 + UI完整流程")
    print("=" * 60)
    
    # 测试XML字符串
    xml_string = """
    <question type="choice">
        <title>开发工具偏好</title>
        <content>你平时最常用的代码编辑器是什么？</content>
        <options>
            <option value="vscode">Visual Studio Code</option>
            <option value="cursor">Cursor</option>
            <option value="pycharm">PyCharm</option>
            <option value="vim">Vim/Neovim</option>
            <option value="sublime">Sublime Text</option>
            <option value="other">其他</option>
        </options>
    </question>
    """
    
    print("测试XML解析...")
    parser = QuestionParser()
    
    try:
        question = parser.parse_xml(xml_string)
        print("✓ XML解析成功")
        print(f"  问题类型: {question.question_type}")
        print(f"  问题标题: {question.title}")
        print(f"  选项数量: {len(question.options) if question.options else 0}")
        
        # 验证问题
        if parser.validate_question(question):
            print("✓ 问题验证通过")
            
            print("\n即将弹出从XML解析的问题对话框...")
            ui_handler = UIHandler()
            result = ui_handler.show_question(question)
            
            print(f"\n✓ XML解析+UI测试结果:")
            if result is None:
                print("  用户取消了回答")
            else:
                print(f"  用户选择: {result}")
                selected_option = next(
                    (opt for opt in question.options if opt.value == result),
                    None
                )
                if selected_option:
                    print(f"  选项文本: {selected_option.text}")
            
            return result
        else:
            print("✗ 问题验证失败")
            return None
            
    except Exception as e:
        print(f"✗ XML解析失败: {e}")
        return None


def test_ui_responsiveness():
    """测试UI响应性"""
    print("\n" + "=" * 60)
    print("测试 5: UI响应性测试")
    print("=" * 60)
    
    print("这个测试将连续弹出3个简单对话框，测试UI的响应性...")
    
    ui_handler = UIHandler()
    results = []
    
    for i in range(3):
        question = ParsedQuestion(
            question_type="qa",
            title=f"响应性测试 {i+1}/3",
            content=f"这是第 {i+1} 个测试对话框。\n请输入任意内容或直接点击确定。"
        )
        
        print(f"\n弹出第 {i+1} 个对话框...")
        result = ui_handler.show_question(question)
        results.append(result)
        
        if result is None:
            print(f"  第 {i+1} 个对话框: 用户取消")
        else:
            print(f"  第 {i+1} 个对话框: 用户输入了 {len(result)} 字符")
    
    print(f"\n✓ UI响应性测试完成，共处理 {len(results)} 个对话框")
    return results


def main():
    """主测试函数"""
    print("YuoMCP Interactive Query Tool - UI测试")
    print("=" * 60)
    print("这个脚本将测试图形界面的各种功能")
    print("包括问答题、选择题、XML解析和UI响应性")
    print("=" * 60)
    
    # 询问用户要运行哪些测试
    print("\n可用的测试:")
    print("1. 问答题界面测试")
    print("2. 选择题界面测试") 
    print("3. 复杂选择题界面测试")
    print("4. XML解析+UI完整流程测试")
    print("5. UI响应性测试")
    print("6. 运行所有测试")
    
    choice = input("\n请选择要运行的测试 (1-6): ").strip()
    
    results = {}
    
    if choice == "1":
        results["qa"] = test_qa_question()
    elif choice == "2":
        results["choice"] = test_choice_question()
    elif choice == "3":
        results["complex"] = test_complex_choice_question()
    elif choice == "4":
        results["xml_ui"] = test_xml_parsing_and_ui()
    elif choice == "5":
        results["responsiveness"] = test_ui_responsiveness()
    elif choice == "6":
        print("\n开始运行所有测试...")
        results["qa"] = test_qa_question()
        time.sleep(1)  # 短暂延迟
        results["choice"] = test_choice_question()
        time.sleep(1)
        results["complex"] = test_complex_choice_question()
        time.sleep(1)
        results["xml_ui"] = test_xml_parsing_and_ui()
        time.sleep(1)
        results["responsiveness"] = test_ui_responsiveness()
    else:
        print("无效的选择，退出测试。")
        return
    
    # 显示测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, result in results.items():
        if test_name == "responsiveness":
            success_count = sum(1 for r in result if r is not None)
            print(f"✓ {test_name}: {success_count}/{len(result)} 个对话框成功")
        else:
            status = "成功" if result is not None else "取消"
            print(f"✓ {test_name}: {status}")
    
    print("\n测试完成！")
    print("\n使用说明:")
    print("- 如果所有测试都正常工作，说明UI组件功能正常")
    print("- 你可以在Cursor中使用这个MCP工具了")
    print("- 运行 install_to_cursor.bat 或 install_to_cursor.py 来配置Cursor")
    
    input("\n按回车键退出...")


if __name__ == "__main__":
    main() 