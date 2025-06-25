#!/usr/bin/env python3
"""
Obsidian文档展示与分析系统启动文件
"""

import os
from dotenv import load_dotenv
from app import create_app

# 加载环境变量
load_dotenv()

def main():
    """主函数"""
    app = create_app()
    
    # 获取配置
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 启动Obsidian文档展示系统...")
    print(f"📍 访问地址: http://{host}:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    
    # 启动应用
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )

if __name__ == '__main__':
    main() 