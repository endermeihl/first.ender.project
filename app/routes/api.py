"""
API路由 - 为后期C/Rust服务预留接口
"""

from flask import Blueprint, request, jsonify, current_app
import requests
import json
from app.services.document_service import DocumentService
from app.services.analysis_service import AnalysisService

api_bp = Blueprint('api', __name__)

@api_bp.route('/documents', methods=['GET'])
def get_documents():
    """获取所有文档列表"""
    try:
        doc_service = DocumentService()
        documents = doc_service.get_all_documents()
        return jsonify({
            'success': True,
            'data': documents,
            'count': len(documents)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/documents/<path:doc_path>', methods=['GET'])
def get_document(doc_path):
    """获取单个文档"""
    try:
        doc_service = DocumentService()
        document = doc_service.get_document(doc_path)
        
        if not document:
            return jsonify({
                'success': False,
                'error': '文档不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': document
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/documents/<path:doc_path>/analysis', methods=['GET'])
def analyze_document(doc_path):
    """分析文档 - 预留接口，后期可调用C/Rust服务"""
    try:
        doc_service = DocumentService()
        document = doc_service.get_document(doc_path)
        
        if not document:
            return jsonify({
                'success': False,
                'error': '文档不存在'
            }), 404
        
        # 尝试使用外部分析服务（预留接口）
        external_analysis = try_external_analysis_service(document)
        
        if external_analysis:
            return jsonify({
                'success': True,
                'data': external_analysis,
                'source': 'external_service'
            })
        
        # 回退到本地分析
        analysis_service = AnalysisService()
        analysis = analysis_service.analyze_document(document)
        
        return jsonify({
            'success': True,
            'data': analysis,
            'source': 'local_service'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/search', methods=['GET'])
def search_documents():
    """搜索文档"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({
            'success': False,
            'error': '搜索关键词不能为空'
        }), 400
    
    try:
        doc_service = DocumentService()
        results = doc_service.search_documents(query)
        
        return jsonify({
            'success': True,
            'data': results,
            'query': query,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取全局统计信息"""
    try:
        analysis_service = AnalysisService()
        stats = analysis_service.get_global_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'obsidian_docs_web'
    })

def try_external_analysis_service(document):
    """
    尝试调用外部分析服务（预留接口）
    后期可以替换为C/Rust实现的高性能分析服务
    """
    try:
        service_url = current_app.config.get('ANALYSIS_SERVICE_URL')
        timeout = current_app.config.get('ANALYSIS_SERVICE_TIMEOUT', 30)
        
        if not service_url or service_url == 'http://localhost:8001':
            # 默认服务未启动，返回None使用本地分析
            return None
        
        # 准备请求数据
        payload = {
            'content': document.get('content', ''),
            'metadata': document.get('metadata', {}),
            'file_path': document.get('file_path', '')
        }
        
        # 调用外部服务
        response = requests.post(
            f"{service_url}/analyze",
            json=payload,
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            current_app.logger.warning(f"外部分析服务返回错误: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        current_app.logger.warning(f"外部分析服务调用失败: {str(e)}")
        return None
    except Exception as e:
        current_app.logger.error(f"外部分析服务异常: {str(e)}")
        return None 