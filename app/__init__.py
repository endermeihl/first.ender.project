"""
Obsidian文档展示与分析系统 - Flask应用初始化
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

def create_app(config_name=None):
    """创建Flask应用实例"""
    
    # 加载环境变量
    load_dotenv()
    
    # 创建应用实例，明确指定静态文件路径
    app = Flask(__name__, 
                static_folder='../static',
                static_url_path='/static')
    
    # 配置应用
    configure_app(app)
    
    # 初始化扩展
    init_extensions(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 配置日志
    setup_logging(app)
    
    return app

def configure_app(app):
    """配置应用"""
    
    # 基础配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Obsidian文档路径
    app.config['OBSIDIAN_VAULT_PATH'] = os.getenv('OBSIDIAN_VAULT_PATH', './docs')
    
    # 分析服务配置
    app.config['ANALYSIS_SERVICE_URL'] = os.getenv('ANALYSIS_SERVICE_URL', 'http://localhost:8001')
    app.config['ANALYSIS_SERVICE_TIMEOUT'] = int(os.getenv('ANALYSIS_SERVICE_TIMEOUT', 30))
    
    # 数据库配置
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///obsidian_docs.db')
    
    # 缓存配置
    app.config['CACHE_TYPE'] = os.getenv('CACHE_TYPE', 'simple')
    app.config['CACHE_DEFAULT_TIMEOUT'] = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))

def init_extensions(app):
    """初始化Flask扩展"""
    
    # 启用CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

def register_blueprints(app):
    """注册蓝图"""
    
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.setup import setup_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(setup_bp)
    
    # 初始化监控服务
    init_monitor_service(app)

def init_monitor_service(app):
    """初始化监控服务"""
    try:
        from app.services.config_service import ConfigService
        from app.services.monitor_service import MonitorService
        
        config_service = ConfigService()
        monitor_service = MonitorService()
        monitor_service.initialize(config_service)
        
        # 将服务实例存储到应用上下文中
        app.config_service = config_service
        app.monitor_service = monitor_service
        
        app.logger.info('监控服务初始化完成')
        
    except Exception as e:
        app.logger.error(f'监控服务初始化失败: {e}')

def setup_logging(app):
    """配置日志"""
    
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'logs/app.log')
    
    # 创建日志目录
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置日志格式
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    app.logger.info('应用启动完成') 