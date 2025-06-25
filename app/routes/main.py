"""
主要页面路由
"""

from flask import Blueprint, render_template, request, jsonify
from app.services.document_service import DocumentService
from app.services.analysis_service import AnalysisService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页"""
    return render_template('index.html')

@main_bp.route('/docs')
def docs_list():
    """文档列表页面"""
    try:
        doc_service = DocumentService()
        documents = doc_service.get_all_documents()
        return render_template('docs_list.html', documents=documents)
    except Exception as e:
        return render_template('error.html', error=str(e))

@main_bp.route('/doc/<path:doc_path>')
def doc_detail(doc_path):
    """文档详情页面"""
    try:
        doc_service = DocumentService()
        document = doc_service.get_document(doc_path)
        
        if not document:
            return render_template('error.html', error="文档不存在")
        
        # 获取文档分析结果
        analysis_service = AnalysisService()
        analysis = analysis_service.analyze_document(document)
        
        return render_template('doc_detail.html', 
                             document=document, 
                             analysis=analysis)
    except Exception as e:
        return render_template('error.html', error=str(e))

@main_bp.route('/search')
def search():
    """搜索页面"""
    query = request.args.get('q', '')
    if query:
        try:
            doc_service = DocumentService()
            results = doc_service.search_documents(query)
            return render_template('search_results.html', 
                                 results=results, 
                                 query=query)
        except Exception as e:
            return render_template('error.html', error=str(e))
    
    return render_template('search.html')

@main_bp.route('/analysis')
def analysis_dashboard():
    """分析仪表板"""
    try:
        analysis_service = AnalysisService()
        stats = analysis_service.get_global_statistics()
        return render_template('analysis_dashboard.html', stats=stats)
    except Exception as e:
        return render_template('error.html', error=str(e))

@main_bp.route('/about')
def about():
    """关于页面"""
    return render_template('about.html') 