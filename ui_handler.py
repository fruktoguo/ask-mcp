"""
现代化图形界面处理模块
使用PyQt5创建美观的现代化弹出窗口供用户回答问题
支持自适应分辨率、圆角阴影、渐变背景和流畅动效
支持图片粘贴和拖拽，遵循MCP协议格式
"""

import sys
import base64
import json
import mimetypes
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QTextEdit, QRadioButton, 
                           QLineEdit, QButtonGroup, QFrame, QScrollArea, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QSize, QMimeData
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient, QPainter, QPen, QBrush, QPixmap, QClipboard
from question_parser import ParsedQuestion, QuestionOption


class ImageSupportedTextEdit(QTextEdit):
    """支持图片粘贴的QTextEdit"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.images = []  # 存储图片数据，格式遵循MCP协议
        
    def canInsertFromMimeData(self, source):
        """检查是否可以插入MIME数据"""
        if source.hasImage() or source.hasUrls():
            return True
        return super().canInsertFromMimeData(source)
        
    def insertFromMimeData(self, source):
        """处理MIME数据插入"""
        try:
            # 优先尝试处理图片数据
            if source.hasImage():
                image = source.imageData()
                if image:
                    self.insert_image(image)
                    return
                    
            # 处理URL（包括文件路径）
            if source.hasUrls():
                for url in source.urls():
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if self.is_image_file(file_path):
                            self.insert_image_from_file(file_path)
                            return
            
            # 处理文本中的图片路径（QQ等应用复制图片时的情况）
            if source.hasText():
                text = source.text().strip()
                if text.startswith('file:///') and self.is_image_file(text.replace('file:///', '')):
                    # 从文件路径加载图片
                    file_path = text.replace('file:///', '').replace('/', '\\')
                    if self.is_image_file(file_path):
                        self.insert_image_from_file(file_path)
                        return
                elif text.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                    # 检查是否是图片文件路径
                    if self.is_image_file(text):
                        self.insert_image_from_file(text)
                        return
                            
            super().insertFromMimeData(source)
        except Exception as e:
            print(f"处理粘贴数据时出错: {e}")
            # 即使出错也要调用父类方法，避免完全失败
            try:
                super().insertFromMimeData(source)
            except:
                pass  # 忽略父类方法的错误
        
    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasImage() or self.has_image_urls(event.mimeData()):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)
            
    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        if event.mimeData().hasImage() or self.has_image_urls(event.mimeData()):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)
            
    def dropEvent(self, event):
        """拖拽放下事件"""
        try:
            if event.mimeData().hasImage():
                self.insert_image(event.mimeData().imageData())
                event.acceptProposedAction()
            elif self.has_image_urls(event.mimeData()):
                for url in event.mimeData().urls():
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if self.is_image_file(file_path):
                            self.insert_image_from_file(file_path)
                            break
                event.acceptProposedAction()
            else:
                super().dropEvent(event)
        except Exception as e:
            print(f"拖拽事件处理失败: {e}")
            # 不抛出异常，避免闪退
        
    def has_image_urls(self, mime_data):
        """检查是否包含图片URL"""
        if mime_data.hasUrls():
            for url in mime_data.urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if self.is_image_file(file_path):
                        return True
        return False
        
    def is_image_file(self, file_path):
        """检查是否为图片文件"""
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            return mime_type and mime_type.startswith('image/')
        except:
            return False
            
    def insert_image(self, image):
        """插入图片（从QPixmap或QImage）"""
        try:
            if hasattr(image, 'save'):
                # QPixmap或QImage
                pixmap = image if isinstance(image, QPixmap) else QPixmap.fromImage(image)
                
                # 检查图片是否有效
                if pixmap.isNull():
                    print("图片数据无效，跳过插入")
                    return
                
                # 缩放图片到合适大小
                max_width = 300
                max_height = 200
                if pixmap.width() > max_width or pixmap.height() > max_height:
                    pixmap = pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # 转换为字节数据
                from PyQt5.QtCore import QBuffer, QIODevice
                buffer = QBuffer()
                buffer.open(QIODevice.WriteOnly)
                
                # 尝试保存为PNG格式
                if not pixmap.save(buffer, "PNG"):
                    print("无法将图片保存为PNG格式")
                    return
                    
                image_data = buffer.data()
                
                # 检查数据是否有效
                if not image_data or len(image_data) == 0:
                    print("图片数据为空，跳过插入")
                    return
                
                # 按MCP协议格式存储
                image_info = {
                    "type": "image",
                    "data": base64.b64encode(image_data).decode('utf-8'),
                    "mimeType": "image/png"
                }
                
                self.images.append(image_info)
                
                # 在文本编辑器中插入实际图片（不显示占位符）
                cursor = self.textCursor()
                cursor.insertImage(pixmap.toImage())
                
        except Exception as e:
            print(f"插入图片失败: {e}")
            # 不抛出异常，避免闪退
        
    def insert_image_from_file(self, file_path):
        """从文件插入图片"""
        try:
            # 处理文件路径格式
            import os
            if file_path.startswith('file:///'):
                file_path = file_path.replace('file:///', '')
            
            # 规范化路径
            file_path = os.path.normpath(file_path)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"图片文件不存在: {file_path}")
                return
            
            # 检查文件大小（避免加载过大的文件）
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB限制
                print(f"图片文件过大 ({file_size} bytes): {file_path}")
                return
            
            # 加载图片并创建QPixmap
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                print(f"无法加载图片: {file_path}")
                return
                
            # 缩放图片到合适大小
            max_width = 300
            max_height = 200
            if pixmap.width() > max_width or pixmap.height() > max_height:
                pixmap = pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
            # 读取原始文件数据用于MCP协议
            try:
                with open(file_path, 'rb') as f:
                    image_data = f.read()
            except Exception as e:
                print(f"读取图片文件失败: {e}")
                return
                
            # 检查数据是否有效
            if not image_data or len(image_data) == 0:
                print(f"图片文件数据为空: {file_path}")
                return
                
            # 获取MIME类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = 'image/png'
                
            # 按MCP协议格式存储
            image_info = {
                "type": "image", 
                "data": base64.b64encode(image_data).decode('utf-8'),
                "mimeType": mime_type
            }
            
            self.images.append(image_info)
            
            # 在文本编辑器中插入实际图片（不显示占位符）
            cursor = self.textCursor()
            cursor.insertImage(pixmap.toImage())
            
        except Exception as e:
            print(f"从文件插入图片失败: {e}")
            print(f"文件路径: {file_path}")
            # 不抛出异常，避免闪退
        
    def get_content_with_images(self):
        """获取包含图片的完整内容（MCP协议格式）"""
        text_content = self.toPlainText()
        
        if not self.images:
            return text_content
            
        # 返回包含文本和图片的结构化数据
        return {
            "text": text_content,
            "images": self.images
        }


class AutoResizeTextEdit(QTextEdit):
    """自适应高度的文本编辑器，支持图片粘贴和拖拽"""
    
    def __init__(self, parent=None, is_single_line=False):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.images = []  # 存储图片数据，格式遵循MCP协议
        self.is_single_line = is_single_line
        self._updating_height = False  # 防止高度更新时的递归调用
        
        # 基础设置
        self.setAcceptRichText(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        if is_single_line:
            # 单行模式设置
            self.setLineWrapMode(QTextEdit.NoWrap)
            self.setMinimumHeight(40)
            self.setMaximumHeight(120)  # 允许一定的扩展高度
        else:
            # 多行模式设置
            self.setLineWrapMode(QTextEdit.WidgetWidth)
            self.setMinimumHeight(60)
            self.setMaximumHeight(300)
        
        # 设置文档属性
        try:
            self.document().setDocumentMargin(8)
            # 连接文档内容变化信号以自动调整高度
            self.document().contentsChanged.connect(self._adjust_height)
            self.textChanged.connect(self._on_text_changed)
        except Exception as e:
            print(f"设置文档属性时出错: {e}")
    
    def _adjust_height(self):
        """自动调整高度以适应内容"""
        if self._updating_height:
            return
            
        try:
            self._updating_height = True
            
            # 计算文档需要的高度
            doc_height = self.document().size().height()
            margins = self.contentsMargins()
            total_height = int(doc_height + margins.top() + margins.bottom() + 10)
            
            # 限制高度范围
            min_height = self.minimumHeight()
            max_height = self.maximumHeight()
            new_height = max(min_height, min(max_height, total_height))
            
            # 只有当高度确实需要改变时才调整
            if abs(self.height() - new_height) > 5:
                self.setFixedHeight(new_height)
                
        except Exception as e:
            print(f"调整高度时出错: {e}")
        finally:
            self._updating_height = False
    
    def _on_text_changed(self):
        """处理文本变化"""
        try:
            if self.is_single_line:
                # 单行模式：限制文本长度并阻止换行
                text = self.toPlainText()
                if '\n' in text or '\r' in text:
                    # 移除换行符
                    clean_text = text.replace('\n', ' ').replace('\r', ' ')
                    cursor = self.textCursor()
                    cursor.select(cursor.Document)
                    cursor.insertText(clean_text)
                
                # 限制文本长度
                if len(text) > 500:
                    cursor = self.textCursor()
                    cursor.select(cursor.Document)
                    cursor.insertText(text[:500])
            
            # 调整高度
            self._adjust_height()
            
        except Exception as e:
            print(f"处理文本变化时出错: {e}")
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        try:
            # 单行模式下阻止换行
            if self.is_single_line and event.key() in (Qt.Key_Return, Qt.Key_Enter):
                return
                
            # 处理Ctrl+V粘贴图片
            if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
                try:
                    clipboard = QApplication.clipboard()
                    mime_data = clipboard.mimeData()
                    
                    if mime_data.hasImage():
                        self.insert_image(mime_data.imageData())
                        return
                    
                    # 处理文件路径
                    if mime_data.hasText():
                        text = mime_data.text().strip()
                        if self.is_image_file(text):
                            self.insert_image_from_file(text)
                            return
                except Exception as e:
                    print(f"处理粘贴事件时出错: {e}")
                
            super().keyPressEvent(event)
        except Exception as e:
            print(f"键盘事件处理失败: {e}")
            try:
                super().keyPressEvent(event)
            except:
                pass
    
    def insertFromMimeData(self, source):
        """处理MIME数据插入"""
        try:
            if source.hasImage():
                self.insert_image(source.imageData())
                return
                
            if source.hasUrls():
                for url in source.urls():
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if self.is_image_file(file_path):
                            self.insert_image_from_file(file_path)
                            return
            
            super().insertFromMimeData(source)
        except Exception as e:
            print(f"处理MIME数据时出错: {e}")
            try:
                super().insertFromMimeData(source)
            except:
                pass
    
    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        try:
            if event.mimeData().hasImage() or self.has_image_urls(event.mimeData()):
                event.acceptProposedAction()
            else:
                super().dragEnterEvent(event)
        except Exception as e:
            print(f"拖拽进入事件处理失败: {e}")
            
    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        try:
            if event.mimeData().hasImage() or self.has_image_urls(event.mimeData()):
                event.acceptProposedAction()
            else:
                super().dragMoveEvent(event)
        except Exception as e:
            print(f"拖拽移动事件处理失败: {e}")
            
    def dropEvent(self, event):
        """拖拽放下事件"""
        try:
            if event.mimeData().hasImage():
                self.insert_image(event.mimeData().imageData())
                event.acceptProposedAction()
            elif self.has_image_urls(event.mimeData()):
                for url in event.mimeData().urls():
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if self.is_image_file(file_path):
                            self.insert_image_from_file(file_path)
                            break
                event.acceptProposedAction()
            else:
                super().dropEvent(event)
        except Exception as e:
            print(f"拖拽放下事件处理失败: {e}")
    
    def has_image_urls(self, mime_data):
        """检查是否包含图片URL"""
        try:
            if mime_data.hasUrls():
                for url in mime_data.urls():
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if self.is_image_file(file_path):
                            return True
        except:
            pass
        return False
        
    def is_image_file(self, file_path):
        """检查是否为图片文件"""
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            return mime_type and mime_type.startswith('image/')
        except:
            return False
            
    def insert_image(self, image):
        """插入图片"""
        try:
            if hasattr(image, 'save'):
                pixmap = image if isinstance(image, QPixmap) else QPixmap.fromImage(image)
                
                if pixmap.isNull():
                    return
                
                # 根据模式调整图片大小
                if self.is_single_line:
                    max_height = 30
                else:
                    max_height = 100
                    
                if pixmap.height() > max_height:
                    pixmap = pixmap.scaledToHeight(max_height, Qt.SmoothTransformation)
                
                # 保存图片数据
                from PyQt5.QtCore import QBuffer, QIODevice
                buffer = QBuffer()
                buffer.open(QIODevice.WriteOnly)
                
                if pixmap.save(buffer, "PNG"):
                    image_data = buffer.data()
                    if image_data:
                        image_info = {
                            "type": "image",
                            "data": base64.b64encode(image_data).decode('utf-8'),
                            "mimeType": "image/png"
                        }
                        self.images.append(image_info)
                        
                        # 插入图片到文档
                        cursor = self.textCursor()
                        cursor.insertImage(pixmap.toImage())
                        
        except Exception as e:
            print(f"插入图片失败: {e}")
    
    def insert_image_from_file(self, file_path):
        """从文件插入图片"""
        try:
            import os
            
            if file_path.startswith('file:///'):
                file_path = file_path.replace('file:///', '')
            
            file_path = os.path.normpath(file_path)
            
            if not os.path.exists(file_path):
                return
                
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB限制
                return
            
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # 调整图片大小
                if self.is_single_line:
                    max_height = 30
                else:
                    max_height = 200
                    
                if pixmap.height() > max_height:
                    pixmap = pixmap.scaledToHeight(max_height, Qt.SmoothTransformation)
                
                # 读取原始文件数据
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                
                if image_data:
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if not mime_type or not mime_type.startswith('image/'):
                        mime_type = 'image/png'
                    
                    image_info = {
                        "type": "image",
                        "data": base64.b64encode(image_data).decode('utf-8'),
                        "mimeType": mime_type
                    }
                    self.images.append(image_info)
                    
                    # 插入图片到文档
                    cursor = self.textCursor()
                    cursor.insertImage(pixmap.toImage())
                    
        except Exception as e:
            print(f"从文件插入图片失败: {e}")
    
    def get_content_with_images(self):
        """获取包含图片的完整内容（MCP协议格式）"""
        text_content = self.toPlainText()
        
        if not self.images:
            return text_content
            
        return {
            "text": text_content,
            "images": self.images
        }


# 保持向后兼容
class ImageSupportedLineEdit(AutoResizeTextEdit):
    """支持图片粘贴的单行文本编辑器（向后兼容）"""
    
    def __init__(self, parent=None):
        super().__init__(parent, is_single_line=True)


class ModernQuestionDialog(QWidget):
    """现代化的问题对话框，支持自适应分辨率和美观效果"""
    
    finished = pyqtSignal(object)
    
    def __init__(self, question: ParsedQuestion):
        super().__init__()
        self.question = question
        self.result = None  # 默认为None表示未完成
        self.is_completed = False  # 新增：标记对话框是否已完成交互
        self.cancel_reason = None  # 只有在明确取消时才设置
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
        
        # 限制缩放范围在0.6到1.2之间，确保在小屏幕上也能完整显示
        return max(0.6, min(1.2, scale))
        
    def scaled(self, value):
        """根据缩放因子调整数值"""
        return int(value * self.scale_factor)
        
    def init_ui(self):
        """初始化现代化界面"""
        # 设置窗口属性
        self.setWindowTitle("询问问题")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 初始设置一个基础大小
        if self.question.question_type == 'choice':
            base_width = 600
            base_height = 600  # 增加初始高度以容纳"其他"选项
        else:
            base_width = 550
            base_height = 450
            
        # 应用缩放
        width = self.scaled(base_width)
        height = self.scaled(base_height)
        
        # 确保窗口不会超出屏幕边界
        max_width = int(self.screen.width() * 0.9)
        max_height = int(self.screen.height() * 0.9)
        
        width = min(width, max_width)
        height = min(height, max_height)
            
        # 设置初始大小（之后会根据内容调整）
        self.resize(width, height)
        
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
        
        # 根据内容调整最终大小
        self.adjust_size_to_content()
        
    def center_window(self):
        """窗口居中，确保完全在屏幕内"""
        # 计算居中位置
        x = (self.screen.width() - self.width()) // 2
        y = (self.screen.height() - self.height()) // 2
        
        # 确保窗口不会超出屏幕边界
        x = max(0, min(x, self.screen.width() - self.width()))
        y = max(0, min(y, self.screen.height() - self.height()))
        
        self.move(x, y)
    
    def adjust_size_to_content(self):
        """根据内容调整对话框大小"""
        try:
            # 让布局先计算所需的大小
            self.main_container.adjustSize()
            
            # 获取内容所需的大小
            content_size = self.main_container.sizeHint()
            
            # 添加一些边距
            padding = self.scaled(60)  # 总边距
            needed_width = content_size.width() + padding
            needed_height = content_size.height() + padding
            
            # 限制最大和最小尺寸
            min_width = self.scaled(500)
            min_height = self.scaled(400)
            max_width = int(self.screen.width() * 0.9)
            max_height = int(self.screen.height() * 0.9)
            
            # 计算最终尺寸
            final_width = max(min_width, min(needed_width, max_width))
            final_height = max(min_height, min(needed_height, max_height))
            
            # 只有当尺寸确实需要改变时才调整
            if abs(self.width() - final_width) > 10 or abs(self.height() - final_height) > 10:
                self.resize(final_width, final_height)
                self.center_window()  # 重新居中
                
                # 更新主容器大小
                self.main_container.setGeometry(0, 0, self.width(), self.height())
                
        except Exception as e:
            print(f"调整对话框大小时出错: {e}")
        
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
        
        self.text_input = ImageSupportedTextEdit()
        self.text_input.setObjectName("modernTextEdit")
        self.text_input.setPlaceholderText("💭 请在此输入您的回答...\n📎 支持拖拽图片或Ctrl+V粘贴图片")
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
        
        self.custom_input = AutoResizeTextEdit(is_single_line=False)
        self.custom_input.setObjectName("modernTextEdit")
        self.custom_input.setPlaceholderText("🖊️ 请输入自定义选项... 📎 支持拖拽或粘贴图片\n支持多行文本，窗口会自动适应内容高度")
        self.custom_input.setEnabled(False)
        other_layout.addWidget(self.custom_input)
        
        other_frame.setLayout(other_layout)
        scroll_layout.addWidget(other_frame)
        
        # 连接信号 - 使用安全的信号连接
        try:
            other_radio.toggled.connect(self.on_custom_toggled)
            self.custom_input.textChanged.connect(self.on_custom_changed)
        except Exception as e:
            print(f"连接信号时出错: {e}")
        
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
            
            /* 自定义输入框（多行文本编辑器） */
            QTextEdit#modernTextEdit:disabled {{
                background: rgba(255, 255, 255, 0.3);
                color: rgba(255, 255, 255, 0.5);
                border: 2px solid rgba(255, 255, 255, 0.2);
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
        try:
            self.custom_input.setEnabled(checked)
            if checked:
                self.custom_input.setFocus()
                # 当启用"其他"选项时，重新调整对话框大小以适应内容
                QTimer.singleShot(100, self.adjust_size_to_content)
            else:
                # 暂时断开信号连接，避免循环触发
                self.custom_input.textChanged.disconnect()
                self.custom_input.clear()
                # 重新连接信号
                self.custom_input.textChanged.connect(self.on_custom_changed)
                # 清空后也重新调整大小
                QTimer.singleShot(100, self.adjust_size_to_content)
        except Exception as e:
            print(f"处理自定义选项切换时出错: {e}")
            
    def on_custom_changed(self):
        """处理自定义输入变化"""
        try:
            text = self.custom_input.toPlainText().strip()
            if text:
                # 如果有自定义文本，自动选择"其他"选项
                other_button = self.choice_group.button(len(self.question.options))
                if other_button and not other_button.isChecked():
                    # 暂时断开切换信号，避免循环触发
                    other_button.toggled.disconnect()
                    other_button.setChecked(True)
                    # 重新连接信号
                    other_button.toggled.connect(self.on_custom_toggled)
        except Exception as e:
            print(f"处理自定义输入变化时出错: {e}")
    
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
                # 问答题 - 支持图片内容
                content = self.text_input.get_content_with_images()
                
                # 检查是否有内容（文本或图片）
                if isinstance(content, dict):
                    if not content.get("text", "").strip() and not content.get("images", []):
                        self.show_error("请输入您的回答或添加图片")
                        return
                elif not content.strip():
                    self.show_error("请输入您的回答")
                    return
                    
                self.result = content
                
            elif self.question.question_type == 'choice':
                # 选择题
                checked_button = self.choice_group.checkedButton()
                if not checked_button:
                    self.show_error("请选择一个选项")
                    return
                    
                button_id = self.choice_group.id(checked_button)
                
                if button_id == len(self.question.options):  # "其他"选项
                    # 支持图片内容的自定义选项
                    content = self.custom_input.get_content_with_images()
                    
                    # 检查是否有内容（文本或图片）
                    if isinstance(content, dict):
                        if not content.get("text", "").strip() and not content.get("images", []):
                            self.show_error("请输入自定义选项内容或添加图片")
                            return
                    elif not content.strip():
                        self.show_error("请输入自定义选项内容")
                        return
                        
                    self.result = content
                else:
                    # 预设选项
                    option = self.question.options[button_id]
                    self.result = option.value
            
            # 标记为已完成
            self.is_completed = True
            self.finished.emit(self.result)
            self.close()
            
        except Exception as e:
            self.show_error(f"提交失败: {str(e)}")
    
    def cancel_dialog(self):
        """取消对话框"""
        self.cancel_reason = "[BUTTON]用户点击了取消按钮"
        self.is_completed = True
        self.result = None
        self.finished.emit(None)
        self.close()
        
    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() == Qt.Key_Escape:
            self.cancel_reason = "[ESC]用户按了ESC键"
            self.is_completed = True
            self.result = None
            self.finished.emit(None)
            self.close()
        elif event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            self.submit_answer()
        else:
            super().keyPressEvent(event)
            
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 只有在用户主动关闭窗口时才标记为取消
        if not self.is_completed:
            self.cancel_reason = "[CLOSE]用户关闭了窗口(点击X按钮或其他方式)"
            self.is_completed = True
            if self.result is None:
                self.finished.emit(None)
        event.accept()
            
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
        """同步显示问题对话框 - 支持连续调用"""
        from PyQt5.QtCore import QEventLoop
        
        # 获取或创建QApplication实例
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
            app.setQuitOnLastWindowClosed(False)
        
        result_container = {"result": None, "dialog": None, "completed": False}
        
        try:
            dialog = ModernQuestionDialog(question)
            result_container["dialog"] = dialog
            
            # 使用QEventLoop而不是app.exec()来避免连续调用问题
            event_loop = QEventLoop()
            
            def on_finished(result_value):
                result_container["result"] = result_value
                result_container["completed"] = True
                event_loop.quit()  # 退出本地事件循环
            
            dialog.finished.connect(on_finished)
            dialog.show()
            
            # 运行本地事件循环，不影响全局应用程序状态
            event_loop.exec_()
            
            # 从容器中获取结果和对话框引用
            result = result_container["result"]
            dialog_ref = result_container["dialog"]
            completed = result_container["completed"]
            
            # 检查对话框是否正常完成了交互
            if not completed:
                return "CANCELLED:[HANDLER]对话框未正常完成交互"
            
            # 如果结果为None，检查是否是用户主动取消
            if result is None and dialog_ref:
                cancel_reason = getattr(dialog_ref, 'cancel_reason', None)
                if cancel_reason:
                    return f"CANCELLED:{cancel_reason}"
                else:
                    # 没有取消原因说明可能是程序问题，不应该标记为取消
                    return "ERROR:[HANDLER]对话框返回None但无取消原因，可能存在程序错误"
            elif result is None:
                return "ERROR:[HANDLER]UIHandler中result为None且无对话框引用"
            
            return result
            
        except Exception as e:
            print(f"显示问题对话框时出错: {e}")
            return f"ERROR:[EXCEPTION]UIHandler异常: {str(e)}"
        finally:
            # 清理对话框
            if 'dialog' in result_container and result_container["dialog"]:
                try:
                    result_container["dialog"].deleteLater()
                except:
                    pass
    
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