"""
分析服务 - 负责文档内容分析和总结
后期可以替换为C/Rust实现的高性能分析服务
"""

import re
import jieba
import nltk
import textstat
from collections import Counter
from typing import Dict, List, Optional
from flask import current_app

# 初始化NLTK数据，如果下载失败则使用降级方案
nltk_available = True
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    stop_words = set(nltk.corpus.stopwords.words('english'))
except (LookupError, Exception) as e:
    current_app.logger.warning(f"NLTK数据不可用，使用降级方案: {e}")
    nltk_available = False
    stop_words = set()

class AnalysisService:
    """文档分析服务类"""
    
    def __init__(self):
        self.stop_words = stop_words
        # 添加中文停用词
        self.stop_words.update(['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'])
    
    def analyze_document(self, document: Dict) -> Dict:
        """分析单个文档"""
        content = document.get('content', '')
        
        analysis = {
            'basic_stats': self._get_basic_stats(content),
            'readability': self._analyze_readability(content),
            'keywords': self._extract_keywords(content),
            'sentiment': self._analyze_sentiment(content),
            'topics': self._extract_topics(content),
            'summary': self._generate_summary(content),
            'structure': self._analyze_structure(content)
        }
        
        return analysis
    
    def get_global_statistics(self) -> Dict:
        """获取全局统计信息"""
        from app.services.document_service import DocumentService
        
        doc_service = DocumentService()
        documents = doc_service.get_all_documents()
        
        # 基础统计
        total_docs = len(documents)
        total_words = sum(doc.get('word_count', 0) for doc in documents)
        total_size = sum(doc.get('size', 0) for doc in documents)
        
        # 标签统计
        all_tags = []
        for doc in documents:
            all_tags.extend(doc.get('tags', []))
        tag_counts = Counter(all_tags)
        
        # 按月份统计
        monthly_stats = {}
        for doc in documents:
            modified_time = doc.get('modified_time', '')
            if modified_time:
                month = modified_time[:7]
                monthly_stats[month] = monthly_stats.get(month, 0) + 1
        
        # 平均可读性
        readability_scores = []
        for doc in documents:
            analysis = self.analyze_document(doc)
            readability = analysis.get('readability', {})
            if readability.get('flesch_reading_ease'):
                readability_scores.append(readability['flesch_reading_ease'])
        
        avg_readability = sum(readability_scores) / len(readability_scores) if readability_scores else 0
        
        return {
            'total_documents': total_docs,
            'total_words': total_words,
            'total_size': total_size,
            'average_readability': round(avg_readability, 2),
            'top_tags': dict(tag_counts.most_common(10)),
            'monthly_stats': monthly_stats,
            'document_types': self._analyze_document_types(documents)
        }
    
    def _get_basic_stats(self, content: str) -> Dict:
        """获取基础统计信息"""
        words = content.split()
        
        # 使用NLTK或简单的句子分割
        if nltk_available:
            try:
                sentences = nltk.sent_tokenize(content)
            except:
                sentences = self._simple_sentence_split(content)
        else:
            sentences = self._simple_sentence_split(content)
        
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'paragraph_count': len(paragraphs),
            'character_count': len(content),
            'average_sentence_length': len(words) / len(sentences) if sentences else 0,
            'average_paragraph_length': len(words) / len(paragraphs) if paragraphs else 0
        }
    
    def _simple_sentence_split(self, text: str) -> List[str]:
        """简单的句子分割（降级方案）"""
        # 使用常见的句子结束符分割
        sentence_endings = r'[.!?。！？\n]+'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _analyze_readability(self, content: str) -> Dict:
        """分析可读性"""
        try:
            return {
                'flesch_reading_ease': textstat.flesch_reading_ease(content),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(content),
                'gunning_fog': textstat.gunning_fog(content),
                'smog_index': textstat.smog_index(content),
                'automated_readability_index': textstat.automated_readability_index(content),
                'coleman_liau_index': textstat.coleman_liau_index(content),
                'linsear_write_formula': textstat.linsear_write_formula(content),
                'dale_chall_readability_score': textstat.dale_chall_readability_score(content)
            }
        except Exception as e:
            current_app.logger.warning(f"可读性分析失败: {str(e)}")
            return {}
    
    def _extract_keywords(self, content: str, top_n: int = 10) -> List[Dict]:
        """提取关键词"""
        try:
            # 分词
            words = jieba.cut(content)
            
            # 过滤停用词和短词
            filtered_words = [
                word for word in words 
                if len(word) > 1 and word.lower() not in self.stop_words
            ]
            
            # 统计词频
            word_counts = Counter(filtered_words)
            
            # 返回前N个关键词
            keywords = []
            for word, count in word_counts.most_common(top_n):
                keywords.append({
                    'word': word,
                    'count': count,
                    'frequency': count / len(filtered_words) if filtered_words else 0
                })
            
            return keywords
        except Exception as e:
            current_app.logger.warning(f"关键词提取失败: {str(e)}")
            return []
    
    def _analyze_sentiment(self, content: str) -> Dict:
        """分析情感倾向（简化版）"""
        # 简单的情感词统计
        positive_words = ['好', '优秀', '棒', '喜欢', '爱', '开心', '快乐', '成功', '满意', '精彩']
        negative_words = ['坏', '糟糕', '讨厌', '恨', '难过', '痛苦', '失败', '失望', '无聊', '困难']
        
        content_lower = content.lower()
        positive_count = sum(content_lower.count(word) for word in positive_words)
        negative_count = sum(content_lower.count(word) for word in negative_words)
        
        total_words = len(content.split())
        positive_ratio = positive_count / total_words if total_words > 0 else 0
        negative_ratio = negative_count / total_words if total_words > 0 else 0
        
        # 计算情感得分 (-1 到 1)
        sentiment_score = positive_ratio - negative_ratio
        
        return {
            'positive_words': positive_count,
            'negative_words': negative_count,
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio,
            'sentiment_score': sentiment_score,
            'sentiment_label': self._get_sentiment_label(sentiment_score)
        }
    
    def _get_sentiment_label(self, score: float) -> str:
        """获取情感标签"""
        if score > 0.1:
            return '积极'
        elif score < -0.1:
            return '消极'
        else:
            return '中性'
    
    def _extract_topics(self, content: str) -> List[str]:
        """提取主题（简化版）"""
        # 基于关键词和标题提取主题
        keywords = self._extract_keywords(content, 5)
        topics = [kw['word'] for kw in keywords]
        
        # 添加一些常见主题
        common_topics = ['技术', '学习', '工作', '生活', '思考', '笔记', '总结']
        for topic in common_topics:
            if topic in content:
                topics.append(topic)
        
        return list(set(topics))[:5]  # 去重并限制数量
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """生成文档摘要"""
        # 简单的摘要生成：选择前几句话
        sentences = nltk.sent_tokenize(content)
        
        if not sentences:
            return ""
        
        # 选择前3句话作为摘要
        summary_sentences = sentences[:3]
        summary = ' '.join(summary_sentences)
        
        # 如果摘要太长，截断
        if len(summary) > max_length:
            summary = summary[:max_length] + '...'
        
        return summary
    
    def _analyze_structure(self, content: str) -> Dict:
        """分析文档结构"""
        lines = content.split('\n')
        
        # 统计标题层级
        headers = {
            'h1': len([line for line in lines if line.startswith('# ')]),
            'h2': len([line for line in lines if line.startswith('## ')]),
            'h3': len([line for line in lines if line.startswith('### ')]),
            'h4': len([line for line in lines if line.startswith('#### ')])
        }
        
        # 统计代码块
        code_blocks = len(re.findall(r'```[\s\S]*?```', content))
        
        # 统计列表
        bullet_lists = len([line for line in lines if line.strip().startswith(('-', '*', '+'))])
        numbered_lists = len([line for line in lines if re.match(r'^\d+\.', line.strip())])
        
        return {
            'headers': headers,
            'code_blocks': code_blocks,
            'bullet_lists': bullet_lists,
            'numbered_lists': numbered_lists,
            'total_sections': sum(headers.values())
        }
    
    def _analyze_document_types(self, documents: List[Dict]) -> Dict:
        """分析文档类型分布"""
        doc_types = {}
        
        for doc in documents:
            # 基于标签和内容判断文档类型
            tags = doc.get('tags', [])
            content = doc.get('content', '')
            
            doc_type = '其他'
            
            # 根据标签判断类型
            if any(tag in ['技术', '编程', '代码'] for tag in tags):
                doc_type = '技术文档'
            elif any(tag in ['学习', '笔记', '总结'] for tag in tags):
                doc_type = '学习笔记'
            elif any(tag in ['工作', '项目', '任务'] for tag in tags):
                doc_type = '工作文档'
            elif any(tag in ['生活', '日记', '随笔'] for tag in tags):
                doc_type = '生活记录'
            
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        return doc_types 