#!/usr/bin/env python3
"""
MCP配置快速设置脚本
自动更新mcp.json中的脚本路径为当前项目目录
"""

import json
import os
import sys
from pathlib import Path

def find_mcp_json():
    """查找所有mcp.json文件"""
    current_dir = Path.cwd()
    mcp_files = []
    
    # 在当前目录查找
    mcp_file = current_dir / "mcp.json"
    if mcp_file.exists():
        mcp_files.append(mcp_file)
    
    # 在.cursor目录查找
    cursor_mcp = current_dir / ".cursor" / "mcp.json"
    if cursor_mcp.exists():
        mcp_files.append(cursor_mcp)
    
    # 在父目录查找
    for parent in current_dir.parents:
        mcp_file = parent / "mcp.json"
        if mcp_file.exists():
            mcp_files.append(mcp_file)
        
        cursor_mcp = parent / ".cursor" / "mcp.json"
        if cursor_mcp.exists():
            mcp_files.append(cursor_mcp)
    
    return mcp_files

def find_fastmcp_server():
    """查找fastmcp_server.py文件"""
    current_dir = Path.cwd()
    
    # 在当前目录查找
    server_file = current_dir / "fastmcp_server.py"
    if server_file.exists():
        return server_file
    
    # 在子目录中查找
    for root, dirs, files in os.walk(current_dir):
        if "fastmcp_server.py" in files:
            return Path(root) / "fastmcp_server.py"
    
    return None

def update_mcp_config():
    """更新MCP配置文件"""
    print("🔍 正在查找配置文件...")
    
    # 查找所有mcp.json文件
    mcp_files = find_mcp_json()
    if not mcp_files:
        print("❌ 未找到任何mcp.json文件")
        return False
    
    print(f"✅ 找到 {len(mcp_files)} 个mcp.json文件:")
    for mcp_file in mcp_files:
        print(f"   - {mcp_file}")
    
    # 查找fastmcp_server.py
    server_file = find_fastmcp_server()
    if not server_file:
        print("❌ 未找到fastmcp_server.py文件")
        return False
    
    print(f"✅ 找到服务器脚本: {server_file}")
    
    # 获取绝对路径并转换为Windows格式
    server_path = str(server_file.resolve()).replace('/', '\\')
    
    success_count = 0
    
    # 更新所有找到的mcp.json文件
    for mcp_file in mcp_files:
        try:
            print(f"\n📝 正在更新: {mcp_file}")
            
            # 读取现有配置
            with open(mcp_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新配置
            if 'mcpServers' in config and 'ask-mcp' in config['mcpServers']:
                old_args = config['mcpServers']['ask-mcp'].get('args', [])
                config['mcpServers']['ask-mcp']['args'] = [server_path]
                
                # 保存配置
                with open(mcp_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print(f"   ✅ 更新成功!")
                print(f"   旧路径: {old_args[0] if old_args else '无'}")
                print(f"   新路径: {server_path}")
                success_count += 1
            else:
                print(f"   ❌ 格式不正确，缺少ask-mcp配置")
                
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON解析错误: {e}")
        except Exception as e:
            print(f"   ❌ 更新时出错: {e}")
    
    return success_count > 0

def main():
    """主函数"""
    print("🚀 MCP配置快速设置工具")
    print("=" * 40)
    
    if update_mcp_config():
        print("\n🎉 配置设置完成！")
        print("💡 提示: 重启Cursor以使配置生效")
    else:
        print("\n❌ 配置设置失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 