# 🎯 Ask-MCP - AI交互式问答工具

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-red.svg)

**一个允许AI在对话中动态询问用户问题的现代化MCP工具**

</div>

---

## 📋 项目简介

Ask-MCP 是一个基于 Model Context Protocol (MCP) 的交互式问答工具，它允许AI助手在对话过程中通过美观的图形界面向用户提出问题并获取回答。**现已支持图片粘贴和拖拽功能，遵循MCP协议标准！**

## 🚀 快速开始

### 1. 下载项目
```bash
# 从GitHub下载项目
git clone https://github.com/your-username/ask-mcp.git
cd ask-mcp
```

### 2. 运行安装脚本
```bash
# Windows用户直接双击运行
第一次使用时运行.bat
```

### 3. 配置MCP服务器

安装脚本会生成 `mcp.json` 配置文件，将其内容合并到以下位置：

**Cursor IDE:**
- 配置文件位置: `%APPDATA%\Cursor\User\globalStorage\cursor.workbench\mcp.json`

**Claude Desktop:**
- 配置文件位置: `%APPDATA%\Claude\claude_desktop_config.json`

将生成的配置内容添加到现有的 `mcpServers` 部分即可。

### 4. 测试界面
```bash
# 测试现代化UI界面
python testUI.py
```

## 📖 使用示例

### AI使用方式

AI可以通过调用 `ask_user_question` 工具来向用户提问：

#### 问答题示例
```xml
<question type="qa">
  <title>项目反馈</title>
  <content>请分享您对这个功能的使用体验</content>
</question>
```

#### 选择题示例
```xml
<question type="choice">
  <title>技术偏好</title>
  <content>请选择您偏好的编程语言：</content>
  <options>
    <option value="python">Python</option>
    <option value="javascript">JavaScript</option>
    <option value="rust">Rust</option>
  </options>
</question>
```

### 🖼️ 图片支持功能

**新功能特性：**
- ✅ **图片粘贴**: 支持 Ctrl+V 粘贴剪贴板图片
- ✅ **图片拖拽**: 支持直接拖拽图片文件到输入框
- ✅ **多格式支持**: PNG, JPG, GIF, BMP 等常见格式
- ✅ **MCP协议兼容**: 图片数据按照MCP标准进行base64编码
- ✅ **智能显示**: 图片以占位符形式显示，不影响界面美观

**图片数据格式：**
```json
{
  "text": "用户输入的文本内容",
  "images": [
    {
      "type": "image",
      "data": "base64编码的图片数据",
      "mimeType": "image/png"
    }
  ]
}
```

## 🏗️ 项目结构

```
ask-mcp/
├── 📄 README.md                 # 项目说明文档
├── 📄 requirements.txt          # Python依赖列表
├── 🔧 第一次使用时运行.bat      # 一键安装脚本
├── 🚀 fastmcp_server.py        # MCP服务器主程序
├── 🎨 ui_handler.py            # 现代化UI界面处理
├── 📝 question_parser.py       # XML问题解析器
└── 🧪 testUI.py               # UI功能测试
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

<div align="center">

**如果这个项目对您有帮助，请给我一个 ⭐ Star！**

</div> 