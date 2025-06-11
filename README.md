# Ask-MCP

一个允许AI在对话中动态询问用户问题的MCP工具。

## 特点

- **简洁高效** - 基于FastMCP框架，代码简洁易维护
- **交互友好** - 图形界面弹窗，支持问答题和选择题
- **灵活扩展** - 自动添加"其他"选项，支持自定义输入
- **现代化设计** - macOS风格界面，支持异步处理

## 功能特性

- 支持AI发送XML格式的问题给用户
- 支持问答题和选择题两种问题类型
- 弹出图形界面窗口供用户回答
- 用户回答后立即返回给AI继续对话
- 异步处理，不阻塞对话流程

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 测试组件
```bash
# 运行组件测试
python test.py
```

### 3. 开发测试
```bash
# 使用MCP Inspector进行开发测试
fastmcp dev fastmcp_server.py
```

### 4. 安装到Claude Desktop
```bash
# 自动安装到Claude Desktop
fastmcp install fastmcp_server.py
```

### 5. 验证安装
重启Claude Desktop，你应该能看到"YuoMCP Interactive Query Tool"已经可用。

## 使用方法

AI可以调用 `ask_user_question` 工具发送问题给用户：

### 问答题示例
```xml
<question type="qa">
  <title>请输入你的想法</title>
  <content>你对这个功能有什么建议？</content>
</question>
```

### 选择题示例
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

## 安装配置

### 自动配置到Cursor IDE

**方法1：使用批处理脚本（推荐）**
```bash
# 双击运行或在命令行执行
install_to_cursor.bat
```

**方法2：使用Python脚本**
```bash
python install_to_cursor.py
```

这些脚本会自动：
- 检测当前工具目录
- 查找Cursor配置目录
- 备份现有配置（如果存在）
- 写入MCP服务器配置
- 提供详细的安装反馈

### 手动配置
如果自动配置失败，可以手动编辑Cursor的MCP配置文件，添加：
```json
{
  "mcpServers": {
    "yuomcp-interactive": {
      "command": "python",
      "args": ["path/to/your/fastmcp_server.py"],
      "env": {}
    }
  }
}
```

## 测试验证

### UI功能测试
```bash
# 运行UI测试脚本，测试界面弹出和数据返回
python testUI.py
```

测试包括：
- 问答题界面测试
- 选择题界面测试
- 复杂选择题测试
- XML解析+UI完整流程测试
- UI响应性测试

### 组件测试
```bash
# 运行组件功能测试
python test.py
```

## 项目结构

- `fastmcp_server.py` - FastMCP服务器主文件
- `ui_handler.py` - 图形界面处理模块  
- `question_parser.py` - XML问题解析模块
- `test.py` - 组件功能测试脚本
- `testUI.py` - UI界面测试脚本
- `install_to_cursor.bat` - Windows批处理安装脚本
- `install_to_cursor.py` - Python安装配置脚本
- `requirements.txt` - 项目依赖
- `README.md` - 项目说明文档 