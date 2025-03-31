document.addEventListener('DOMContentLoaded', function() {
    class AyurvedaChat {
        // Constants
        static ENDPOINTS = {
            GENERAL: '/api/general'
        };

        static MESSAGE_TYPES = {
            USER: 'user',
            BOT: 'bot'
        };

        static TABS = {
            GENERAL: 'general'
        };

        static WELCOME_MESSAGE = `
            **Welcome to AyurBot!**  
            I'm your Ayurvedic consultant. How can I help you today?  
            - Ask general health questions in **General Consult**
        `;

        constructor() {
            // DOM Elements
            this.elements = {
                toggleBtn: document.querySelector('.chat-toggle'),
                overlay: document.querySelector('.chat-overlay'),
                chatContainer: document.querySelector('.chat-container'),
                tabBtns: document.querySelectorAll('.tab-btn'),
                chatContents: document.querySelectorAll('.chat-content'),
                closeBtn: document.querySelector('.close-chat'),
                input: document.querySelector('#userInput'),
                sendBtn: document.querySelector('#sendBtn'),
                chatLaunchBtn: document.querySelector('#chatLaunchBtn'),
                heroChatBtn: document.querySelector('.chat-launch')
            };

            // State
            this.state = {
                activeTab: AyurvedaChat.TABS.GENERAL,
                histories: {
                    [AyurvedaChat.TABS.GENERAL]: []
                },
                isProcessing: false
            };

            this.init();
        }

        init() {
            this.bindEvents();
            this.render();
            this.addWelcomeMessage();
        }

        bindEvents() {
            const toggleButtons = [
                this.elements.toggleBtn,
                this.elements.chatLaunchBtn,
                this.elements.heroChatBtn
            ].filter(Boolean);

            toggleButtons.forEach(btn => {
                btn.addEventListener('click', () => this.toggleChat());
            });

            this.elements.closeBtn.addEventListener('click', () => this.toggleChat());
            this.elements.overlay.addEventListener('click', () => this.toggleChat());
            
            this.elements.tabBtns.forEach(btn => {
                btn.addEventListener('click', () => 
                    this.switchTab(btn.dataset.tab)
                );
            });
            
            this.elements.sendBtn.addEventListener('click', () => this.sendMessage());
            this.elements.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        }

        toggleChat() {
            const isOpen = this.elements.chatContainer.style.display === 'flex';
            
            this.elements.overlay.style.display = isOpen ? 'none' : 'block';
            this.elements.chatContainer.style.display = isOpen ? 'none' : 'flex';
            
            if (!isOpen) {
                this.elements.input.focus();
            }
            
            document.body.classList.toggle('chat-open', !isOpen);
        }

        switchTab(tab) {
            if (!Object.values(AyurvedaChat.TABS).includes(tab)) return;
            
            this.state.activeTab = tab;
            
            // Reset symptom analysis if switching to general tab
            if (tab === AyurvedaChat.TABS.GENERAL) {
                this.state.symptomAnalysis = this.state.symptomAnalysis || {};
                this.state.symptomAnalysis.inProgress = false;
                this.showInputField();
            }
            
            this.updateTabUI();
            this.renderHistory();
            this.elements.input.focus();
        }
        
        showInputField() {
            if (this.elements.inputContainer) {
                this.elements.inputContainer.style.display = 'flex';
            }
        }

        updateTabUI() {
            this.elements.tabBtns.forEach(btn => {
                btn.classList.toggle('active', btn.dataset.tab === this.state.activeTab);
            });
            
            this.elements.chatContents.forEach(content => {
                content.classList.toggle('active', 
                    content.id === `${this.state.activeTab}-chat`);
            });
        }

        async sendMessage() {
            if (this.state.isProcessing) return;
            
            const message = this.elements.input.value.trim();
            if (!message) return;
            
            this.addMessageToUI(message, AyurvedaChat.MESSAGE_TYPES.USER);
            this.saveToHistory(message, AyurvedaChat.MESSAGE_TYPES.USER);
            this.elements.input.value = '';
            
            this.state.isProcessing = true;
            this.elements.sendBtn.disabled = true;
            
            try {
                await this.getBotResponse(message);
            } catch (error) {
                console.error('Message sending error:', error);
                this.addMessageToUI(
                    "Sorry, I encountered an error. Please try again.",
                    AyurvedaChat.MESSAGE_TYPES.BOT
                );
            } finally {
                this.state.isProcessing = false;
                this.elements.sendBtn.disabled = false;
            }
        }

        async getBotResponse(message) {
            const endpoint = AyurvedaChat.ENDPOINTS.GENERAL;
            
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        message
                    })
                });
                
                if (!response.ok) throw new Error(await response.text());
                
                const data = await response.json();
                
                this.addMessageToUI(data.response, AyurvedaChat.MESSAGE_TYPES.BOT);
                this.saveToHistory(data.response, AyurvedaChat.MESSAGE_TYPES.BOT);
                
                fetchRemedies();
                
            } catch (error) {
                console.error('API Error:', error);
                this.addMessageToUI(
                    "Let me consult Ayurvedic texts... Please try again in a moment.",
                    AyurvedaChat.MESSAGE_TYPES.BOT
                );
            }
        }

        // Input field is always visible in general consultation mode

        addMessageToUI(content, sender) {
            const activeChat = document.querySelector(
                `#${this.state.activeTab}-chat`
            );
            const messageDiv = document.createElement('div');
            
            messageDiv.classList.add('message', `${sender}-message`);
            messageDiv.innerHTML = this.formatMessage(content);
            
            activeChat.appendChild(messageDiv);
            activeChat.scrollTop = activeChat.scrollHeight;
        }

        formatMessage(text) {
            return DOMPurify.sanitize(text)
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/(\d+)\./g, '<span class="list-number">$1.</span>')
                .split('\n\n').map(para => 
                    `<p>${para.replace(/\n/g, '<br>')}</p>`
                ).join('');
        }

        saveToHistory(content, sender) {
            this.state.histories[this.state.activeTab].push({
                type: sender,
                content: sender === AyurvedaChat.MESSAGE_TYPES.USER 
                    ? content 
                    : this.formatMessage(content)
            });
        }

        renderHistory() {
            const activeChat = document.querySelector(
                `#${this.state.activeTab}-chat`
            );
            const history = this.state.histories[this.state.activeTab];
            
            activeChat.innerHTML = '';
            history.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message', `${msg.type}-message`);
                messageDiv.innerHTML = msg.content;
                activeChat.appendChild(messageDiv);
            });
            
            activeChat.scrollTop = activeChat.scrollHeight;
        }

        addWelcomeMessage() {
            this.addMessageToUI(
                AyurvedaChat.WELCOME_MESSAGE,
                AyurvedaChat.MESSAGE_TYPES.BOT
            );
            this.saveToHistory(
                AyurvedaChat.WELCOME_MESSAGE,
                AyurvedaChat.MESSAGE_TYPES.BOT
            );
        }

        render() {
            this.updateTabUI();
        }
    }

    new AyurvedaChat();
    
    async function fetchRemedies() {
        try {
            const response = await fetch('/api/remedies');
            if (!response.ok) throw new Error('Network response was not ok');
            const remediesData = await response.json();
            updateRemediesUI(remediesData);
        } catch (error) {
            console.error('Error fetching remedies:', error);
        }
    }
    
    function updateRemediesUI(remediesData) {
        const remediesList = document.querySelector('.remedies-list');
        if (!remediesList) return;
        let htmlContent = '';
        if (Object.keys(remediesData).length > 0) {
            for (const [disease, remedies] of Object.entries(remediesData)) {
                htmlContent += `<li class="remedy-item"><h3 style="color: var(--primary);">${disease.charAt(0).toUpperCase() + disease.slice(1)}</h3>`;
                remedies.forEach(remedy => {
                    htmlContent += `<p>${remedy}</p>`;
                });
                htmlContent += '</li>';
            }
        } else {
            htmlContent = `<li><p>No remedies tracked yet.</p></li>`;
        }
        remediesList.innerHTML = htmlContent;
    }
});
