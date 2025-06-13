#!/usr/bin/env python3
"""
Ask-MCP - 基于FastMCP的实现
允许AI在对话中动态询问用户问题的MCP工具
"""

import asyncio
import threading
from typing import Optional
from fastmcp import FastMCP
from question_parser import QuestionParser, ParsedQuestion
from ui_handler import UIHandler


# 创建FastMCP服务器实例
mcp = FastMCP(
    name="Ask-MCP",
    instructions="这是一个交互式查询工具，允许AI在对话中动态询问用户问题。支持问答题和选择题两种类型。"
)

# 初始化组件
question_parser = QuestionParser()
ui_handler = UIHandler()


@mcp.tool()
def ask_user_question(question_xml: str) -> str:
    """
    向用户询问问题并获取回答。支持问答题和选择题两种类型。
    
    Args:
        question_xml: XML格式的问题。支持两种类型：
                     问答题格式：
                     <question type="qa">
                       <title>问题标题</title>
                       <content>问题内容</content>
                     </question>
                     
                     选择题格式：
                     <question type="choice">
                       <title>问题标题</title>
                       <content>问题内容</content>
                       <options>
                         <option value="value1">选项1</option>
                         <option value="value2">选项2</option>
                       </options>
                     </question>
    
    Returns:
        str: 用户的回答内容
    
    Raises:
        ValueError: 当XML格式错误或问题数据无效时
    """
    try:
        # 解析XML问题
        question = question_parser.parse_xml(question_xml)
        
        # 验证问题数据
        if not question_parser.validate_question(question):
            raise ValueError("问题数据验证失败，请检查问题内容是否完整。")
        
        # 在新线程中显示对话框（避免阻塞）
        result_container = {"answer": None, "error": None}
        
        def show_dialog():
            try:
                answer = ui_handler.show_question(question)
                result_container["answer"] = answer
            except Exception as e:
                result_container["error"] = str(e)
        
        # 创建并启动线程
        dialog_thread = threading.Thread(target=show_dialog)
        dialog_thread.start()
        dialog_thread.join()  # 等待用户回答
        
        # 检查是否有错误
        if result_container["error"]:
            raise ValueError(f"显示问题对话框时出错: {result_container['error']}")
        
        user_answer = result_container["answer"]
        
        if user_answer is None:
            return "用户取消了回答。"
        else:
            # 构建返回结果
            result_text = f"用户回答: {user_answer}"
            
            # 如果是选择题，还可以提供选项的文本描述
            if question.question_type == 'choice' and question.options:
                selected_option = next(
                    (opt for opt in question.options if opt.value == user_answer),
                    None
                )
                if selected_option:
                    result_text += f"\n选择的选项: {selected_option.text}"
            
            return result_text
            
    except ValueError as e:
        raise ValueError(f"XML解析错误: {e}")
    except Exception as e:
        raise ValueError(f"处理请求时出错: {e}")


@mcp.resource("examples://question-formats")
def get_question_examples() -> str:
    """提供问题格式的示例"""
    return """
# 问题格式示例

## 问答题格式
```xml
<question type="qa">
  <title>请输入你的想法</title>
  <content>你对这个功能有什么建议？</content>
</question>
```

## 选择题格式
```xml
<question type="choice">
  <title>选择你喜欢的颜色</title>
  <content>请选择一个颜色：</content>
  <options>
    <option value="red">红色</option>
    <option value="blue">蓝色</option>
    <option value="green">绿色</option>
  </options>
</question>
```

## 使用说明
1. 问答题允许用户输入自由文本
2. 选择题提供预定义选项供用户选择
3. 所有问题都会弹出图形界面窗口
4. 用户可以取消回答，此时工具会返回取消信息
"""


@mcp.prompt("create_question")
def create_question_prompt(question_type: str, title: str, content: str, options: str = "") -> str:
    """
    生成创建问题的XML格式提示
    
    Args:
        question_type: 问题类型 ('qa' 或 'choice')
        title: 问题标题
        content: 问题内容
        options: 选择题选项 (格式: "value1:文本1,value2:文本2")
    """
    if question_type == "qa":
        return f"""
<question type="qa">
  <title>{title}</title>
  <content>{content}</content>
</question>
"""
    elif question_type == "choice":
        options_xml = ""
        if options:
            for option in options.split(","):
                if ":" in option:
                    value, text = option.split(":", 1)
                    options_xml += f'    <option value="{value.strip()}">{text.strip()}</option>\n'
        
        return f"""
<question type="choice">
  <title>{title}</title>
  <content>{content}</content>
  <options>
{options_xml}  </options>
</question>
"""
    else:
        return "错误：问题类型必须是 'qa' 或 'choice'"


# 主函数
if __name__ == "__main__":
    print("启动 Ask-MCP")
    
    # 运行服务器
    mcp.run() 