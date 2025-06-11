"""
XML问题解析模块
解析AI发送的XML格式问题
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class QuestionOption:
    """选择题选项"""
    value: str
    text: str


@dataclass
class ParsedQuestion:
    """解析后的问题数据"""
    question_type: str  # 'qa' 或 'choice'
    title: str
    content: str
    options: Optional[List[QuestionOption]] = None


class QuestionParser:
    """问题解析器"""
    
    @staticmethod
    def parse_xml(xml_string: str) -> ParsedQuestion:
        """
        解析XML格式的问题
        
        Args:
            xml_string: XML格式的问题字符串
            
        Returns:
            ParsedQuestion: 解析后的问题对象
            
        Raises:
            ValueError: XML格式错误或缺少必要字段
        """
        try:
            root = ET.fromstring(xml_string.strip())
            
            # 检查根元素
            if root.tag != 'question':
                raise ValueError("根元素必须是 'question'")
            
            # 获取问题类型
            question_type = root.get('type')
            if not question_type:
                raise ValueError("缺少问题类型 'type' 属性")
            
            if question_type not in ['qa', 'choice']:
                raise ValueError("问题类型必须是 'qa' 或 'choice'")
            
            # 获取标题和内容
            title_elem = root.find('title')
            content_elem = root.find('content')
            
            if title_elem is None:
                raise ValueError("缺少 'title' 元素")
            if content_elem is None:
                raise ValueError("缺少 'content' 元素")
            
            title = title_elem.text or ""
            content = content_elem.text or ""
            
            # 解析选项（仅选择题需要）
            options = None
            if question_type == 'choice':
                options_elem = root.find('options')
                if options_elem is None:
                    raise ValueError("选择题必须包含 'options' 元素")
                
                options = []
                for option_elem in options_elem.findall('option'):
                    value = option_elem.get('value')
                    text = option_elem.text
                    
                    if not value:
                        raise ValueError("选项必须包含 'value' 属性")
                    if not text:
                        raise ValueError("选项必须包含文本内容")
                    
                    options.append(QuestionOption(value=value, text=text))
                
                if not options:
                    raise ValueError("选择题必须至少包含一个选项")
            
            return ParsedQuestion(
                question_type=question_type,
                title=title,
                content=content,
                options=options
            )
            
        except ET.ParseError as e:
            raise ValueError(f"XML解析错误: {e}")
        except Exception as e:
            raise ValueError(f"问题解析失败: {e}")
    
    @staticmethod
    def validate_question(question: ParsedQuestion) -> bool:
        """
        验证问题数据的完整性
        
        Args:
            question: 要验证的问题对象
            
        Returns:
            bool: 验证是否通过
        """
        if not question.title.strip():
            return False
        
        if not question.content.strip():
            return False
        
        if question.question_type == 'choice':
            if not question.options or len(question.options) == 0:
                return False
            
            for option in question.options:
                if not option.value.strip() or not option.text.strip():
                    return False
        
        return True


# 测试用例
if __name__ == "__main__":
    # 测试问答题
    qa_xml = """
    <question type="qa">
        <title>请输入你的想法</title>
        <content>你对这个功能有什么建议？</content>
    </question>
    """
    
    # 测试选择题
    choice_xml = """
    <question type="choice">
        <title>选择你喜欢的颜色</title>
        <content>请选择一个颜色：</content>
        <options>
            <option value="red">红色</option>
            <option value="blue">蓝色</option>
            <option value="green">绿色</option>
        </options>
    </question>
    """
    
    parser = QuestionParser()
    
    try:
        qa_question = parser.parse_xml(qa_xml)
        print("问答题解析成功:", qa_question)
        
        choice_question = parser.parse_xml(choice_xml)
        print("选择题解析成功:", choice_question)
        
    except ValueError as e:
        print("解析错误:", e) 