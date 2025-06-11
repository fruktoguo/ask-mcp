"""
图形界面处理模块
使用tkinter创建macOS风格的现代化弹出窗口供用户回答问题
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import asyncio
from typing import Optional, Any
from question_parser import ParsedQuestion, QuestionOption


class MacOSQuestionDialog:
    """macOS风格现代化问题对话框类"""
    
    # macOS风格配色方案
    COLORS = {
        'bg': '#F5F5F7',           # macOS浅灰背景
        'card_bg': '#FFFFFF',      # 纯白卡片背景
        'primary': '#007AFF',      # iOS蓝色
        'primary_hover': '#0051D5', # 蓝色悬停
        'secondary': '#8E8E93',    # 系统灰色
        'text': '#1D1D1F',         # 主文本颜色
        'text_secondary': '#86868B', # 次要文本
        'border': '#D2D2D7',       # 边框颜色
        'success': '#30D158',      # 系统绿色
        'warning': '#FF9F0A',      # 系统橙色
        'danger': '#FF3B30',       # 系统红色
        'shadow': '#00000010',     # 阴影颜色
    }
    
    def __init__(self, question: ParsedQuestion):
        self.question = question
        self.result = None
        self.root = None
        self.completed = threading.Event()
        self.choice_var = None
        self.custom_entry = None
        self.text_widget = None
        
    def show_dialog(self) -> Optional[str]:
        """
        显示macOS风格对话框并等待用户回答
        
        Returns:
            Optional[str]: 用户的回答，如果取消则返回None
        """
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("")  # 移除标题栏文字
        self.root.configure(bg=self.COLORS['bg'])
        
        # 设置窗口样式
        self._setup_macos_window()
        
        # 创建macOS风格界面
        self._create_macos_widgets()
        
        # 绑定事件
        self._bind_events()
        
        # 运行GUI主循环
        self.root.mainloop()
        
        return self.result
    
    def _setup_macos_window(self):
        """设置macOS风格窗口"""
        # 设置窗口大小
        if self.question.question_type == 'choice':
            self.root.geometry("520x580")
        else:
            self.root.geometry("520x480")
        
        self.root.resizable(False, False)  # macOS对话框通常不可调整大小
        
        # 居中显示
        self._center_window()
        
        # 设置窗口属性
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        
        # 尝试设置macOS样式（如果支持）
        try:
            # 移除标题栏装饰
            self.root.overrideredirect(False)
            # 设置窗口样式
            self.root.configure(relief='flat', bd=0)
        except:
            pass
    
    def _center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def _create_macos_widgets(self):
        """创建macOS风格界面组件"""
        # 主容器（带圆角效果的模拟）
        main_container = tk.Frame(self.root, bg=self.COLORS['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # 内容卡片（模拟圆角和阴影）
        content_card = tk.Frame(
            main_container, 
            bg=self.COLORS['card_bg'],
            relief='flat',
            bd=0
        )
        content_card.pack(fill=tk.BOTH, expand=True)
        
        # 添加视觉边框效果
        border_frame = tk.Frame(
            content_card,
            bg=self.COLORS['border'],
            height=1
        )
        border_frame.pack(fill=tk.X, side=tk.TOP)
        
        # 内容区域
        content_area = tk.Frame(content_card, bg=self.COLORS['card_bg'])
        content_area.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)
        
        # 标题区域
        self._create_macos_title_section(content_area)
        
        # 内容区域
        self._create_macos_content_section(content_area)
        
        # 输入区域
        if self.question.question_type == 'qa':
            self._create_macos_qa_section(content_area)
        elif self.question.question_type == 'choice':
            self._create_macos_choice_section(content_area)
        
        # 按钮区域
        self._create_macos_button_section(content_area)
    
    def _create_macos_title_section(self, parent):
        """创建macOS风格标题区域"""
        title_frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        title_frame.pack(fill=tk.X, pady=(0, 16))
        
        title_label = tk.Label(
            title_frame,
            text=self.question.title,
            font=('SF Pro Display', 20, 'bold'),  # macOS系统字体
            fg=self.COLORS['text'],
            bg=self.COLORS['card_bg'],
            wraplength=450,
            justify=tk.CENTER
        )
        title_label.pack()
    
    def _create_macos_content_section(self, parent):
        """创建macOS风格内容区域"""
        if self.question.content:
            content_frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
            content_frame.pack(fill=tk.X, pady=(0, 24))
            
            content_label = tk.Label(
                content_frame,
                text=self.question.content,
                font=('SF Pro Text', 14),
                fg=self.COLORS['text_secondary'],
                bg=self.COLORS['card_bg'],
                wraplength=450,
                justify=tk.CENTER
            )
            content_label.pack()
    
    def _create_macos_qa_section(self, parent):
        """创建macOS风格问答题输入区域"""
        qa_frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        qa_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 24))
        
        # 文本输入框容器（模拟macOS圆角输入框）
        text_container = tk.Frame(
            qa_frame, 
            bg=self.COLORS['bg'], 
            relief='solid', 
            bd=1,
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        text_container.pack(fill=tk.BOTH, expand=True)
        
        # 文本输入框
        self.text_widget = tk.Text(
            text_container,
            font=('SF Pro Text', 14),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text'],
            relief='flat',
            bd=12,
            wrap=tk.WORD,
            selectbackground=self.COLORS['primary'],
            selectforeground='white',
            insertbackground=self.COLORS['primary'],
            insertwidth=2
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 焦点效果
        def on_focus_in(event):
            text_container.configure(highlightbackground=self.COLORS['primary'])
        
        def on_focus_out(event):
            text_container.configure(highlightbackground=self.COLORS['border'])
        
        self.text_widget.bind('<FocusIn>', on_focus_in)
        self.text_widget.bind('<FocusOut>', on_focus_out)
        self.text_widget.focus_set()
    
    def _create_macos_choice_section(self, parent):
        """创建macOS风格选择题区域"""
        choice_frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        choice_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 24))
        
        # 选项容器
        options_container = tk.Frame(choice_frame, bg=self.COLORS['card_bg'])
        options_container.pack(fill=tk.X)
        
        # 单选按钮变量
        self.choice_var = tk.StringVar()
        
        # 创建原有选项
        for i, option in enumerate(self.question.options):
            self._create_macos_option_button(options_container, option.text, option.value, i)
        
        # 自动添加"其他"选项
        other_index = len(self.question.options)
        self._create_macos_other_option(options_container, other_index)
        
        # 默认选择第一个选项
        if self.question.options:
            self.choice_var.set(self.question.options[0].value)
    
    def _create_macos_option_button(self, parent, text, value, index):
        """创建macOS风格选项按钮"""
        # 选项容器（模拟macOS列表项）
        option_container = tk.Frame(
            parent, 
            bg=self.COLORS['card_bg'],
            relief='flat',
            bd=0
        )
        option_container.pack(fill=tk.X, pady=2)
        
        # 选项内容框架
        option_frame = tk.Frame(
            option_container,
            bg=self.COLORS['bg'],
            relief='flat',
            bd=0
        )
        option_frame.pack(fill=tk.X, padx=4, pady=4)
        
        # 单选按钮
        radio_button = tk.Radiobutton(
            option_frame,
            text=text,
            variable=self.choice_var,
            value=value,
            font=('SF Pro Text', 14),
            fg=self.COLORS['text'],
            bg=self.COLORS['bg'],
            activebackground=self.COLORS['bg'],
            activeforeground=self.COLORS['primary'],
            selectcolor=self.COLORS['primary'],
            relief='flat',
            bd=0,
            padx=16,
            pady=12,
            wraplength=400,
            justify=tk.LEFT,
            anchor='w'
        )
        radio_button.pack(fill=tk.X)
        
        # macOS风格悬停效果
        def on_enter(e):
            option_frame.configure(bg=self.COLORS['border'])
            radio_button.configure(bg=self.COLORS['border'])
        
        def on_leave(e):
            option_frame.configure(bg=self.COLORS['bg'])
            radio_button.configure(bg=self.COLORS['bg'])
        
        option_frame.bind("<Enter>", on_enter)
        option_frame.bind("<Leave>", on_leave)
        radio_button.bind("<Enter>", on_enter)
        radio_button.bind("<Leave>", on_leave)
    
    def _create_macos_other_option(self, parent, index):
        """创建macOS风格"其他"选项"""
        # "其他"选项容器
        other_container = tk.Frame(
            parent, 
            bg=self.COLORS['card_bg'],
            relief='flat',
            bd=0
        )
        other_container.pack(fill=tk.X, pady=2)
        
        # "其他"选项框架
        other_frame = tk.Frame(
            other_container,
            bg=self.COLORS['bg'],
            relief='flat',
            bd=0
        )
        other_frame.pack(fill=tk.X, padx=4, pady=4)
        
        # "其他"单选按钮
        other_radio = tk.Radiobutton(
            other_frame,
            text="其他",
            variable=self.choice_var,
            value="__custom__",
            font=('SF Pro Text', 14),
            fg=self.COLORS['text'],
            bg=self.COLORS['bg'],
            activebackground=self.COLORS['bg'],
            activeforeground=self.COLORS['primary'],
            selectcolor=self.COLORS['primary'],
            relief='flat',
            bd=0,
            padx=16,
            pady=8,
            command=self._on_other_selected
        )
        other_radio.pack(anchor=tk.W)
        
        # 自定义输入框容器
        custom_container = tk.Frame(
            other_frame,
            bg=self.COLORS['card_bg'],
            relief='solid',
            bd=1,
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        custom_container.pack(fill=tk.X, padx=16, pady=(4, 8))
        
        # 自定义输入框
        self.custom_entry = tk.Entry(
            custom_container,
            font=('SF Pro Text', 14),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text'],
            relief='flat',
            bd=8,
            selectbackground=self.COLORS['primary'],
            selectforeground='white',
            insertbackground=self.COLORS['primary'],
            insertwidth=2
        )
        self.custom_entry.pack(fill=tk.X)
        
        # 输入框焦点效果
        def on_entry_focus_in(event):
            custom_container.configure(highlightbackground=self.COLORS['primary'])
            self.choice_var.set("__custom__")
        
        def on_entry_focus_out(event):
            custom_container.configure(highlightbackground=self.COLORS['border'])
        
        self.custom_entry.bind('<FocusIn>', on_entry_focus_in)
        self.custom_entry.bind('<FocusOut>', on_entry_focus_out)
        self.custom_entry.bind('<KeyPress>', lambda e: self.choice_var.set("__custom__"))
        
        # 悬停效果
        def on_enter(e):
            other_frame.configure(bg=self.COLORS['border'])
            other_radio.configure(bg=self.COLORS['border'])
        
        def on_leave(e):
            other_frame.configure(bg=self.COLORS['bg'])
            other_radio.configure(bg=self.COLORS['bg'])
        
        other_frame.bind("<Enter>", on_enter)
        other_frame.bind("<Leave>", on_leave)
        other_radio.bind("<Enter>", on_enter)
        other_radio.bind("<Leave>", on_leave)
    
    def _on_other_selected(self):
        """当选择"其他"选项时，聚焦到输入框"""
        if self.custom_entry:
            self.custom_entry.focus_set()
    
    def _create_macos_button_section(self, parent):
        """创建macOS风格按钮区域"""
        button_frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        button_frame.pack(fill=tk.X, pady=(16, 0))
        
        # 按钮容器（居中对齐）
        button_container = tk.Frame(button_frame, bg=self.COLORS['card_bg'])
        button_container.pack()
        
        # 取消按钮（macOS次要按钮样式）
        cancel_btn = self._create_macos_button(
            button_container, 
            "取消", 
            self._on_cancel,
            style='secondary'
        )
        cancel_btn.pack(side=tk.LEFT, padx=(0, 12))
        
        # 确定按钮（macOS主要按钮样式）
        ok_btn = self._create_macos_button(
            button_container,
            "确定",
            self._on_ok,
            style='primary'
        )
        ok_btn.pack(side=tk.LEFT)
    
    def _create_macos_button(self, parent, text, command, style='primary'):
        """创建macOS风格按钮"""
        if style == 'primary':
            bg_color = self.COLORS['primary']
            hover_color = self.COLORS['primary_hover']
            text_color = 'white'
        else:
            bg_color = self.COLORS['bg']
            hover_color = self.COLORS['border']
            text_color = self.COLORS['text']
        
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=('SF Pro Text', 14, 'bold'),
            fg=text_color,
            bg=bg_color,
            activebackground=hover_color,
            activeforeground=text_color,
            relief='flat',
            bd=0,
            padx=24,
            pady=10,
            cursor='hand2',
            width=8
        )
        
        # macOS风格悬停效果
        def on_enter(e):
            button.configure(bg=hover_color)
        
        def on_leave(e):
            button.configure(bg=bg_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def _bind_events(self):
        """绑定键盘事件"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.bind('<Return>', lambda e: self._on_ok())
        self.root.bind('<Escape>', lambda e: self._on_cancel())
        self.root.bind('<Command-w>', lambda e: self._on_cancel())  # macOS快捷键
    
    def _on_ok(self):
        """确定按钮点击事件"""
        if self.question.question_type == 'qa':
            # 获取文本输入
            answer = self.text_widget.get("1.0", tk.END).strip()
            if not answer:
                self._show_macos_warning("请输入回答内容")
                return
            self.result = answer
            
        elif self.question.question_type == 'choice':
            # 获取选择结果
            selected = self.choice_var.get()
            if not selected:
                self._show_macos_warning("请选择一个选项")
                return
            
            if selected == "__custom__":
                # 处理自定义输入
                custom_text = self.custom_entry.get().strip()
                if not custom_text:
                    self._show_macos_warning("请输入自定义选项内容")
                    return
                self.result = custom_text
            else:
                self.result = selected
        
        self.root.destroy()
    
    def _on_cancel(self):
        """取消按钮点击事件"""
        self.result = None
        self.root.destroy()
    
    def _show_macos_warning(self, message):
        """显示macOS风格警告对话框"""
        messagebox.showwarning("", message, parent=self.root)


class UIHandler:
    """UI处理器类"""
    
    @staticmethod
    def show_question(question: ParsedQuestion) -> Optional[str]:
        """
        显示问题对话框
        
        Args:
            question: 解析后的问题对象
            
        Returns:
            Optional[str]: 用户回答，取消时返回None
        """
        try:
            dialog = MacOSQuestionDialog(question)
            return dialog.show_dialog()
        except Exception as e:
            print(f"显示问题对话框时出错: {e}")
            return None
    
    @staticmethod
    async def show_question_async(question: ParsedQuestion) -> Optional[str]:
        """
        异步显示问题对话框
        
        Args:
            question: 解析后的问题对象
            
        Returns:
            Optional[str]: 用户回答，取消时返回None
        """
        loop = asyncio.get_event_loop()
        
        def run_dialog():
            try:
                dialog = MacOSQuestionDialog(question)
                return dialog.show_dialog()
            except Exception as e:
                print(f"异步显示问题对话框时出错: {e}")
                return None
        
        # 在线程池中运行GUI对话框
        result = await loop.run_in_executor(None, run_dialog)
        return result


# 测试用例
if __name__ == "__main__":
    from question_parser import ParsedQuestion, QuestionOption
    
    # 测试问答题
    qa_question = ParsedQuestion(
        question_type="qa",
        title="请输入你的想法",
        content="你对这个功能有什么建议？"
    )
    
    # 测试选择题
    choice_question = ParsedQuestion(
        question_type="choice",
        title="选择你喜欢的颜色",
        content="请选择一个颜色：",
        options=[
            QuestionOption(value="red", text="红色"),
            QuestionOption(value="blue", text="蓝色"),
            QuestionOption(value="green", text="绿色")
        ]
    )
    
    ui_handler = UIHandler()
    
    print("测试问答题...")
    qa_result = ui_handler.show_question(qa_question)
    print(f"问答题结果: {qa_result}")
    
    print("测试选择题...")
    choice_result = ui_handler.show_question(choice_question)
    print(f"选择题结果: {choice_result}") 