// API 基础地址
const API_BASE = '';

// 全局状态
let currentMessages = [];
let currentMediaList = []; // 改为数组，支持多个媒体文件
let isGenerating = false; // 是否正在生成
let abortController = null; // 用于取消请求

// DOM 元素
const elements = {
    // 导航
    navBtns: document.querySelectorAll('.nav-btn'),
    tabContents: document.querySelectorAll('.tab-content'),
    
    // 对话
    modelSelect: document.getElementById('model-select'),
    temperature: document.getElementById('temperature'),
    maxTokens: document.getElementById('max-tokens'),
    topP: document.getElementById('top-p'),
    presencePenalty: document.getElementById('presence-penalty'),
    frequencyPenalty: document.getElementById('frequency-penalty'),
    tempValue: document.getElementById('temp-value'),
    tokensValue: document.getElementById('tokens-value'),
    topPValue: document.getElementById('top-p-value'),
    presenceValue: document.getElementById('presence-value'),
    frequencyValue: document.getElementById('frequency-value'),
    toolsCheckboxes: document.getElementById('tools-checkboxes'),
    mediaUpload: document.getElementById('media-upload'),
    mediaPreview: document.getElementById('media-preview'),
    chatMessages: document.getElementById('chat-messages'),
    userInput: document.getElementById('user-input'),
    sendBtn: document.getElementById('send-btn'),
    clearChat: document.getElementById('clear-chat'),
    
    // 模型管理
    modelsList: document.getElementById('models-list'),
    addModelBtn: document.getElementById('add-model-btn'),
    modelModal: document.getElementById('model-modal'),
    editModelModal: document.getElementById('edit-model-modal'),
    newModelName: document.getElementById('new-model-name'),
    newModelActualName: document.getElementById('new-model-actual-name'),
    newModelUrl: document.getElementById('new-model-url'),
    newModelKey: document.getElementById('new-model-key'),
    newModelType: document.getElementById('new-model-type'),
    testModelBtn: document.getElementById('test-model-btn'),
    saveModelBtn: document.getElementById('save-model-btn'),
    modelTestResult: document.getElementById('model-test-result'),
    editModelName: document.getElementById('edit-model-name'),
    editModelSystemPrompt: document.getElementById('edit-model-system-prompt'),
    updateModelBtn: document.getElementById('update-model-btn'),
    
    // 工具管理
    toolsList: document.getElementById('tools-list'),
    addToolBtn: document.getElementById('add-tool-btn'),
    toolModal: document.getElementById('tool-modal'),
    autoParseTools: document.getElementById('auto-parse-tools'),
    newToolType: document.getElementById('new-tool-type'),
    // 内置工具
    builtinToolSection: document.getElementById('builtin-tool-section'),
    builtinToolSelect: document.getElementById('builtin-tool-select'),
    builtinToolInfo: document.getElementById('builtin-tool-info'),
    // API工具
    apiToolSection: document.getElementById('api-tool-section'),
    apiToolName: document.getElementById('api-tool-name'),
    apiToolDescription: document.getElementById('api-tool-description'),
    apiToolUrl: document.getElementById('api-tool-url'),
    apiToolMethod: document.getElementById('api-tool-method'),
    apiToolHeaders: document.getElementById('api-tool-headers'),
    apiToolParameters: document.getElementById('api-tool-parameters'),
    // 代码工具
    codeToolSection: document.getElementById('code-tool-section'),
    codeToolName: document.getElementById('code-tool-name'),
    codeToolDescription: document.getElementById('code-tool-description'),
    codeToolCode: document.getElementById('code-tool-code'),
    codeToolParameters: document.getElementById('code-tool-parameters'),
    saveToolBtn: document.getElementById('save-tool-btn'),
};

// ==================== 初始化 ====================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initSliders();
    initChat();
    initModals();
    initToolForm();
    loadModels();
    loadTools();
    loadBuiltinTools();
});

// ==================== 导航 ====================

function initNavigation() {
    elements.navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            
            // 更新导航按钮状态
            elements.navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // 切换内容
            elements.tabContents.forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${tab}-tab`).classList.add('active');
        });
    });
}

// ==================== 滑块 ====================

function initSliders() {
    elements.temperature.addEventListener('input', (e) => {
        elements.tempValue.textContent = parseFloat(e.target.value).toFixed(2);
    });
    
    elements.maxTokens.addEventListener('input', (e) => {
        elements.tokensValue.textContent = e.target.value;
    });
    
    elements.topP.addEventListener('input', (e) => {
        elements.topPValue.textContent = parseFloat(e.target.value).toFixed(2);
    });
    
    elements.presencePenalty.addEventListener('input', (e) => {
        elements.presenceValue.textContent = parseFloat(e.target.value).toFixed(1);
    });
    
    elements.frequencyPenalty.addEventListener('input', (e) => {
        elements.frequencyValue.textContent = parseFloat(e.target.value).toFixed(1);
    });
}

// ==================== 对话功能 ====================

function initChat() {
    elements.sendBtn.addEventListener('click', sendMessage);
    elements.userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            // 如果正在生成，阻止发送
            if (!isGenerating) {
                sendMessage();
            }
        }
    });
    elements.clearChat.addEventListener('click', clearChat);
    elements.mediaUpload.addEventListener('change', handleMediaUpload);
}

function stopGeneration() {
    if (abortController) {
        abortController.abort();
        isGenerating = false;
        elements.sendBtn.textContent = '发送';
        elements.sendBtn.classList.remove('generating');
        elements.sendBtn.onclick = null;
        
        const inputArea = elements.sendBtn.closest('.chat-input-area');
        if (inputArea) {
            inputArea.classList.remove('generating');
        }
        elements.userInput.disabled = false;
    }
}

async function sendMessage() {
    const message = elements.userInput.value.trim();
    if (!message && currentMediaList.length === 0) return;
    
    const modelId = elements.modelSelect.value;
    if (!modelId) {
        alert('请先选择一个模型');
        return;
    }
    
    // 如果正在生成，不允许发送
    if (isGenerating) {
        return;
    }
    
    // 标记为生成中
    isGenerating = true;
    
    // 创建新的 AbortController
    abortController = new AbortController();
    
    // 更新发送按钮为暂停按钮
    elements.sendBtn.textContent = '⏸ 暂停';
    elements.sendBtn.classList.add('generating');
    elements.sendBtn.onclick = stopGeneration;
    
    // 禁用输入区域
    const inputArea = elements.sendBtn.closest('.chat-input-area');
    if (inputArea) {
        inputArea.classList.add('generating');
    }
    elements.userInput.disabled = true;
    
    // 构造用户消息
    const userMessage = {
        role: 'user',
        content: message
    };
    
    // 如果有媒体，添加到消息中
    if (currentMediaList.length > 0) {
        const contentArray = [{ type: 'text', text: message }];
        
        // 添加所有媒体
        currentMediaList.forEach(media => {
            const mediaType = media.type === 'video' ? 'video' : 'image';
            contentArray.push({
                type: `${mediaType}_url`,
                [`${mediaType}_url`]: {
                    url: `data:${mediaType}/${media.type === 'video' ? 'mp4' : 'jpeg'};base64,${media.base64}`
                }
            });
        });
        
        userMessage.content = contentArray;
    }
    
    currentMessages.push(userMessage);
    
    // 移除待发送媒体显示
    const pendingMedia = elements.chatMessages.querySelector('.pending-media-container');
    if (pendingMedia) pendingMedia.remove();
    
    // 显示用户消息（传递整个媒体列表）
    appendMessage('user', message, currentMediaList);
    elements.userInput.value = '';
    currentMediaList = [];
    elements.mediaPreview.innerHTML = '';
    
    // 获取启用的工具
    const enabledTools = Array.from(
        elements.toolsCheckboxes.querySelectorAll('input[type="checkbox"]:checked')
    ).map(cb => cb.value);
    
    // 获取参数
    const params = {
        temperature: parseFloat(elements.temperature.value),
        max_tokens: parseInt(elements.maxTokens.value),
        top_p: parseFloat(elements.topP.value),
        presence_penalty: parseFloat(elements.presencePenalty.value),
        frequency_penalty: parseFloat(elements.frequencyPenalty.value)
    };
    
    // 创建助手消息容器
    const assistantMessageDiv = appendMessage('assistant', '');
    const messageBody = assistantMessageDiv.querySelector('.message-body');
    const statusDiv = messageBody.querySelector('.message-status');
    const contentDiv = messageBody.querySelector('.message-content');
    const textDiv = contentDiv.querySelector('.message-text') || document.createElement('div');
    textDiv.className = 'message-text';
    if (!contentDiv.querySelector('.message-text')) {
        contentDiv.appendChild(textDiv);
    }
    
    let thinkingDiv = null;
    let fullContent = '';
    let buffer = '';  // 用于缓存内容，处理 <think> 标签
    
    try {
        // 检查是否启用自动解析
        const autoParseEnabled = elements.autoParseTools && elements.autoParseTools.checked;
        const endpoint = autoParseEnabled ? '/api/chat/mcp' : '/api/chat/stream';
        
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model_id: modelId,
                messages: currentMessages,
                enabled_tools: enabledTools,
                params: params,
                auto_parse: autoParseEnabled
            }),
            signal: abortController.signal
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (!line.trim() || !line.startsWith('data: ')) continue;
                
                const data = line.slice(6);
                if (data === '[DONE]') continue;
                
                try {
                    const parsed = JSON.parse(data);
                    
                    // 处理MCP特有事件
                    if (autoParseEnabled) {
                        handleMCPEvent(parsed, messageBody, statusDiv, textDiv, thinkingDiv, contentDiv);
                        // MCP事件也包含普通事件，继续处理
                    }
                    
                    if (parsed.type === 'status') {
                        // 更新状态
                        if (parsed.status === 'thinking') {
                            statusDiv.textContent = '🤔 thinking...';
                            statusDiv.style.color = '#999';
                            if (!thinkingDiv) {
                                thinkingDiv = document.createElement('div');
                                thinkingDiv.className = 'message-thinking';
                                contentDiv.insertBefore(thinkingDiv, textDiv);
                            }
                        } else if (parsed.status === 'function_calling') {
                            statusDiv.textContent = '🔧 function calling...';
                            statusDiv.style.color = '#999';
                        } else if (parsed.status === 'answering') {
                            statusDiv.textContent = '💬 answering...';
                            statusDiv.style.color = '#999';
                        } else if (parsed.status === 'error') {
                            statusDiv.textContent = 'error';
                            statusDiv.style.color = '#ff4b4b';
                        }
                    } else if (parsed.type === 'error') {
                        // 显示错误信息
                        statusDiv.textContent = 'error';
                        statusDiv.style.color = '#ff4b4b';
                        textDiv.textContent = parsed.error;
                        textDiv.style.color = '#ff4b4b';
                        if (thinkingDiv) {
                            thinkingDiv.remove();
                            thinkingDiv = null;
                        }
                    } else if (parsed.type === 'content') {
                        // 接收流式内容，需要解析 <think></think> 标签
                        buffer += parsed.content;
                        
                        // 尝试解析 buffer 中的内容
                        const result = parseThinkingContent(buffer);
                        
                        // 显示 thinking 内容
                        if (result.thinking && thinkingDiv) {
                            thinkingDiv.textContent = result.thinking;
                            thinkingDiv.style.display = 'block';
                        }
                        
                        // 显示正常内容
                        if (result.content) {
                            fullContent = result.content;
                            textDiv.textContent = fullContent;
                        }
                        
                        // 如果 thinking 已完成，隐藏 thinking div
                        if (result.thinkingComplete && thinkingDiv) {
                            thinkingDiv.style.display = 'none';
                        }
                        
                        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
                    } else if (parsed.type === 'done') {
                        // 完成，移除状态和thinking（除非是错误状态）
                        if (statusDiv.textContent !== 'error') {
                            statusDiv.remove();
                        }
                        if (thinkingDiv && statusDiv.textContent !== 'error') {
                            thinkingDiv.remove();
                        }
                        
                        // 如果启用了自动解析工具调用，尝试解析并执行
                        // 注意：在MCP模式下不需要这个，因为MCP已经处理了
                        if (!autoParseEnabled && elements.autoParseTools && elements.autoParseTools.checked && fullContent) {
                            await autoParseAndExecuteTools(fullContent, textDiv, assistantMessageDiv);
                        }
                    }
                } catch (e) {
                    console.error('解析错误:', e);
                }
            }
        }
        
        // 保存到消息历史
        const assistantMessage = {
            role: 'assistant',
            content: fullContent
        };
        currentMessages.push(assistantMessage);
        
    } catch (error) {
        // 如果是主动取消，不显示错误
        if (error.name === 'AbortError') {
            statusDiv.textContent = '⏹ 已暂停';
            statusDiv.style.color = '#999';
        } else {
            // 显示错误
            statusDiv.textContent = 'error';
            statusDiv.style.color = '#ff4b4b';
            textDiv.textContent = `❌ ${error.message}`;
            textDiv.style.color = '#ff4b4b';
        }
        if (thinkingDiv) {
            thinkingDiv.remove();
        }
    } finally {
        // 恢复发送按钮和输入区域
        isGenerating = false;
        elements.sendBtn.textContent = '发送';
        elements.sendBtn.classList.remove('generating');
        elements.sendBtn.onclick = null;
        elements.sendBtn.disabled = false;
        
        const inputArea = elements.sendBtn.closest('.chat-input-area');
        if (inputArea) {
            inputArea.classList.remove('generating');
        }
        elements.userInput.disabled = false;
    }
}

function appendMessage(role, content, mediaList = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    // 添加头像
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';
    messageDiv.appendChild(avatar);
    
    const messageBody = document.createElement('div');
    messageBody.className = 'message-body';
    
    // 如果是 assistant，添加状态指示器和详情按钮
    if (role === 'assistant') {
        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        
        const status = document.createElement('div');
        status.className = 'message-status';
        status.textContent = 'thinking...';
        headerDiv.appendChild(status);
        
        // 添加详情按钮（初始隐藏）
        const detailsBtn = document.createElement('button');
        detailsBtn.className = 'message-details-btn';
        detailsBtn.innerHTML = '📋';
        detailsBtn.title = '查看详细信息';
        detailsBtn.style.display = 'none';
        detailsBtn.onclick = function() {
            const detailsPanel = messageBody.querySelector('.message-details-panel');
            if (detailsPanel) {
                const isHidden = detailsPanel.style.display === 'none';
                detailsPanel.style.display = isHidden ? 'block' : 'none';
                detailsBtn.classList.toggle('active', isHidden);
            }
        };
        headerDiv.appendChild(detailsBtn);
        
        messageBody.appendChild(headerDiv);
        
        // 添加详情面板（初始隐藏）
        const detailsPanel = document.createElement('div');
        detailsPanel.className = 'message-details-panel';
        detailsPanel.style.display = 'none';
        detailsPanel.innerHTML = `
            <div class="details-header">💭 处理过程详情</div>
            <div class="details-content"></div>
        `;
        messageBody.appendChild(detailsPanel);
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // 先添加文本内容
    if (content) {
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.textContent = content;
        contentDiv.appendChild(textDiv);
    }
    
    // 然后添加媒体（文本在上，媒体在下）- 支持多个媒体
    if (mediaList && mediaList.length > 0) {
        const mediaContainer = document.createElement('div');
        mediaContainer.className = 'message-media-container';
        
        mediaList.forEach(media => {
            if (media.type === 'video') {
                const video = document.createElement('video');
                video.src = `data:video/mp4;base64,${media.base64}`;
                video.className = 'message-media';
                video.controls = true;
                mediaContainer.appendChild(video);
            } else {
                const img = document.createElement('img');
                img.src = `data:image/jpeg;base64,${media.base64}`;
                img.className = 'message-media';
                mediaContainer.appendChild(img);
            }
        });
        
        contentDiv.appendChild(mediaContainer);
    }
    
    messageBody.appendChild(contentDiv);
    messageDiv.appendChild(messageBody);
    
    // 移除欢迎消息
    const welcome = elements.chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();
    
    elements.chatMessages.appendChild(messageDiv);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    
    return messageDiv;
}

async function clearChat() {
    if (confirm('确定要清空对话历史吗？这将同时清空所有上传的文件缓存。')) {
        // 清空对话历史
        currentMessages = [];
        currentMediaList = [];
        elements.chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">🤖</div>
                <h3>欢迎使用行业智能通用运维模型2.0</h3>
                <p>请先在左侧配置模型和工具，然后开始智能对话</p>
            </div>
        `;
        elements.mediaPreview.innerHTML = '';
        
        // 清空服务器端的上传缓存
        try {
            const response = await fetch(`${API_BASE}/api/uploads/clear`, {
                method: 'POST'
            });
            const data = await response.json();
            if (data.success) {
                console.log('✓ 上传缓存已清空');
            } else {
                console.warn('⚠ 清空缓存失败:', data.error);
            }
        } catch (error) {
            console.error('✗ 清空缓存请求失败:', error);
        }
    }
}

async function handleMediaUpload(e) {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    
    // 处理每个文件
    for (const file of files) {
        const isVideo = file.type.startsWith('video/');
        
        try {
            if (!isVideo) {
                // 图片压缩
                const compressedBase64 = await compressImage(file);
                currentMediaList.push({
                    type: 'image',
                    base64: compressedBase64,
                    name: file.name
                });
            } else {
                // 视频上传
                const formData = new FormData();
                formData.append('media', file);
                
                const response = await fetch(`${API_BASE}/api/upload`, {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentMediaList.push({
                        type: 'video',
                        base64: data.base64,
                        name: file.name
                    });
                } else {
                    alert(`${file.name} 上传失败: ${data.error}`);
                    continue;
                }
            }
        } catch (error) {
            alert(`${file.name} 处理失败: ${error.message}`);
            continue;
        }
    }
    
    // 更新预览显示
    updateMediaPreview();
    // 更新对话框显示
    updatePendingMedia();
}

function updateMediaPreview() {
    if (currentMediaList.length === 0) {
        elements.mediaPreview.innerHTML = '';
        return;
    }
    
    let html = '<div class="media-preview-grid">';
    currentMediaList.forEach((media, index) => {
        if (media.type === 'video') {
            html += `
                <div class="preview-item">
                    <video src="data:video/mp4;base64,${media.base64}" class="preview-media"></video>
                    <button class="remove-media-item" onclick="removeMediaItem(${index})">✕</button>
                </div>
            `;
        } else {
            html += `
                <div class="preview-item">
                    <img src="data:image/jpeg;base64,${media.base64}" class="preview-media">
                    <button class="remove-media-item" onclick="removeMediaItem(${index})">✕</button>
                </div>
            `;
        }
    });
    html += '</div>';
    elements.mediaPreview.innerHTML = html;
}

function updatePendingMedia() {
    // 移除旧的待发送媒体
    const oldPending = elements.chatMessages.querySelector('.pending-media-container');
    if (oldPending) oldPending.remove();
    
    if (currentMediaList.length === 0) return;
    
    // 创建新的待发送媒体显示
    const pendingDiv = document.createElement('div');
    pendingDiv.className = 'pending-media-container';
    
    const label = document.createElement('div');
    label.className = 'pending-media-label';
    label.textContent = `📎 待发送的媒体 (${currentMediaList.length}个)：`;
    pendingDiv.appendChild(label);
    
    const grid = document.createElement('div');
    grid.className = 'pending-media-grid';
    
    currentMediaList.forEach(media => {
        if (media.type === 'video') {
            const video = document.createElement('video');
            video.src = `data:video/mp4;base64,${media.base64}`;
            video.className = 'pending-media';
            video.controls = true;
            grid.appendChild(video);
        } else {
            const img = document.createElement('img');
            img.src = `data:image/jpeg;base64,${media.base64}`;
            img.className = 'pending-media';
            grid.appendChild(img);
        }
    });
    
    pendingDiv.appendChild(grid);
    elements.chatMessages.appendChild(pendingDiv);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function removeMediaItem(index) {
    currentMediaList.splice(index, 1);
    updateMediaPreview();
    updatePendingMedia();
    
    if (currentMediaList.length === 0) {
        elements.mediaUpload.value = '';
    }
}

// ==================== 模型管理 ====================

async function loadModels() {
    try {
        const response = await fetch(`${API_BASE}/api/models`);
        const data = await response.json();
        
        if (data.success) {
            renderModels(data.models);
            updateModelSelect(data.models);
        }
    } catch (error) {
        console.error('加载模型失败:', error);
    }
}

function renderModels(models) {
    if (models.length === 0) {
        elements.modelsList.innerHTML = '<p class="text-muted">暂无已注册的模型</p>';
        return;
    }
    
    elements.modelsList.innerHTML = models.map(model => `
        <div class="item-card">
            <div class="item-header">
                <div class="item-title">${model.name}</div>
                <div class="item-actions">
                    <button class="btn btn-secondary" onclick='editModel(${JSON.stringify(model).replace(/'/g, "&apos;")})'>编辑</button>
                    <button class="btn btn-danger" onclick="deleteModel('${model.id}')">删除</button>
                </div>
            </div>
            <div class="item-info">
                <div class="item-info-row">
                    <span class="item-info-label">实际模型:</span>
                    <span class="item-info-value">${model.actual_model_name || '未设置'}</span>
                </div>
                <div class="item-info-row">
                    <span class="item-info-label">类型:</span>
                    <span class="item-info-value">${model.model_type}</span>
                </div>
                <div class="item-info-row">
                    <span class="item-info-label">URL:</span>
                    <span class="item-info-value">${model.url}</span>
                </div>
                <div class="item-info-row">
                    <span class="item-info-label">系统提示词:</span>
                    <span class="item-info-value">${model.system_prompt ? '✓ 已设置' : '✗ 未设置'}</span>
                </div>
                <div class="item-info-row">
                    <span class="item-info-label">状态:</span>
                    <span class="item-status ${model.status}">${model.status === 'active' ? '✓ 活跃' : '✗ 禁用'}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function updateModelSelect(models) {
    if (models.length === 0) {
        elements.modelSelect.innerHTML = '<option value="">请先注册模型</option>';
        return;
    }
    
    elements.modelSelect.innerHTML = models.map(model => 
        `<option value="${model.id}">${model.name}</option>`
    ).join('');
}

function editModel(model) {
    currentEditingModelId = model.id;
    elements.editModelName.value = model.name;
    elements.editModelSystemPrompt.value = model.system_prompt || '';
    showModal(elements.editModelModal);
}

async function updateModel() {
    if (!currentEditingModelId) return;
    
    const systemPrompt = elements.editModelSystemPrompt.value.trim();
    
    elements.updateModelBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/api/models/${currentEditingModelId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                system_prompt: systemPrompt
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            hideModal(elements.editModelModal);
            loadModels();
            alert('模型更新成功！');
        } else {
            alert(`更新失败: ${data.error}`);
        }
    } catch (error) {
        alert(`更新失败: ${error.message}`);
    } finally {
        elements.updateModelBtn.disabled = false;
        currentEditingModelId = null;
    }
}

async function deleteModel(modelId) {
    if (!confirm('确定要删除这个模型吗？')) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/models/${modelId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadModels();
        } else {
            alert(`删除失败: ${data.error}`);
        }
    } catch (error) {
        alert(`删除失败: ${error.message}`);
    }
}

// ==================== 工具管理 ====================

async function loadTools() {
    try {
        const response = await fetch(`${API_BASE}/api/tools`);
        const data = await response.json();
        
        if (data.success) {
            renderTools(data.tools);
            updateToolsCheckboxes(data.tools);
        }
    } catch (error) {
        console.error('加载工具失败:', error);
    }
}

function renderTools(tools) {
    if (tools.length === 0) {
        elements.toolsList.innerHTML = '<p class="text-muted">暂无已注册的工具</p>';
        return;
    }
    
    elements.toolsList.innerHTML = tools.map(tool => `
        <div class="item-card">
            <div class="item-header">
                <div class="item-title">${tool.name}</div>
                <div class="item-actions">
                    <button class="btn ${tool.enabled ? 'btn-secondary' : 'btn-success'}" 
                            onclick="toggleTool('${tool.id}')">
                        ${tool.enabled ? '禁用' : '启用'}
                    </button>
                    <button class="btn btn-danger" onclick="deleteTool('${tool.id}')">删除</button>
                </div>
            </div>
            <div class="item-info">
                <div class="item-info-row">
                    <span class="item-info-label">描述:</span>
                    <span class="item-info-value">${tool.description}</span>
                </div>
                <div class="item-info-row">
                    <span class="item-info-label">状态:</span>
                    <span class="item-status ${tool.enabled ? 'active' : 'inactive'}">
                        ${tool.enabled ? '已启用' : '已禁用'}
                    </span>
                </div>
            </div>
        </div>
    `).join('');
}

function updateToolsCheckboxes(tools) {
    const enabledTools = tools.filter(t => t.enabled);
    
    if (enabledTools.length === 0) {
        elements.toolsCheckboxes.innerHTML = '<p class="text-muted">暂无可用工具</p>';
        return;
    }
    
    elements.toolsCheckboxes.innerHTML = enabledTools.map(tool => `
        <div class="tool-checkbox">
            <input type="checkbox" id="tool-${tool.id}" value="${tool.id}">
            <label for="tool-${tool.id}">${tool.name}</label>
        </div>
    `).join('');
}

async function toggleTool(toolId) {
    try {
        const response = await fetch(`${API_BASE}/api/tools/${toolId}/toggle`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadTools();
        } else {
            alert(`操作失败: ${data.error}`);
        }
    } catch (error) {
        alert(`操作失败: ${error.message}`);
    }
}

async function deleteTool(toolId) {
    if (!confirm('确定要删除这个工具吗？')) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/tools/${toolId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadTools();
        } else {
            alert(`删除失败: ${data.error}`);
        }
    } catch (error) {
        alert(`删除失败: ${error.message}`);
    }
}

// ==================== 弹窗管理 ====================

function initModals() {
    // 模型注册弹窗
    elements.addModelBtn.addEventListener('click', () => {
        showModal(elements.modelModal);
    });
    
    elements.testModelBtn.addEventListener('click', testModelConnection);
    elements.saveModelBtn.addEventListener('click', saveModel);
    
    // 模型编辑弹窗
    elements.updateModelBtn.addEventListener('click', updateModel);
    
    // 工具注册弹窗
    elements.addToolBtn.addEventListener('click', () => {
        showModal(elements.toolModal);
    });
    
    elements.saveToolBtn.addEventListener('click', saveTool);
    
    // 关闭按钮
    document.querySelectorAll('.close').forEach(btn => {
        btn.addEventListener('click', () => {
            hideModal(btn.closest('.modal'));
        });
    });
    
    // 点击外部关闭
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            hideModal(e.target);
        }
    });
}

function showModal(modal) {
    modal.classList.add('show');
}

function hideModal(modal) {
    modal.classList.remove('show');
    // 清空表单
    modal.querySelectorAll('input, textarea').forEach(input => {
        input.value = '';
    });
    // 清空测试结果
    if (elements.modelTestResult) {
        elements.modelTestResult.innerHTML = '';
    }
    // 重置测试状态
    modelTestPassed = false;
}

// 存储测试状态
let modelTestPassed = false;
let currentEditingModelId = null;

// 压缩图片
function compressImage(file, maxWidth = 800, quality = 0.8) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const img = new Image();
            
            img.onload = () => {
                // 创建canvas
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;
                
                // 如果图片宽度超过最大宽度，按比例缩放
                if (width > maxWidth) {
                    height = (height * maxWidth) / width;
                    width = maxWidth;
                }
                
                canvas.width = width;
                canvas.height = height;
                
                // 绘制图片
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                
                // 转换为base64，使用较低的质量
                const base64 = canvas.toDataURL('image/jpeg', quality).split(',')[1];
                resolve(base64);
            };
            
            img.onerror = () => reject(new Error('图片加载失败'));
            img.src = e.target.result;
        };
        
        reader.onerror = () => reject(new Error('文件读取失败'));
        reader.readAsDataURL(file);
    });
}

// 解析包含 <think></think> 标签的内容
function parseThinkingContent(text) {
    const thinkRegex = /<think>([\s\S]*?)<\/think>/g;
    let thinking = '';
    let content = text;
    let thinkingComplete = false;
    
    // 提取所有 <think></think> 中的内容
    let match;
    let lastThinkEnd = 0;
    while ((match = thinkRegex.exec(text)) !== null) {
        thinking = match[1];  // 只保留最后一个 thinking
        lastThinkEnd = match.index + match[0].length;
        thinkingComplete = true;
    }
    
    // 移除 <think></think> 标签，只保留外部内容
    content = text.replace(thinkRegex, '');
    
    // 移除所有格式的工具调用标签
    // 格式1: <tool_call>...</tool_call>
    content = content.replace(/<tool_call>[\s\S]*?<\/tool_call>/g, '');
    // 格式2: <tool_call ... />
    content = content.replace(/<tool_call[^>]*?\/>/g, '');
    // 格式3: 函数调用格式 function_name({...})
    content = content.replace(/\w+\s*\(\s*\{[\s\S]*?\}\s*\)/g, '');
    
    // 如果有未闭合的 <think> 标签
    const openThinkIndex = text.lastIndexOf('<think>');
    const closeThinkIndex = text.lastIndexOf('</think>');
    
    if (openThinkIndex > closeThinkIndex) {
        // 有未闭合的 <think>，提取其中的内容作为 thinking
        thinking = text.substring(openThinkIndex + 7);  // 7 是 '<think>' 的长度
        content = text.substring(0, openThinkIndex);
        thinkingComplete = false;
    }
    
    return {
        thinking: thinking.trim(),
        content: content.trim(),
        thinkingComplete: thinkingComplete
    };
}

async function testModelConnection() {
    const name = elements.newModelName.value.trim();
    const actualName = elements.newModelActualName.value.trim();
    const url = elements.newModelUrl.value.trim();
    const apiKey = elements.newModelKey.value.trim();
    const modelType = elements.newModelType.value;
    
    if (!url) {
        elements.modelTestResult.innerHTML = '<div class="test-result error">请输入 URL</div>';
        modelTestPassed = false;
        return;
    }
    
    elements.testModelBtn.disabled = true;
    elements.testModelBtn.innerHTML = '<span class="loading"></span> 测试中...';
    elements.modelTestResult.innerHTML = '';
    modelTestPassed = false;
    
    try {
        const response = await fetch(`${API_BASE}/api/models/test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                api_key: apiKey,
                model_type: modelType,
                actual_model_name: actualName || 'gpt-3.5-turbo'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            elements.modelTestResult.innerHTML = '<div class="test-result success">✓ 连接测试成功！可以保存了</div>';
            modelTestPassed = true;
        } else {
            elements.modelTestResult.innerHTML = `<div class="test-result error">✗ ${data.error}</div>`;
            modelTestPassed = false;
        }
    } catch (error) {
        elements.modelTestResult.innerHTML = `<div class="test-result error">✗ ${error.message}</div>`;
        modelTestPassed = false;
    } finally {
        elements.testModelBtn.disabled = false;
        elements.testModelBtn.textContent = '测试连接';
    }
}

async function saveModel() {
    const name = elements.newModelName.value.trim();
    const actualName = elements.newModelActualName.value.trim();
    const url = elements.newModelUrl.value.trim();
    const apiKey = elements.newModelKey.value.trim();
    const modelType = elements.newModelType.value;
    
    if (!name || !actualName || !url) {
        alert('请填写显示名称、实际模型名和 URL');
        return;
    }
    
    if (!modelTestPassed) {
        alert('请先测试连接并确保测试通过后再保存');
        return;
    }
    
    elements.saveModelBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/api/models/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                actual_model_name: actualName,
                url: url,
                api_key: apiKey,
                model_type: modelType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            hideModal(elements.modelModal);
            loadModels();
            alert('模型注册成功！');
        } else {
            alert(`注册失败: ${data.error}`);
        }
    } catch (error) {
        alert(`注册失败: ${error.message}`);
    } finally {
        elements.saveModelBtn.disabled = false;
    }
}

// ==================== 工具表单管理 ====================

function initToolForm() {
    // 工具类型切换
    elements.newToolType.addEventListener('change', (e) => {
        const toolType = e.target.value;
        
        // 隐藏所有配置区域
        elements.builtinToolSection.style.display = 'none';
        elements.apiToolSection.style.display = 'none';
        elements.codeToolSection.style.display = 'none';
        
        // 显示对应的配置区域
        switch (toolType) {
            case 'builtin':
                elements.builtinToolSection.style.display = 'block';
                break;
            case 'api':
                elements.apiToolSection.style.display = 'block';
                break;
            case 'code':
                elements.codeToolSection.style.display = 'block';
                break;
        }
    });
    
    // 内置工具选择
    elements.builtinToolSelect.addEventListener('change', (e) => {
        const toolName = e.target.value;
        const selectedTool = builtinToolsCache.find(t => t.name === toolName);
        
        if (selectedTool) {
            elements.builtinToolInfo.innerHTML = `
                <strong>${selectedTool.name}</strong>
                <p>${selectedTool.description}</p>
                <p><em>参数：</em></p>
                <pre>${JSON.stringify(selectedTool.parameters, null, 2)}</pre>
            `;
        } else {
            elements.builtinToolInfo.innerHTML = '';
        }
    });
}

let builtinToolsCache = [];

async function loadBuiltinTools() {
    try {
        const response = await fetch(`${API_BASE}/api/tools/builtin`);
        const data = await response.json();
        
        if (data.success) {
            builtinToolsCache = data.tools;
            
            // 填充内置工具下拉列表
            elements.builtinToolSelect.innerHTML = '<option value="">-- 请选择 --</option>';
            data.tools.forEach(tool => {
                const option = document.createElement('option');
                option.value = tool.name;
                option.textContent = tool.name;
                elements.builtinToolSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载内置工具失败:', error);
    }
}

async function saveTool() {
    const toolType = elements.newToolType.value;
    let toolData = {};
    
    elements.saveToolBtn.disabled = true;
    
    try {
        // 根据工具类型构建数据
        switch (toolType) {
            case 'builtin':
                const builtinToolName = elements.builtinToolSelect.value;
                if (!builtinToolName) {
                    alert('请选择内置工具');
                    return;
                }
                
                const selectedTool = builtinToolsCache.find(t => t.name === builtinToolName);
                if (!selectedTool) {
                    alert('所选工具不存在');
                    return;
                }
                
                toolData = {
                    name: selectedTool.name,
                    description: selectedTool.description,
                    parameters: selectedTool.parameters,
                    tool_type: 'builtin'
                };
                break;
                
            case 'api':
                const apiName = elements.apiToolName.value.trim();
                const apiDescription = elements.apiToolDescription.value.trim();
                const apiUrl = elements.apiToolUrl.value.trim();
                const apiParametersText = elements.apiToolParameters.value.trim();
                
                if (!apiName || !apiDescription || !apiUrl || !apiParametersText) {
                    alert('请填写所有必填字段');
                    return;
                }
                
                let apiParameters;
                try {
                    apiParameters = JSON.parse(apiParametersText);
                } catch (error) {
                    alert('参数定义格式错误');
                    return;
                }
                
                let apiHeaders = {};
                const apiHeadersText = elements.apiToolHeaders.value.trim();
                if (apiHeadersText) {
                    try {
                        apiHeaders = JSON.parse(apiHeadersText);
                    } catch (error) {
                        alert('请求头格式错误');
                        return;
                    }
                }
                
                toolData = {
                    name: apiName,
                    description: apiDescription,
                    parameters: apiParameters,
                    tool_type: 'api',
                    api_url: apiUrl,
                    api_method: elements.apiToolMethod.value,
                    api_headers: apiHeaders
                };
                break;
                
            case 'code':
                const codeName = elements.codeToolName.value.trim();
                const codeDescription = elements.codeToolDescription.value.trim();
                const codeCode = elements.codeToolCode.value.trim();
                const codeParametersText = elements.codeToolParameters.value.trim();
                
                if (!codeName || !codeDescription || !codeCode || !codeParametersText) {
                    alert('请填写所有必填字段');
                    return;
                }
                
                let codeParameters;
                try {
                    codeParameters = JSON.parse(codeParametersText);
                } catch (error) {
                    alert('参数定义格式错误');
                    return;
                }
                
                toolData = {
                    name: codeName,
                    description: codeDescription,
                    parameters: codeParameters,
                    tool_type: 'code',
                    code: codeCode
                };
                break;
        }
        
        const response = await fetch(`${API_BASE}/api/tools/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(toolData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            hideModal(elements.toolModal);
            loadTools();
            alert('工具注册成功！');
            
            // 清空表单
            elements.builtinToolSelect.value = '';
            elements.apiToolName.value = '';
            elements.apiToolDescription.value = '';
            elements.apiToolUrl.value = '';
            elements.apiToolHeaders.value = '';
            elements.apiToolParameters.value = '';
            elements.codeToolName.value = '';
            elements.codeToolDescription.value = '';
            elements.codeToolCode.value = '';
            elements.codeToolParameters.value = '';
            elements.builtinToolInfo.innerHTML = '';
        } else {
            alert(`注册失败: ${data.error}`);
        }
    } catch (error) {
        alert(`注册失败: ${error.message}`);
    } finally {
        elements.saveToolBtn.disabled = false;
    }
}

// ==================== 自动解析和执行工具调用 ====================

async function autoParseAndExecuteTools(content, textDiv, messageDiv) {
    /**
     * 自动从模型输出中解析工具调用并执行
     * 支持多种格式:
     * 1. <tool_call>{"name": "...", "arguments": {...}}</tool_call>
     * 2. <tool_call name="..." arguments='...'/>
     * 3. function_name({"param": "value"})
     */
    try {
        const toolCalls = [];
        
        // 方式1: 解析 <tool_call>...</tool_call> 格式
        const toolCallRegex1 = /<tool_call>([\s\S]*?)<\/tool_call>/g;
        let match;
        while ((match = toolCallRegex1.exec(content)) !== null) {
            try {
                const callData = JSON.parse(match[1].trim());
                if (callData.name) {
                    toolCalls.push({
                        name: callData.name,
                        arguments: callData.arguments || {}
                    });
                }
            } catch (e) {
                console.warn('工具调用JSON解析失败:', e);
            }
        }
        
        // 方式2: 解析 <tool_call name="..." arguments='...'/> 格式
        const toolCallRegex2 = /<tool_call\s+name="([^"]+)"\s+arguments='([^']+)'\/>/g;
        while ((match = toolCallRegex2.exec(content)) !== null) {
            try {
                const args = JSON.parse(match[2]);
                toolCalls.push({
                    name: match[1],
                    arguments: args
                });
            } catch (e) {
                console.warn('工具调用参数解析失败:', e);
            }
        }
        
        // 方式3: 解析 function_name({...}) 格式（在</think>之后）
        const thinkEndIndex = content.lastIndexOf('</think>');
        if (thinkEndIndex !== -1) {
            const afterThink = content.substring(thinkEndIndex + 8); // 8 是 '</think>' 的长度
            const functionCallRegex = /(\w+)\s*\(\s*({[\s\S]*?})\s*\)/g;
            while ((match = functionCallRegex.exec(afterThink)) !== null) {
                try {
                    const args = JSON.parse(match[2]);
                    toolCalls.push({
                        name: match[1],
                        arguments: args
                    });
                } catch (e) {
                    console.warn('函数调用参数解析失败:', e);
                }
            }
        }
        
        if (toolCalls.length === 0) {
            return; // 没有找到工具调用
        }
        
        // 创建工具调用结果显示区域
        const toolResultsDiv = document.createElement('div');
        toolResultsDiv.className = 'tool-execution-results';
        toolResultsDiv.innerHTML = '<div class="tool-execution-header">🔧 执行工具调用</div>';
        
        // 在消息内容后添加
        const messageContent = messageDiv.querySelector('.message-content');
        messageContent.appendChild(toolResultsDiv);
        
        // 执行每个工具调用
        for (const toolCall of toolCalls) {
            const toolResultItem = document.createElement('div');
            toolResultItem.className = 'tool-result-item';
            toolResultItem.innerHTML = `
                <div class="tool-name">📍 ${toolCall.name}</div>
                <div class="tool-args">参数: <code>${JSON.stringify(toolCall.arguments)}</code></div>
                <div class="tool-result">⏳ 执行中...</div>
            `;
            toolResultsDiv.appendChild(toolResultItem);
            
            try {
                // 调用工具执行API
                const response = await fetch(`${API_BASE}/api/tools/execute`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        tool_name: toolCall.name,
                        parameters: toolCall.arguments
                    })
                });
                
                const data = await response.json();
                const resultDiv = toolResultItem.querySelector('.tool-result');
                
                if (data.success) {
                    resultDiv.innerHTML = `✅ 结果: <code>${JSON.stringify(data.result, null, 2)}</code>`;
                    resultDiv.className = 'tool-result success';
                } else {
                    resultDiv.innerHTML = `❌ 错误: ${data.error}`;
                    resultDiv.className = 'tool-result error';
                }
            } catch (error) {
                const resultDiv = toolResultItem.querySelector('.tool-result');
                resultDiv.innerHTML = `❌ 执行失败: ${error.message}`;
                resultDiv.className = 'tool-result error';
            }
        }
        
        // 滚动到底部
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
        
    } catch (error) {
        console.error('自动解析工具调用失败:', error);
    }
}

// ==================== MCP事件处理 ====================

function handleMCPEvent(event, messageBody, statusDiv, textDiv, thinkingDiv, contentDiv) {
    /**
     * 处理MCP事件，记录详细过程信息
     */
    const detailsPanel = messageBody.querySelector('.message-details-panel');
    if (!detailsPanel) return;
    
    const detailsContent = detailsPanel.querySelector('.details-content');
    const detailsBtn = messageBody.querySelector('.message-details-btn');
    
    switch (event.type) {
        case 'iteration_start':
            // 新的迭代开始
            addDetailsItem(detailsContent, {
                type: 'iteration',
                title: `🔄 第 ${event.iteration} 轮处理`,
                time: formatTime(event.timestamp)
            });
            // 显示详情按钮
            if (detailsBtn) detailsBtn.style.display = 'inline-flex';
            break;
            
        case 'thinking_extracted':
            // 提取到thinking内容
            addDetailsItem(detailsContent, {
                type: 'thinking',
                title: '💭 模型思考',
                content: event.thinking,
                time: formatTime(event.timestamp)
            });
            break;
            
        case 'tool_calls_parsed':
            // 解析到工具调用
            addDetailsItem(detailsContent, {
                type: 'info',
                title: `🔍 检测到 ${event.count} 个工具调用`,
                time: formatTime(event.timestamp)
            });
            break;
            
        case 'tool_call_start':
            // 工具调用开始
            const toolCallId = `tool-${Date.now()}-${Math.random()}`;
            addDetailsItem(detailsContent, {
                type: 'tool_call',
                id: toolCallId,
                title: `🔧 调用工具: ${event.name}`,
                content: `参数: ${JSON.stringify(event.arguments, null, 2)}`,
                status: 'executing',
                time: formatTime(event.timestamp)
            });
            // 更新状态显示
            if (statusDiv) {
                statusDiv.textContent = `🔧 调用 ${event.name}...`;
            }
            break;
            
        case 'tool_call_complete':
            // 工具调用完成
            updateLastToolCall(detailsContent, {
                status: event.success ? 'success' : 'error',
                result: event.result
            });
            break;
            
        case 'tool_call_error':
            // 工具调用失败
            updateLastToolCall(detailsContent, {
                status: 'error',
                error: event.error
            });
            break;
            
        case 'iteration_complete':
            // 迭代完成
            if (event.has_tool_calls) {
                addDetailsItem(detailsContent, {
                    type: 'info',
                    title: '✅ 工具执行完成，继续处理',
                    time: formatTime(event.timestamp)
                });
            } else {
                addDetailsItem(detailsContent, {
                    type: 'info',
                    title: '✅ 处理完成',
                    time: formatTime(event.timestamp)
                });
            }
            break;
            
        case 'max_iterations_reached':
            // 达到最大迭代次数
            addDetailsItem(detailsContent, {
                type: 'warning',
                title: `⚠️ 已达到最大迭代次数 (${event.max_iterations})`,
                time: formatTime(event.timestamp)
            });
            break;
    }
}

function addDetailsItem(container, item) {
    /**
     * 添加详情项
     */
    const itemDiv = document.createElement('div');
    itemDiv.className = `details-item details-${item.type}`;
    if (item.id) itemDiv.id = item.id;
    
    let html = `
        <div class="details-item-header">
            <span class="details-item-title">${item.title}</span>
            ${item.time ? `<span class="details-item-time">${item.time}</span>` : ''}
        </div>
    `;
    
    if (item.content) {
        html += `<div class="details-item-content"><pre>${escapeHtml(item.content)}</pre></div>`;
    }
    
    if (item.status) {
        const statusClass = item.status === 'success' ? 'success' : item.status === 'error' ? 'error' : 'executing';
        html += `<div class="details-item-status status-${statusClass}">`;
        
        if (item.status === 'executing') {
            html += '⏳ 执行中...';
        } else if (item.status === 'success') {
            html += `✅ 成功<pre>${escapeHtml(JSON.stringify(item.result, null, 2))}</pre>`;
        } else if (item.status === 'error') {
            html += `❌ 失败: ${item.error || '未知错误'}`;
        }
        
        html += '</div>';
    }
    
    itemDiv.innerHTML = html;
    container.appendChild(itemDiv);
}

function updateLastToolCall(container, update) {
    /**
     * 更新最后一个工具调用的状态
     */
    const toolCalls = container.querySelectorAll('.details-tool_call');
    if (toolCalls.length === 0) return;
    
    const lastCall = toolCalls[toolCalls.length - 1];
    const statusDiv = lastCall.querySelector('.details-item-status');
    
    if (statusDiv) {
        statusDiv.className = `details-item-status status-${update.status}`;
        
        if (update.status === 'success') {
            statusDiv.innerHTML = `✅ 成功<pre>${escapeHtml(JSON.stringify(update.result, null, 2))}</pre>`;
        } else if (update.status === 'error') {
            statusDiv.innerHTML = `❌ 失败: ${update.error || '未知错误'}`;
        }
    }
}

function formatTime(timestamp) {
    /**
     * 格式化时间戳
     */
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', { hour12: false });
}

function escapeHtml(text) {
    /**
     * 转义HTML特殊字符
     */
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

