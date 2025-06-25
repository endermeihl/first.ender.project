"""
配置服务 - 管理系统配置和初始化
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from flask import current_app

class ConfigService:
    """配置服务类"""
    
    def __init__(self):
        self.config_file = 'config.json'
        self.default_config = {
            'obsidian_vault_path': './docs',
            'auto_refresh': True,
            'refresh_interval': 30,  # 秒
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'supported_extensions': ['.md', '.markdown'],
            'exclude_patterns': ['.git', '.obsidian', 'node_modules', '__pycache__'],
            'theme': 'light',
            'language': 'zh-CN'
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in self.default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                return self.default_config.copy()
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
            return self.default_config.copy()
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置值"""
        self.config[key] = value
        return self.save_config()
    
    def initialize_vault(self, vault_path: str) -> Dict[str, Any]:
        """初始化Obsidian文档库"""
        result = {
            'success': False,
            'message': '',
            'stats': {}
        }
        
        try:
            # 验证路径
            if not os.path.exists(vault_path):
                result['message'] = f'路径不存在: {vault_path}'
                return result
            
            # 检查是否包含Markdown文件
            md_files = []
            for root, dirs, files in os.walk(vault_path):
                # 跳过隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if file.endswith(('.md', '.markdown')):
                        md_files.append(os.path.join(root, file))
            
            if not md_files:
                result['message'] = f'在路径 {vault_path} 中未找到Markdown文件'
                return result
            
            # 更新配置
            self.set('obsidian_vault_path', vault_path)
            
            # 更新Flask应用配置
            if current_app:
                current_app.config['OBSIDIAN_VAULT_PATH'] = vault_path
            
            # 统计信息
            result['stats'] = {
                'total_files': len(md_files),
                'vault_path': vault_path,
                'sample_files': md_files[:5]  # 前5个文件作为示例
            }
            
            result['success'] = True
            result['message'] = f'成功初始化文档库，找到 {len(md_files)} 个Markdown文件'
            
        except Exception as e:
            result['message'] = f'初始化失败: {str(e)}'
            logging.error(f"初始化文档库失败: {e}")
        
        return result
    
    def get_vault_info(self) -> Dict[str, Any]:
        """获取文档库信息"""
        vault_path = self.get('obsidian_vault_path', './docs')
        
        info = {
            'vault_path': vault_path,
            'exists': os.path.exists(vault_path),
            'total_files': 0,
            'last_scan': None,
            'auto_refresh': self.get('auto_refresh', True)
        }
        
        if info['exists']:
            try:
                md_files = []
                for root, dirs, files in os.walk(vault_path):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for file in files:
                        if file.endswith(('.md', '.markdown')):
                            md_files.append(os.path.join(root, file))
                
                info['total_files'] = len(md_files)
                info['last_scan'] = os.path.getmtime(vault_path) if md_files else None
                
            except Exception as e:
                logging.error(f"扫描文档库失败: {e}")
        
        return info
    
    def validate_path(self, path: str) -> Dict[str, Any]:
        """验证路径是否有效"""
        result = {
            'valid': False,
            'message': '',
            'stats': {}
        }
        
        try:
            if not os.path.exists(path):
                result['message'] = '路径不存在'
                return result
            
            if not os.path.isdir(path):
                result['message'] = '路径不是目录'
                return result
            
            # 检查是否包含Markdown文件
            md_count = 0
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if file.endswith(('.md', '.markdown')):
                        md_count += 1
                        if md_count >= 10:  # 只检查前10个文件
                            break
                if md_count >= 10:
                    break
            
            if md_count == 0:
                result['message'] = '目录中未找到Markdown文件'
                return result
            
            result['valid'] = True
            result['message'] = f'路径有效，找到至少 {md_count} 个Markdown文件'
            result['stats'] = {
                'md_files_found': md_count,
                'path': path
            }
            
        except Exception as e:
            result['message'] = f'验证失败: {str(e)}'
        
        return result 