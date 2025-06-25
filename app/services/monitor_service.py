"""
文档监控服务 - 监控Obsidian文档变更并自动更新
"""

import os
import time
import threading
import logging
from datetime import datetime
from typing import Dict, List, Set, Callable, Any
from pathlib import Path
from flask import current_app

class DocumentMonitor:
    """文档监控器"""
    
    def __init__(self, vault_path: str, callback: Callable = None):
        self.vault_path = vault_path
        self.callback = callback
        self.running = False
        self.monitor_thread = None
        self.last_scan_time = 0
        self.file_timestamps = {}
        self.exclude_patterns = ['.git', '.obsidian', 'node_modules', '__pycache__', '.DS_Store']
        
    def start(self):
        """启动监控"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logging.info(f"文档监控已启动: {self.vault_path}")
    
    def stop(self):
        """停止监控"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        logging.info("文档监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                self._check_for_changes()
                time.sleep(5)  # 每5秒检查一次
            except Exception as e:
                logging.error(f"监控循环错误: {e}")
                time.sleep(10)  # 出错时等待更长时间
    
    def _check_for_changes(self):
        """检查文件变更"""
        if not os.path.exists(self.vault_path):
            return
        
        current_files = set()
        changes_detected = False
        
        # 扫描当前文件
        for root, dirs, files in os.walk(self.vault_path):
            # 跳过排除的目录
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.exclude_patterns)]
            
            for file in files:
                if file.endswith(('.md', '.markdown')):
                    file_path = os.path.join(root, file)
                    current_files.add(file_path)
                    
                    # 检查文件时间戳
                    try:
                        mtime = os.path.getmtime(file_path)
                        if file_path not in self.file_timestamps or self.file_timestamps[file_path] != mtime:
                            self.file_timestamps[file_path] = mtime
                            changes_detected = True
                            logging.info(f"检测到文件变更: {file_path}")
                    except OSError:
                        pass
        
        # 检查删除的文件
        deleted_files = set(self.file_timestamps.keys()) - current_files
        if deleted_files:
            for file_path in deleted_files:
                del self.file_timestamps[file_path]
                changes_detected = True
                logging.info(f"检测到文件删除: {file_path}")
        
        # 如果有变更，调用回调函数
        if changes_detected and self.callback:
            try:
                self.callback()
            except Exception as e:
                logging.error(f"回调函数执行失败: {e}")

class MonitorService:
    """监控服务类"""
    
    def __init__(self):
        self.monitors = {}
        self.config_service = None
        
    def initialize(self, config_service):
        """初始化监控服务"""
        self.config_service = config_service
        vault_path = config_service.get('obsidian_vault_path', './docs')
        self.start_monitoring(vault_path)
    
    def start_monitoring(self, vault_path: str):
        """开始监控指定路径"""
        if vault_path in self.monitors:
            self.stop_monitoring(vault_path)
        
        def refresh_callback():
            """文档变更回调函数"""
            try:
                # 清除缓存（如果有的话）
                if current_app and hasattr(current_app, 'cache'):
                    current_app.cache.clear()
                
                logging.info("文档库已更新，缓存已清除")
                
            except Exception as e:
                logging.error(f"处理文档变更失败: {e}")
        
        monitor = DocumentMonitor(vault_path, refresh_callback)
        monitor.start()
        self.monitors[vault_path] = monitor
        
        logging.info(f"开始监控文档库: {vault_path}")
    
    def stop_monitoring(self, vault_path: str):
        """停止监控指定路径"""
        if vault_path in self.monitors:
            self.monitors[vault_path].stop()
            del self.monitors[vault_path]
            logging.info(f"停止监控文档库: {vault_path}")
    
    def stop_all(self):
        """停止所有监控"""
        for vault_path in list(self.monitors.keys()):
            self.stop_monitoring(vault_path)
    
    def get_monitor_status(self) -> Dict[str, Any]:
        """获取监控状态"""
        status = {
            'monitoring': len(self.monitors) > 0,
            'monitored_paths': list(self.monitors.keys()),
            'active_monitors': len(self.monitors)
        }
        
        if self.config_service:
            status['config_path'] = self.config_service.get('obsidian_vault_path')
            status['auto_refresh'] = self.config_service.get('auto_refresh', True)
        
        return status
    
    def force_refresh(self) -> Dict[str, Any]:
        """强制刷新文档库"""
        result = {
            'success': False,
            'message': '',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if self.config_service:
                vault_path = self.config_service.get('obsidian_vault_path')
                if vault_path and os.path.exists(vault_path):
                    # 清除缓存
                    if current_app and hasattr(current_app, 'cache'):
                        current_app.cache.clear()
                    
                    result['success'] = True
                    result['message'] = f'文档库已刷新: {vault_path}'
                else:
                    result['message'] = '文档库路径无效'
            else:
                result['message'] = '配置服务未初始化'
                
        except Exception as e:
            result['message'] = f'刷新失败: {str(e)}'
            logging.error(f"强制刷新失败: {e}")
        
        return result 