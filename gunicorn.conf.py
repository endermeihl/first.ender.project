# Gunicorn配置文件 - 生产环境部署

import os
import multiprocessing

# 服务器配置
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
workers = os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1)
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'sync')
worker_connections = os.getenv('GUNICORN_WORKER_CONNECTIONS', 1000)

# 超时配置
timeout = os.getenv('GUNICORN_TIMEOUT', 30)
keepalive = os.getenv('GUNICORN_KEEPALIVE', 2)
graceful_timeout = os.getenv('GUNICORN_GRACEFUL_TIMEOUT', 30)

# 日志配置
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '-')
errorlog = os.getenv('GUNICORN_ERROR_LOG', '-')
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')

# 进程配置
preload_app = True
max_requests = os.getenv('GUNICORN_MAX_REQUESTS', 1000)
max_requests_jitter = os.getenv('GUNICORN_MAX_REQUESTS_JITTER', 100)

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 性能配置
backlog = 2048
forwarded_allow_ips = '*'

def when_ready(server):
    """服务器准备就绪时的回调"""
    server.log.info("🚀 Obsidian文档展示系统已启动")

def worker_int(worker):
    """工作进程中断时的回调"""
    worker.log.info("👋 工作进程正在关闭...")

def pre_fork(server, worker):
    """fork工作进程前的回调"""
    server.log.info("🔄 正在fork工作进程...")

def post_fork(server, worker):
    """fork工作进程后的回调"""
    server.log.info(f"✅ 工作进程 {worker.pid} 已启动")

def post_worker_init(worker):
    """工作进程初始化后的回调"""
    worker.log.info(f"🎯 工作进程 {worker.pid} 初始化完成") 