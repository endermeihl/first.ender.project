"""
文档服务 - 负责读取和管理Obsidian文档
"""

import os
import re
import frontmatter
import markdown
from datetime import datetime
from typing import List, Dict, Optional
from flask import current_app

class DocumentService:
    """文档服务类"""
    
    def __init__(self):
        self._update_vault_path()
        self.md_extensions = ['.md', '.markdown']
        
    def _update_vault_path(self):
        """更新文档库路径"""
        try:
            from app.services.config_service import ConfigService
            config_service = ConfigService()
            self.vault_path = config_service.get('obsidian_vault_path', './docs')
        except Exception as e:
            current_app.logger.warning(f"无法从ConfigService读取配置，使用默认路径: {e}")
            self.vault_path = current_app.config.get('OBSIDIAN_VAULT_PATH', './docs')
        
    def get_all_documents(self) -> List[Dict]:
        """获取所有文档"""
        # 更新文档库路径
        self._update_vault_path()
        
        documents = []
        
        if not os.path.exists(self.vault_path):
            current_app.logger.warning(f"文档库路径不存在: {self.vault_path}")
            return documents
        
        for root, dirs, files in os.walk(self.vault_path):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if any(file.endswith(ext) for ext in self.md_extensions):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.vault_path)
                    
                    try:
                        document = self._parse_document(file_path, relative_path)
                        if document:
                            documents.append(document)
                    except Exception as e:
                        current_app.logger.error(f"解析文档失败 {file_path}: {str(e)}")
        
        # 按修改时间排序
        documents.sort(key=lambda x: x.get('modified_time', ''), reverse=True)
        return documents
    
    def get_document(self, doc_path: str) -> Optional[Dict]:
        """获取单个文档"""
        # 更新文档库路径
        self._update_vault_path()
        
        full_path = os.path.join(self.vault_path, doc_path)
        
        if not os.path.exists(full_path):
            return None
        
        try:
            return self._parse_document(full_path, doc_path)
        except Exception as e:
            current_app.logger.error(f"解析文档失败 {full_path}: {str(e)}")
            return None
    
    def search_documents(self, query: str) -> List[Dict]:
        """搜索文档"""
        all_docs = self.get_all_documents()
        results = []
        
        query_lower = query.lower()
        
        for doc in all_docs:
            # 搜索标题
            if query_lower in doc.get('title', '').lower():
                results.append(doc)
                continue
            
            # 搜索内容
            if query_lower in doc.get('content', '').lower():
                results.append(doc)
                continue
            
            # 搜索标签
            tags = doc.get('tags', [])
            if any(query_lower in tag.lower() for tag in tags):
                results.append(doc)
                continue
        
        return results
    
    def _parse_document(self, file_path: str, relative_path: str) -> Optional[Dict]:
        """解析单个文档"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试解析frontmatter，如果失败则使用原始内容
            try:
                post = frontmatter.loads(content)
                metadata = dict(post.metadata) if post.metadata else {}
                markdown_content = post.content
            except Exception as e:
                current_app.logger.warning(f"Frontmatter解析失败，使用原始内容 {file_path}: {str(e)}")
                metadata = {}
                markdown_content = content
            
            # 获取文件信息
            stat = os.stat(file_path)
            
            # 提取标题
            title = metadata.get('title', '')
            if not title:
                # 从文件名提取标题
                title = os.path.splitext(os.path.basename(file_path))[0]
                title = title.replace('-', ' ').replace('_', ' ').title()
            
            # 提取标签
            tags = metadata.get('tags', [])
            if isinstance(tags, str):
                tags = [tags]
            
            # 转换Markdown为HTML
            try:
                html_content = markdown.markdown(
                    markdown_content,
                    extensions=[
                        'fenced_code',
                        'tables', 
                        'toc',
                        'codehilite',
                        'nl2br',
                        'sane_lists'
                    ],
                    extension_configs={
                        'codehilite': {
                            'css_class': 'highlight',
                            'use_pygments': True,
                            'noclasses': True,
                            'linenums': False
                        }
                    }
                )
                
                # 后处理HTML，改进代码块显示
                html_content = self._post_process_html(html_content)
            except Exception as e:
                current_app.logger.warning(f"Markdown转换失败，使用原始内容 {file_path}: {str(e)}")
                html_content = f'<pre>{markdown_content}</pre>'
            
            # 提取链接
            links = self._extract_links(markdown_content)
            
            # 提取图片
            images = self._extract_images(markdown_content)
            
            document = {
                'file_path': relative_path,
                'title': title,
                'content': markdown_content,
                'html_content': html_content,
                'metadata': metadata,
                'tags': tags,
                'links': links,
                'images': images,
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'size': stat.st_size,
                'word_count': len(markdown_content.split()),
                'line_count': len(markdown_content.splitlines())
            }
            
            return document
            
        except Exception as e:
            current_app.logger.error(f"解析文档失败 {file_path}: {str(e)}")
            return None
    
    def _extract_links(self, content: str) -> List[str]:
        """提取文档中的链接"""
        # Markdown链接模式
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        return [link[1] for link in links]
    
    def _extract_images(self, content: str) -> List[str]:
        """提取文档中的图片"""
        # Markdown图片模式
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        images = re.findall(image_pattern, content)
        return [img[1] for img in images]
    
    def get_document_stats(self) -> Dict:
        """获取文档统计信息"""
        documents = self.get_all_documents()
        
        total_docs = len(documents)
        total_words = sum(doc.get('word_count', 0) for doc in documents)
        total_size = sum(doc.get('size', 0) for doc in documents)
        
        # 标签统计
        tag_counts = {}
        for doc in documents:
            for tag in doc.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 按月份统计
        monthly_stats = {}
        for doc in documents:
            modified_time = doc.get('modified_time', '')
            if modified_time:
                month = modified_time[:7]  # YYYY-MM
                monthly_stats[month] = monthly_stats.get(month, 0) + 1
        
        return {
            'total_documents': total_docs,
            'total_words': total_words,
            'total_size': total_size,
            'tag_counts': tag_counts,
            'monthly_stats': monthly_stats
        }
    
    def _post_process_html(self, html_content: str) -> str:
        """后处理HTML内容，改进代码块显示"""
        import re
        
        # 为代码块添加语言标识
        def add_language_to_code(match):
            code_block = match.group(0)
            # 检查是否已经有语言标识
            if 'class="highlight' in code_block:
                return code_block
            
            # 尝试从代码内容推断语言
            code_content = match.group(1)
            language = self._detect_language(code_content)
            
            if language:
                # 替换为带语言标识的代码块
                return f'<pre class="highlight" data-lang="{language}"><code>{code_content}</code></pre>'
            
            return code_block
        
        # 处理代码块
        html_content = re.sub(
            r'<pre><code>(.*?)</code></pre>',
            add_language_to_code,
            html_content,
            flags=re.DOTALL
        )
        
        # 改进行内代码样式
        html_content = re.sub(
            r'<code>(.*?)</code>',
            r'<code class="inline-code">\1</code>',
            html_content
        )
        
        return html_content
    
    def _detect_language(self, code_content: str) -> str:
        """检测代码语言"""
        # 简单的语言检测规则
        code_lower = code_content.lower()
        
        if any(keyword in code_lower for keyword in ['def ', 'import ', 'from ', 'class ', 'print(']):
            return 'python'
        elif any(keyword in code_lower for keyword in ['function', 'var ', 'let ', 'const ', 'console.log']):
            return 'javascript'
        elif any(keyword in code_lower for keyword in ['<?php', 'echo ', '$', 'function ']):
            return 'php'
        elif any(keyword in code_lower for keyword in ['public class', 'public static', 'System.out']):
            return 'java'
        elif any(keyword in code_lower for keyword in ['#include', 'int main', 'printf']):
            return 'c'
        elif any(keyword in code_lower for keyword in ['fn ', 'let ', 'println!', 'use ']):
            return 'rust'
        elif any(keyword in code_lower for keyword in ['package ', 'import ', 'func ']):
            return 'go'
        elif any(keyword in code_lower for keyword in ['<html', '<div', '<script']):
            return 'html'
        elif any(keyword in code_lower for keyword in ['color:', 'background:', 'margin:', 'padding:']):
            return 'css'
        elif any(keyword in code_lower for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM']):
            return 'sql'
        elif any(keyword in code_lower for keyword in ['docker', 'FROM', 'RUN', 'COPY']):
            return 'dockerfile'
        elif any(keyword in code_lower for keyword in ['version:', 'services:', 'image:']):
            return 'yaml'
        elif any(keyword in code_lower for keyword in ['{', '}', '"name"', '"version"']):
            return 'json'
        
        return 'text' 