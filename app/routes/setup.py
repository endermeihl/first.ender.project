"""
设置和初始化路由
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from app.services.config_service import ConfigService
from app.services.monitor_service import MonitorService
import os

setup_bp = Blueprint('setup', __name__)

# 全局服务实例
config_service = None
monitor_service = None

def init_services():
    """初始化服务"""
    global config_service, monitor_service
    if config_service is None:
        config_service = ConfigService()
    if monitor_service is None:
        monitor_service = MonitorService()
        monitor_service.initialize(config_service)

@setup_bp.route('/setup')
def setup_page():
    """设置页面"""
    init_services()
    
    vault_info = config_service.get_vault_info()
    monitor_status = monitor_service.get_monitor_status()
    
    return render_template('setup.html', 
                         vault_info=vault_info,
                         monitor_status=monitor_status)

@setup_bp.route('/api/setup/validate-path', methods=['POST'])
def validate_path():
    """验证路径"""
    init_services()
    
    data = request.get_json()
    path = data.get('path', '').strip()
    
    if not path:
        return jsonify({
            'valid': False,
            'message': '请输入路径'
        })
    
    result = config_service.validate_path(path)
    return jsonify(result)

@setup_bp.route('/api/setup/initialize', methods=['POST'])
def initialize_vault():
    """初始化文档库"""
    init_services()
    
    data = request.get_json()
    vault_path = data.get('vault_path', '').strip()
    
    if not vault_path:
        return jsonify({
            'success': False,
            'message': '请输入文档库路径'
        })
    
    # 初始化文档库
    result = config_service.initialize_vault(vault_path)
    
    if result['success']:
        # 重新启动监控
        monitor_service.start_monitoring(vault_path)
        
        # 更新Flask应用配置
        current_app.config['OBSIDIAN_VAULT_PATH'] = vault_path
    
    return jsonify(result)

@setup_bp.route('/api/setup/vault-info')
def get_vault_info():
    """获取文档库信息"""
    init_services()
    
    vault_info = config_service.get_vault_info()
    monitor_status = monitor_service.get_monitor_status()
    
    return jsonify({
        'vault_info': vault_info,
        'monitor_status': monitor_status
    })

@setup_bp.route('/api/setup/refresh', methods=['POST'])
def force_refresh():
    """强制刷新文档库"""
    init_services()
    
    result = monitor_service.force_refresh()
    return jsonify(result)

@setup_bp.route('/api/setup/config', methods=['GET', 'POST'])
def manage_config():
    """管理配置"""
    init_services()
    
    if request.method == 'GET':
        # 获取配置
        config = {
            'obsidian_vault_path': config_service.get('obsidian_vault_path'),
            'auto_refresh': config_service.get('auto_refresh'),
            'refresh_interval': config_service.get('refresh_interval'),
            'theme': config_service.get('theme'),
            'language': config_service.get('language')
        }
        return jsonify(config)
    
    else:
        # 更新配置
        data = request.get_json()
        
        # 更新配置项
        for key, value in data.items():
            if key in ['obsidian_vault_path', 'auto_refresh', 'refresh_interval', 'theme', 'language']:
                config_service.set(key, value)
        
        # 如果文档库路径变更，重新启动监控
        if 'obsidian_vault_path' in data:
            new_path = data['obsidian_vault_path']
            monitor_service.start_monitoring(new_path)
            current_app.config['OBSIDIAN_VAULT_PATH'] = new_path
        
        return jsonify({
            'success': True,
            'message': '配置已更新'
        })

@setup_bp.route('/api/setup/status')
def get_status():
    """获取系统状态"""
    init_services()
    
    vault_info = config_service.get_vault_info()
    monitor_status = monitor_service.get_monitor_status()
    
    # 检查系统健康状态
    health_status = {
        'config_service': config_service is not None,
        'monitor_service': monitor_service is not None,
        'vault_accessible': vault_info['exists'],
        'monitoring_active': monitor_status['monitoring']
    }
    
    return jsonify({
        'health': health_status,
        'vault_info': vault_info,
        'monitor_status': monitor_status
    }) 