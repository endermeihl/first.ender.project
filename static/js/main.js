/**
 * Obsidian文档展示系统 - 主要JavaScript文件
 */

// 全局变量
let currentDocument = null;
let analysisData = null;

// 工具函数
const utils = {
    // 格式化日期
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // 格式化文件大小
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // 防抖函数
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // 显示加载状态
    showLoading: function(element) {
        element.innerHTML = '<div class="loading"></div> 加载中...';
    },
    
    // 隐藏加载状态
    hideLoading: function(element) {
        element.innerHTML = '';
    },
    
    // 显示通知
    showNotification: function(message, type = 'info') {
        const alertClass = `alert-${type}`;
        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('main .container');
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // 自动隐藏
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
};

// 文档相关功能
const documentManager = {
    // 加载文档
    loadDocument: async function(docPath) {
        try {
            const response = await fetch(`/api/documents/${encodeURIComponent(docPath)}`);
            const data = await response.json();
            
            if (data.success) {
                currentDocument = data.data;
                this.displayDocument(currentDocument);
                return currentDocument;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('加载文档失败:', error);
            utils.showNotification('加载文档失败: ' + error.message, 'danger');
            return null;
        }
    },
    
    // 显示文档
    displayDocument: function(document) {
        const contentContainer = document.querySelector('.document-content');
        if (!contentContainer) return;
        
        // 更新页面标题
        document.title = `${document.title} - Obsidian文档展示系统`;
        
        // 显示文档内容
        contentContainer.innerHTML = document.html_content;
        
        // 高亮代码块
        if (window.Prism) {
            Prism.highlightAll();
        }
        
        // 显示文档元信息
        this.displayDocumentMeta(document);
    },
    
    // 显示文档元信息
    displayDocumentMeta: function(document) {
        const metaContainer = document.querySelector('.document-meta');
        if (!metaContainer) return;
        
        const metaHtml = `
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0"><i class="fas fa-info-circle me-2"></i>文档信息</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>创建时间:</strong> ${utils.formatDate(document.created_time)}</p>
                            <p><strong>修改时间:</strong> ${utils.formatDate(document.modified_time)}</p>
                            <p><strong>文件大小:</strong> ${utils.formatFileSize(document.size)}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>字数:</strong> ${document.word_count}</p>
                            <p><strong>行数:</strong> ${document.line_count}</p>
                            <p><strong>链接数:</strong> ${document.links.length}</p>
                        </div>
                    </div>
                    ${document.tags.length > 0 ? `
                        <div class="mt-3">
                            <strong>标签:</strong>
                            ${document.tags.map(tag => `<span class="badge bg-secondary me-1">${tag}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        metaContainer.innerHTML = metaHtml;
    }
};

// 分析相关功能
const analysisManager = {
    // 加载文档分析
    loadAnalysis: async function(docPath) {
        try {
            const response = await fetch(`/api/documents/${encodeURIComponent(docPath)}/analysis`);
            const data = await response.json();
            
            if (data.success) {
                analysisData = data.data;
                this.displayAnalysis(analysisData);
                return analysisData;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('加载分析失败:', error);
            utils.showNotification('加载分析失败: ' + error.message, 'danger');
            return null;
        }
    },
    
    // 显示分析结果
    displayAnalysis: function(analysis) {
        const analysisContainer = document.querySelector('.analysis-results');
        if (!analysisContainer) return;
        
        const analysisHtml = `
            <div class="row">
                <div class="col-md-6">
                    <div class="analysis-panel">
                        <h5><i class="fas fa-chart-bar me-2"></i>基础统计</h5>
                        <div class="row">
                            <div class="col-6">
                                <p><strong>字数:</strong> ${analysis.basic_stats.word_count}</p>
                                <p><strong>句子数:</strong> ${analysis.basic_stats.sentence_count}</p>
                                <p><strong>段落数:</strong> ${analysis.basic_stats.paragraph_count}</p>
                            </div>
                            <div class="col-6">
                                <p><strong>平均句长:</strong> ${analysis.basic_stats.average_sentence_length.toFixed(1)}</p>
                                <p><strong>平均段长:</strong> ${analysis.basic_stats.average_paragraph_length.toFixed(1)}</p>
                                <p><strong>字符数:</strong> ${analysis.basic_stats.character_count}</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="analysis-panel">
                        <h5><i class="fas fa-brain me-2"></i>可读性分析</h5>
                        ${this.renderReadability(analysis.readability)}
                    </div>
                </div>
            </div>
            
            <div class="row mt-3">
                <div class="col-md-6">
                    <div class="analysis-panel">
                        <h5><i class="fas fa-tags me-2"></i>关键词</h5>
                        <div class="keyword-cloud">
                            ${analysis.keywords.map(kw => `
                                <div class="keyword-item">
                                    ${kw.word}
                                    <span class="keyword-count">${kw.count}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="analysis-panel">
                        <h5><i class="fas fa-smile me-2"></i>情感分析</h5>
                        ${this.renderSentiment(analysis.sentiment)}
                    </div>
                </div>
            </div>
            
            <div class="row mt-3">
                <div class="col-12">
                    <div class="analysis-panel">
                        <h5><i class="fas fa-file-alt me-2"></i>文档摘要</h5>
                        <p class="lead">${analysis.summary}</p>
                    </div>
                </div>
            </div>
        `;
        
        analysisContainer.innerHTML = analysisHtml;
    },
    
    // 渲染可读性分析
    renderReadability: function(readability) {
        if (!readability || Object.keys(readability).length === 0) {
            return '<p class="text-muted">暂无数据</p>';
        }
        
        return `
            <p><strong>Flesch可读性:</strong> ${readability.flesch_reading_ease?.toFixed(1) || 'N/A'}</p>
            <p><strong>Flesch-Kincaid等级:</strong> ${readability.flesch_kincaid_grade?.toFixed(1) || 'N/A'}</p>
            <p><strong>Gunning Fog指数:</strong> ${readability.gunning_fog?.toFixed(1) || 'N/A'}</p>
        `;
    },
    
    // 渲染情感分析
    renderSentiment: function(sentiment) {
        if (!sentiment) return '<p class="text-muted">暂无数据</p>';
        
        const sentimentClass = sentiment.sentiment_label === '积极' ? 'success' : 
                              sentiment.sentiment_label === '消极' ? 'danger' : 'secondary';
        
        return `
            <p><strong>情感倾向:</strong> <span class="badge bg-${sentimentClass}">${sentiment.sentiment_label}</span></p>
            <p><strong>积极词数:</strong> ${sentiment.positive_words}</p>
            <p><strong>消极词数:</strong> ${sentiment.negative_words}</p>
            <p><strong>情感得分:</strong> ${sentiment.sentiment_score.toFixed(3)}</p>
        `;
    }
};

// 搜索功能
const searchManager = {
    // 搜索文档
    search: async function(query) {
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.success) {
                this.displaySearchResults(data.data, query);
                return data.data;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('搜索失败:', error);
            utils.showNotification('搜索失败: ' + error.message, 'danger');
            return [];
        }
    },
    
    // 显示搜索结果
    displaySearchResults: function(results, query) {
        const resultsContainer = document.querySelector('.search-results');
        if (!resultsContainer) return;
        
        if (results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    未找到包含 "${query}" 的文档
                </div>
            `;
            return;
        }
        
        const resultsHtml = `
            <div class="alert alert-success">
                <i class="fas fa-search me-2"></i>
                找到 ${results.length} 个包含 "${query}" 的文档
            </div>
            <div class="list-group">
                ${results.map(doc => `
                    <a href="/doc/${encodeURIComponent(doc.file_path)}" class="list-group-item list-group-item-action">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${doc.title}</h6>
                            <small class="text-muted">${utils.formatDate(doc.modified_time)}</small>
                        </div>
                        <p class="mb-1 text-muted">${doc.content.substring(0, 200)}...</p>
                        ${doc.tags.length > 0 ? `
                            <small class="text-muted">
                                ${doc.tags.map(tag => `<span class="badge bg-secondary me-1">${tag}</span>`).join('')}
                            </small>
                        ` : ''}
                    </a>
                `).join('')}
            </div>
        `;
        
        resultsContainer.innerHTML = resultsHtml;
    }
};

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('Obsidian文档展示系统已加载');
    
    // 初始化搜索功能
    const searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = this.querySelector('input[name="q"]').value.trim();
            if (query) {
                searchManager.search(query);
            }
        });
    }
    
    // 初始化文档页面
    const docPath = document.querySelector('[data-doc-path]')?.dataset.docPath;
    if (docPath) {
        documentManager.loadDocument(docPath).then(() => {
            analysisManager.loadAnalysis(docPath);
        });
    }
    
    // 初始化图表
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
});

// 初始化图表
function initializeCharts() {
    // 标签分布图表
    const tagChartCanvas = document.getElementById('tagChart');
    if (tagChartCanvas) {
        fetch('/api/statistics')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.data.top_tags) {
                    const ctx = tagChartCanvas.getContext('2d');
                    new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: Object.keys(data.data.top_tags),
                            datasets: [{
                                data: Object.values(data.data.top_tags),
                                backgroundColor: [
                                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                                ]
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: {
                                    position: 'bottom'
                                },
                                title: {
                                    display: true,
                                    text: '标签分布'
                                }
                            }
                        }
                    });
                }
            });
    }
    
    // 月度统计图表
    const monthlyChartCanvas = document.getElementById('monthlyChart');
    if (monthlyChartCanvas) {
        fetch('/api/statistics')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.data.monthly_stats) {
                    const ctx = monthlyChartCanvas.getContext('2d');
                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: Object.keys(data.data.monthly_stats),
                            datasets: [{
                                label: '文档数量',
                                data: Object.values(data.data.monthly_stats),
                                borderColor: '#36A2EB',
                                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                                tension: 0.1
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                title: {
                                    display: true,
                                    text: '月度文档统计'
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                }
            });
    }
} 