#!/usr/bin/env python3
"""
简单的启动脚本 - 用于测试和开发
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('OBSIDIAN_VAULT_PATH', './docs')

def main():
    """主函数"""
    print("🚀 启动Obsidian文档展示系统...")
    print(f"📁 文档库路径: {os.environ.get('OBSIDIAN_VAULT_PATH')}")
    print(f"🔧 调试模式: {os.environ.get('DEBUG')}")
    
    try:
        from app import create_app
        app = create_app()
        
        print("✅ 应用创建成功")
        print("🌐 访问地址: http://127.0.0.1:5000")
        print("⏹️  按 Ctrl+C 停止服务")
        
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 