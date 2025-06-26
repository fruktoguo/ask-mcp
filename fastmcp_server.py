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
    向用户询问问题并获取回答。支持问答题和选择题两种类型，支持图片粘贴和拖拽。
    
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
        str: 用户的回答内容。如果包含图片，会返回包含文本和图片数据的详细信息。
             图片数据遵循MCP协议格式，使用base64编码。
    
    Features:
        - 支持文本输入和图片粘贴/拖拽
        - 图片格式：PNG, JPG, GIF等常见格式
        - 图片数据按MCP协议格式编码（base64）
        - 支持Ctrl+V粘贴剪贴板图片
        - 支持拖拽图片文件到输入框
    
    Raises:
        ValueError: 当XML格式错误或问题数据无效时
    """
    try:
        # 解析XML问题
        try:
            question = question_parser.parse_xml(question_xml)
        except Exception as e:
            return f"❌ XML解析失败: {str(e)}\n\n请检查XML格式是否正确。\n\n提供的XML:\n{question_xml}"
        
        # 验证问题数据
        if not question_parser.validate_question(question):
            return f"❌ 问题数据验证失败，请检查问题内容是否完整。\n\n解析结果:\n- 类型: {question.question_type}\n- 标题: {question.title}\n- 内容: {question.content}\n- 选项数量: {len(question.options) if question.options else 0}"
        
        # 在新线程中显示对话框（避免阻塞）
        result_container = {"answer": None, "error": None, "cancelled": False}
        
        def show_dialog():
            try:
                answer = ui_handler.show_question(question)
                if answer is None:
                    result_container["error"] = "[THREAD]线程中收到None结果，这不应该发生"
                elif isinstance(answer, str) and answer.startswith("CANCELLED:"):
                    result_container["cancelled"] = True
                    result_container["cancel_reason"] = answer.replace("CANCELLED:", "")
                elif isinstance(answer, str) and answer.startswith("ERROR:"):
                    result_container["error"] = answer.replace("ERROR:", "")
                else:
                    result_container["answer"] = answer
            except Exception as e:
                result_container["error"] = f"[THREAD]线程异常: {str(e)}"
        
        # 创建并启动线程
        dialog_thread = threading.Thread(target=show_dialog)
        dialog_thread.start()
        dialog_thread.join()  # 等待用户回答
        
        # 检查是否有错误
        if result_container["error"]:
            return f"❌ 显示问题对话框时出错: {result_container['error']}"
        
        # 检查是否被用户主动取消
        if result_container["cancelled"]:
            cancel_reason = result_container.get("cancel_reason", "[UNKNOWN]未知的取消原因")
            return f"⚠️ 用户取消了回答。详细原因: {cancel_reason}"
        
        user_answer = result_container["answer"]
        
        # 检查是否有有效答案
        if user_answer is None:
            return "❌ 程序错误: 结果容器中answer为None，但没有错误或取消标记"
        else:
            # 处理包含图片的回答
            if isinstance(user_answer, dict) and ('text' in user_answer or 'images' in user_answer):
                # 包含图片的结构化回答
                result_parts = []
                
                # 文本部分
                text_content = user_answer.get('text', '').strip()
                if text_content:
                    result_parts.append(f"用户回答: {text_content}")
                
                # 图片部分
                images = user_answer.get('images', [])
                if images:
                    result_parts.append(f"用户提供了 {len(images)} 张图片:")
                    
                    for i, image in enumerate(images, 1):
                        image_info = f"图片 {i}: {image.get('mimeType', 'unknown')} "
                        image_info += f"(大小: {len(image.get('data', ''))} 字符的base64数据)"
                        result_parts.append(image_info)
                        
                        # 将图片数据作为MCP协议格式返回给AI
                        # AI可以读取这些base64编码的图片数据
                        result_parts.append(f"图片 {i} 数据 (MCP格式): {image}")
                
                # 如果是选择题的自定义选项
                if question.question_type == 'choice':
                    result_parts.append("这是选择题的自定义选项回答。")
                
                return "\n".join(result_parts)
            else:
                # 传统的文本回答
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
        return f"❌ 参数错误: {str(e)}"
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"❌ 处理请求时出现未预期的错误: {str(e)}\n\n详细错误信息:\n{error_details}"


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

## 图片支持功能
- **粘贴图片**: 用户可以通过Ctrl+V粘贴剪贴板中的图片
- **拖拽图片**: 用户可以直接拖拽图片文件到输入框
- **支持格式**: PNG, JPG, GIF, BMP等常见图片格式
- **MCP协议**: 图片数据按照MCP协议格式进行base64编码

## 图片数据格式
当用户提供图片时，返回的数据格式为：
```json
{
  "text": "用户输入的文本",
  "images": [
    {
      "type": "image",
      "data": "base64编码的图片数据",
      "mimeType": "image/png"
    }
  ]
}
```

## 使用说明
1. 问答题允许用户输入自由文本和图片
2. 选择题提供预定义选项，"其他"选项支持文本和图片
3. 所有问题都会弹出现代化图形界面窗口
4. 用户可以取消回答，此时工具会返回取消信息
5. 图片会以占位符形式在文本中显示，实际数据以MCP格式传输
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