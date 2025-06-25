#!/usr/bin/env python3
"""
系统测试脚本 - 验证各个模块是否正常工作
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from app import create_app
        print("✅ Flask应用导入成功")
    except Exception as e:
        print(f"❌ Flask应用导入失败: {e}")
        return False
    
    try:
        from app.services.document_service import DocumentService
        print("✅ 文档服务导入成功")
    except Exception as e:
        print(f"❌ 文档服务导入失败: {e}")
        return False
    
    try:
        from app.services.analysis_service import AnalysisService
        print("✅ 分析服务导入成功")
    except Exception as e:
        print(f"❌ 分析服务导入失败: {e}")
        return False
    
    return True

def test_document_service():
    """测试文档服务"""
    print("\n📚 测试文档服务...")
    
    try:
        from app.services.document_service import DocumentService
        
        # 设置测试环境
        os.environ['OBSIDIAN_VAULT_PATH'] = './docs'
        
        doc_service = DocumentService()
        documents = doc_service.get_all_documents()
        
        print(f"✅ 文档服务正常，找到 {len(documents)} 个文档")
        
        if documents:
            print("📄 文档列表:")
            for doc in documents[:3]:  # 只显示前3个
                print(f"  - {doc['title']} ({doc['file_path']})")
        
        return True
        
    except Exception as e:
        print(f"❌ 文档服务测试失败: {e}")
        return False

def test_analysis_service():
    """测试分析服务"""
    print("\n🧠 测试分析服务...")
    
    try:
        from app.services.analysis_service import AnalysisService
        
        analysis_service = AnalysisService()
        
        # 测试文本分析
        test_text = "这是一个测试文档。Python是一种优秀的编程语言。"
        analysis = analysis_service.analyze_document({
            'content': test_text,
            'title': '测试文档'
        })
        
        print("✅ 分析服务正常")
        print(f"📊 基础统计: {analysis['basic_stats']['word_count']} 字")
        print(f"🔑 关键词: {len(analysis['keywords'])} 个")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析服务测试失败: {e}")
        return False

def test_flask_app():
    """测试Flask应用"""
    print("\n🌐 测试Flask应用...")
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # 测试首页
            response = client.get('/')
            if response.status_code == 200:
                print("✅ 首页路由正常")
            else:
                print(f"❌ 首页路由失败: {response.status_code}")
                return False
            
            # 测试API健康检查
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ API健康检查正常")
            else:
                print(f"❌ API健康检查失败: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Flask应用测试失败: {e}")
        return False

def check_dependencies():
    """检查依赖"""
    print("📦 检查依赖...")
    
    required_packages = [
        'flask',
        'markdown',
        'frontmatter',
        'jieba',
        'nltk',
        'textstat'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🧪 Obsidian文档展示系统 - 系统测试")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请先安装依赖")
        return
    
    # 测试模块导入
    if not test_imports():
        print("\n❌ 模块导入测试失败")
        return
    
    # 测试文档服务
    if not test_document_service():
        print("\n❌ 文档服务测试失败")
        return
    
    # 测试分析服务
    if not test_analysis_service():
        print("\n❌ 分析服务测试失败")
        return
    
    # 测试Flask应用
    if not test_flask_app():
        print("\n❌ Flask应用测试失败")
        return
    
    print("\n🎉 所有测试通过！系统可以正常启动")
    print("\n💡 启动系统:")
    print("  python start.py")
    print("  或")
    print("  python run.py")

if __name__ == '__main__':
    main() 