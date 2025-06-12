"""
现代化图形界面处理模块
使用PyQt5创建美观的现代化弹出窗口供用户回答问题
支持自适应分辨率、圆角阴影、渐变背景和流畅动效
"""

import sys
from typing import Optional
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QTextEdit, QRadioButton, 
                           QLineEdit, QButtonGroup, QFrame, QScrollArea, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient, QPainter, QPen, QBrush, QPixmap
from question_parser import ParsedQuestion, QuestionOption


class ModernQuestionDialog(QWidget):
    """现代化的问题对话框，支持自适应分辨率和美观效果"""
    
    finished = pyqtSignal(object)
    
    def __init__(self, question: ParsedQuestion):
        super().__init__()
        self.question = question
        self.result = None
        self.choice_group = None
        self.custom_input = None
        self.text_input = None
        self.error_label = None
        self.animation = None
        
        # 获取屏幕信息以适应分辨率
        self.screen = QApplication.desktop().screenGeometry()
        self.scale_factor = self.get_scale_factor()
        
        self.init_ui()
        self.setup_animations()
        
    def get_scale_factor(self):
        """根据屏幕分辨率计算缩放因子"""
        base_width = 1920
        base_height = 1080
        
        # 计算基于宽度和高度的缩放因子
        width_scale = self.screen.width() / base_width
        height_scale = self.screen.height() / base_height
        
        # 使用较小的缩放因子，确保界面不会过大
        scale = min(width_scale, height_scale)
        
        # 限制缩放范围在0.7到1.5之间
        return max(0.7, min(1.5, scale))
        
    def scaled(self, value):
        """根据缩放因子调整数值"""
        return int(value * self.scale_factor)
        
    def init_ui(self):
        """初始化现代化界面"""
        # 设置窗口属性
        self.setWindowTitle("询问问题")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 根据内容类型和缩放因子设置窗口大小
        if self.question.question_type == 'choice':
            width = self.scaled(600)
            height = self.scaled(500)
        else:
            width = self.scaled(550)
            height = self.scaled(400)
            
        self.setFixedSize(width, height)
        
        # 居中显示
        self.center_window()
        
        # 创建主容器
        self.setup_main_container()
        
        # 创建布局
        self.setup_layout()
        
        # 设置样式
        self.setup_styles()
        
        # 添加阴影效果
        self.add_shadow_effect()
        
    def center_window(self):
        """窗口居中"""
        x = (self.screen.width() - self.width()) // 2
        y = (self.screen.height() - self.height()) // 2
        self.move(x, y)
        
    def setup_main_container(self):
        """设置主容器"""
        self.main_container = QFrame(self)
        self.main_container.setGeometry(0, 0, self.width(), self.height())
        self.main_container.setObjectName("mainContainer")
        
    def setup_layout(self):
        """设置现代化布局"""
        main_layout = QVBoxLayout(self.main_container)
        main_layout.setSpacing(self.scaled(20))
        main_layout.setContentsMargins(self.scaled(30), self.scaled(30), self.scaled(30), self.scaled(30))
        
        # 创建标题区域
        self.create_header(main_layout)
        
        # 错误信息标签
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setVisible(False)
        main_layout.addWidget(self.error_label)
        
        # 输入区域
        if self.question.question_type == 'qa':
            self.create_text_input(main_layout)
        elif self.question.question_type == 'choice':
            self.create_choice_input(main_layout)
        
        # 按钮区域
        self.create_buttons(main_layout)
        
    def create_header(self, layout):
        """创建现代化头部区域"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(self.scaled(12))
        
        # 标题
        title_label = QLabel(self.question.title)
        title_label.setObjectName("titleLabel")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        # 内容描述
        if self.question.content:
            content_label = QLabel(self.question.content)
            content_label.setObjectName("contentLabel")
            content_label.setWordWrap(True)
            content_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(content_label)
            
        layout.addWidget(header_frame)
        
    def create_text_input(self, layout):
        """创建现代化文本输入区域"""
        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_input = QTextEdit()
        self.text_input.setObjectName("modernTextEdit")
        self.text_input.setPlaceholderText("💭 请在此输入您的回答...")
        self.text_input.setMaximumHeight(self.scaled(150))
        self.text_input.setAcceptRichText(False)
        
        input_layout.addWidget(self.text_input)
        layout.addWidget(input_frame)
        
        # 聚焦到文本输入框
        self.text_input.setFocus()
        
    def create_choice_input(self, layout):
        """创建现代化选择题输入区域"""
        self.choice_group = QButtonGroup()
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setObjectName("modernScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(self.scaled(250))
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_widget = QWidget()
        scroll_widget.setObjectName("scrollWidget")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(self.scaled(8))
        
        # 添加预设选项
        for i, option in enumerate(self.question.options):
            option_frame = QFrame()
            option_frame.setObjectName("optionFrame")
            option_layout = QHBoxLayout(option_frame)
            option_layout.setContentsMargins(self.scaled(15), self.scaled(8), self.scaled(15), self.scaled(8))
            
            radio = QRadioButton(option.text)
            radio.setObjectName("modernRadio")
            radio.setAttribute(Qt.WA_Hover, True)
            
            # 添加emoji图标
            emoji_icons = ["🔹", "🔸", "⭐", "🎯", "🌟", "💎", "🎪", "🎨", "🎭", "🎪"]
            if i < len(emoji_icons):
                radio.setText(f"{emoji_icons[i]} {option.text}")
            
            self.choice_group.addButton(radio, i)
            option_layout.addWidget(radio)
            scroll_layout.addWidget(option_frame)
            
            # 默认选择第一个
            if i == 0:
                radio.setChecked(True)
        
        # 添加"其他"选项
        other_frame = QFrame()
        other_frame.setObjectName("otherFrame")
        other_layout = QVBoxLayout(other_frame)
        other_layout.setContentsMargins(self.scaled(15), self.scaled(8), self.scaled(15), self.scaled(8))
        other_layout.setSpacing(self.scaled(8))
        
        other_radio = QRadioButton("✨ 其他")
        other_radio.setObjectName("modernRadio")
        other_radio.setAttribute(Qt.WA_Hover, True)
        self.choice_group.addButton(other_radio, len(self.question.options))
        other_layout.addWidget(other_radio)
        
        self.custom_input = QLineEdit()
        self.custom_input.setObjectName("modernLineEdit")
        self.custom_input.setPlaceholderText("🖊️ 请输入自定义选项...")
        self.custom_input.setEnabled(False)
        other_layout.addWidget(self.custom_input)
        
        other_frame.setLayout(other_layout)
        scroll_layout.addWidget(other_frame)
        
        # 连接信号
        other_radio.toggled.connect(self.on_custom_toggled)
        self.custom_input.textChanged.connect(self.on_custom_changed)
        
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
    def create_buttons(self, layout):
        """创建现代化按钮区域"""
        button_frame = QFrame()
        button_frame.setObjectName("buttonFrame")
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(self.scaled(15))
        button_layout.addStretch()
        
        # 取消按钮
        cancel_btn = QPushButton("✖ 取消")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setFixedSize(self.scaled(100), self.scaled(40))
        cancel_btn.clicked.connect(self.cancel_dialog)
        cancel_btn.setAttribute(Qt.WA_Hover, True)
        button_layout.addWidget(cancel_btn)
        
        # 确定按钮
        ok_btn = QPushButton("✓ 确定")
        ok_btn.setObjectName("okButton")
        ok_btn.setFixedSize(self.scaled(100), self.scaled(40))
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.submit_answer)
        ok_btn.setAttribute(Qt.WA_Hover, True)
        button_layout.addWidget(ok_btn)
        
        layout.addWidget(button_frame)
        
    def add_shadow_effect(self):
        """添加阴影效果"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(self.scaled(25))
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, self.scaled(8))
        self.main_container.setGraphicsEffect(shadow)
        
    def setup_animations(self):
        """设置动画效果"""
        # 入场动画
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 设置初始位置（从屏幕上方滑入）
        start_rect = QRect(self.x(), -self.height(), self.width(), self.height())
        end_rect = QRect(self.x(), self.y(), self.width(), self.height())
        
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        
    def showEvent(self, event):
        """窗口显示时播放动画"""
        super().showEvent(event)
        if self.animation:
            self.animation.start()
            
    def setup_styles(self):
        """设置现代化样式"""
        font_size_base = self.scaled(13)
        font_size_title = self.scaled(18)
        font_size_content = self.scaled(14)
        
        self.setStyleSheet(f"""
            /* 主容器 */
            QFrame#mainContainer {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: {self.scaled(16)}px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            /* 字体基础设置 */
            * {{
                font-family: 'Microsoft YaHei UI', 'Segoe UI', Arial, sans-serif;
                color: white;
            }}
            
            /* 头部区域 */
            QFrame#headerFrame {{
                background: transparent;
                border: none;
            }}
            
            /* 标题样式 */
            QLabel#titleLabel {{
                font-size: {font_size_title}px;
                font-weight: bold;
                color: white;
                background: transparent;
                padding: {self.scaled(10)}px;
            }}
            
            /* 内容样式 */
            QLabel#contentLabel {{
                font-size: {font_size_content}px;
                color: rgba(255, 255, 255, 0.9);
                background: transparent;
                padding: {self.scaled(5)}px;
            }}
            
            /* 错误标签 */
            QLabel#errorLabel {{
                color: #ff6b6b;
                background: rgba(255, 107, 107, 0.1);
                border: 1px solid rgba(255, 107, 107, 0.3);
                border-radius: {self.scaled(8)}px;
                padding: {self.scaled(10)}px;
                font-size: {font_size_base}px;
            }}
            
            /* 输入框区域 */
            QFrame#inputFrame {{
                background: transparent;
                border: none;
            }}
            
            /* 文本输入框 */
            QTextEdit#modernTextEdit {{
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: {self.scaled(12)}px;
                padding: {self.scaled(15)}px;
                font-size: {font_size_base}px;
                color: #333;
                selection-background-color: #667eea;
            }}
            
            QTextEdit#modernTextEdit:focus {{
                border: 2px solid rgba(255, 255, 255, 0.8);
                background: rgba(255, 255, 255, 1.0);
            }}
            
            /* 滚动区域 */
            QScrollArea#modernScrollArea {{
                background: transparent;
                border: none;
            }}
            
            QWidget#scrollWidget {{
                background: transparent;
            }}
            
            /* 选项框架 */
            QFrame#optionFrame {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: {self.scaled(8)}px;
                margin: {self.scaled(2)}px;
            }}
            
            QFrame#optionFrame:hover {{
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.4);
            }}
            
            QFrame#otherFrame {{
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: {self.scaled(8)}px;
                margin: {self.scaled(2)}px;
            }}
            
            /* 单选按钮 */
            QRadioButton#modernRadio {{
                font-size: {font_size_base}px;
                color: white;
                background: transparent;
                padding: {self.scaled(5)}px;
                spacing: {self.scaled(8)}px;
            }}
            
            QRadioButton#modernRadio::indicator {{
                width: {self.scaled(16)}px;
                height: {self.scaled(16)}px;
            }}
            
            QRadioButton#modernRadio::indicator:unchecked {{
                border: 2px solid rgba(255, 255, 255, 0.6);
                border-radius: {self.scaled(8)}px;
                background: transparent;
            }}
            
            QRadioButton#modernRadio::indicator:checked {{
                border: 2px solid white;
                border-radius: {self.scaled(8)}px;
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.5, stop:0 white, stop:0.3 white, 
                    stop:0.4 transparent, stop:1 transparent);
            }}
            
            /* 自定义输入框 */
            QLineEdit#modernLineEdit {{
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: {self.scaled(6)}px;
                padding: {self.scaled(8)}px;
                font-size: {font_size_base}px;
                color: #333;
            }}
            
            QLineEdit#modernLineEdit:focus {{
                border: 1px solid rgba(255, 255, 255, 0.8);
                background: rgba(255, 255, 255, 1.0);
            }}
            
            QLineEdit#modernLineEdit:disabled {{
                background: rgba(255, 255, 255, 0.3);
                color: rgba(255, 255, 255, 0.5);
            }}
            
            /* 按钮区域 */
            QFrame#buttonFrame {{
                background: transparent;
                border: none;
            }}
            
            /* 取消按钮 */
            QPushButton#cancelButton {{
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: {self.scaled(20)}px;
                color: white;
                font-size: {font_size_base}px;
                font-weight: bold;
            }}
            
            QPushButton#cancelButton:hover {{
                background: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }}
            
            QPushButton#cancelButton:pressed {{
                background: rgba(255, 255, 255, 0.1);
            }}
            
            /* 确定按钮 */
            QPushButton#okButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4facfe, stop:1 #00f2fe);
                border: none;
                border-radius: {self.scaled(20)}px;
                color: white;
                font-size: {font_size_base}px;
                font-weight: bold;
            }}
            
            QPushButton#okButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5fbbff, stop:1 #1ff3ff);
            }}
            
            QPushButton#okButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3f9bde, stop:1 #00d2de);
            }}
            
            /* 滚动条样式 */
            QScrollBar:vertical {{
                background: rgba(255, 255, 255, 0.1);
                width: {self.scaled(8)}px;
                border-radius: {self.scaled(4)}px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background: rgba(255, 255, 255, 0.3);
                border-radius: {self.scaled(4)}px;
                min-height: {self.scaled(20)}px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: rgba(255, 255, 255, 0.5);
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
    def on_custom_toggled(self, checked):
        """处理自定义选项切换"""
        self.custom_input.setEnabled(checked)
        if checked:
            self.custom_input.setFocus()
        else:
            self.custom_input.clear()
            
    def on_custom_changed(self, text):
        """处理自定义输入变化"""
        if text.strip():
            # 如果有自定义文本，自动选择"其他"选项
            other_button = self.choice_group.button(len(self.question.options))
            if other_button and not other_button.isChecked():
                other_button.setChecked(True)
    
    def show_error(self, message, duration=3000):
        """显示错误信息"""
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        
        # 自动隐藏错误信息
        QTimer.singleShot(duration, lambda: self.error_label.setVisible(False))
        
    def submit_answer(self):
        """提交答案"""
        try:
            if self.question.question_type == 'qa':
                # 问答题
                answer = self.text_input.toPlainText().strip()
                if not answer:
                    self.show_error("请输入您的回答")
                    return
                self.result = answer
                
            elif self.question.question_type == 'choice':
                # 选择题
                checked_button = self.choice_group.checkedButton()
                if not checked_button:
                    self.show_error("请选择一个选项")
                    return
                    
                button_id = self.choice_group.id(checked_button)
                
                if button_id == len(self.question.options):  # "其他"选项
                    custom_text = self.custom_input.text().strip()
                    if not custom_text:
                        self.show_error("请输入自定义选项内容")
                        return
                    self.result = custom_text
                else:
                    # 预设选项
                    option = self.question.options[button_id]
                    self.result = option.value
            
            self.finished.emit(self.result)
            self.close()
            
        except Exception as e:
            self.show_error(f"提交失败: {str(e)}")
    
    def cancel_dialog(self):
        """取消对话框"""
        self.result = None
        self.finished.emit(None)
        self.close()
        
    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() == Qt.Key_Escape:
            self.cancel_dialog()
        elif event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            self.submit_answer()
        else:
            super().keyPressEvent(event)
            
    def mousePressEvent(self, event):
        """处理鼠标按压事件，实现窗口拖拽"""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，实现窗口拖拽"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_start_position'):
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()


class UIHandler:
    """UI处理器"""
    
    @staticmethod
    def show_question(question: ParsedQuestion) -> Optional[str]:
        """同步显示问题对话框"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
            app.setQuitOnLastWindowClosed(False)
        else:
            app = QApplication.instance()
        
        result = None
        
        try:
            dialog = ModernQuestionDialog(question)
            
            def on_finished(result_value):
                nonlocal result
                result = result_value
                app.quit()
            
            dialog.finished.connect(on_finished)
            dialog.show()
            
            app.exec_()
            return result
            
        except Exception as e:
            print(f"显示问题对话框时出错: {e}")
            return None
    
    @staticmethod  
    async def show_question_async(question: ParsedQuestion) -> Optional[str]:
        """异步显示问题对话框"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        def run_dialog():
            return UIHandler.show_question(question)
        
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(executor, run_dialog)
            return result


# 保持向后兼容
SimpleQuestionDialog = ModernQuestionDialog 