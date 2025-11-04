/**
 * College Buddy - Embeddable Chat Widget
 * Usage: <script src="https://yourdomain.com/static/widget.js"></script>
 */

(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        apiUrl: window.COLLEGE_BUDDY_API || 'http://localhost:8001',
        theme: window.COLLEGE_BUDDY_THEME || 'indigo',
        position: window.COLLEGE_BUDDY_POSITION || 'bottom-right',
        autoOpen: window.COLLEGE_BUDDY_AUTO_OPEN || false,
        greeting: window.COLLEGE_BUDDY_GREETING || 'Hi! How can I help you today?'
    };
    
    // Prevent multiple instances
    if (window.CollegeBuddyWidget) {
        console.warn('College Buddy Widget already loaded');
        return;
    }
    
    // Create widget container
    const widgetContainer = document.createElement('div');
    widgetContainer.id = 'college-buddy-widget';
    widgetContainer.style.cssText = `
        position: fixed;
        ${CONFIG.position.includes('bottom') ? 'bottom: 20px;' : 'top: 20px;'}
        ${CONFIG.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;
    
    // Load Tailwind CSS if not already loaded
    if (!document.querySelector('script[src*="tailwindcss"]')) {
        const tailwindScript = document.createElement('script');
        tailwindScript.src = 'https://cdn.tailwindcss.com';
        document.head.appendChild(tailwindScript);
    }
    
    // Create widget button (chat bubble)
    const widgetButton = document.createElement('button');
    widgetButton.id = 'college-buddy-toggle';
    widgetButton.className = 'bg-indigo-600 hover:bg-indigo-700 text-white rounded-full p-4 shadow-lg transition-all duration-300 hover:scale-110';
    widgetButton.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 4v-4z" />
        </svg>
    `;
    widgetButton.setAttribute('aria-label', 'Open College Buddy Chat');
    
    // Create iframe for the chat widget
    const widgetFrame = document.createElement('iframe');
    widgetFrame.id = 'college-buddy-frame';
    widgetFrame.src = `${CONFIG.apiUrl}/widget`;
    widgetFrame.style.cssText = `
        display: none;
        position: fixed;
        ${CONFIG.position.includes('bottom') ? 'bottom: 90px;' : 'top: 90px;'}
        ${CONFIG.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
        width: 400px;
        height: 600px;
        max-width: calc(100vw - 40px);
        max-height: calc(100vh - 120px);
        border: none;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        z-index: 999998;
        background: white;
        transition: all 0.3s ease-in-out;
        transform: scale(0.95);
        opacity: 0;
    `;
    
    // Mobile responsive adjustments
    if (window.innerWidth <= 640) {
        widgetFrame.style.width = 'calc(100vw - 40px)';
        widgetFrame.style.height = '75vh';
    }
    
    // Toggle widget visibility
    let isOpen = false;
    function toggleWidget() {
        isOpen = !isOpen;
        
        if (isOpen) {
            widgetFrame.style.display = 'block';
            setTimeout(() => {
                widgetFrame.style.transform = 'scale(1)';
                widgetFrame.style.opacity = '1';
            }, 10);
            
            widgetButton.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
            `;
            widgetButton.setAttribute('aria-label', 'Close College Buddy Chat');
            
            // Track widget open
            trackEvent('widget_opened');
        } else {
            widgetFrame.style.transform = 'scale(0.95)';
            widgetFrame.style.opacity = '0';
            setTimeout(() => {
                widgetFrame.style.display = 'none';
            }, 300);
            
            widgetButton.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 4v-4z" />
                </svg>
            `;
            widgetButton.setAttribute('aria-label', 'Open College Buddy Chat');
            
            // Track widget close
            trackEvent('widget_closed');
        }
    }
    
    widgetButton.addEventListener('click', toggleWidget);
    
    // Listen for messages from iframe
    window.addEventListener('message', (event) => {
        if (event.origin !== CONFIG.apiUrl.replace(/:\d+$/, '').replace(/https?:\/\//, '')) {
            // Allow localhost for development
            if (!event.origin.includes('localhost') && !event.origin.includes('127.0.0.1')) {
                return;
            }
        }
        
        if (event.data.type === 'close-widget') {
            toggleWidget();
        } else if (event.data.type === 'analytics') {
            trackEvent(event.data.event, event.data.data);
        }
    });
    
    // Analytics tracking
    function trackEvent(eventName, data = {}) {
        // Send to backend analytics endpoint
        fetch(`${CONFIG.apiUrl}/analytics/track`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event: eventName,
                data: data,
                timestamp: Date.now(),
                url: window.location.href,
                referrer: document.referrer
            })
        }).catch(err => console.error('Analytics error:', err));
    }
    
    // Append to DOM
    widgetContainer.appendChild(widgetButton);
    document.body.appendChild(widgetContainer);
    document.body.appendChild(widgetFrame);
    
    // Auto-open if configured
    if (CONFIG.autoOpen) {
        setTimeout(toggleWidget, 1000);
    }
    
    // Track initial page load
    trackEvent('widget_loaded', {
        page: window.location.pathname,
        referrer: document.referrer
    });
    
    // Expose API
    window.CollegeBuddyWidget = {
        open: function() {
            if (!isOpen) toggleWidget();
        },
        close: function() {
            if (isOpen) toggleWidget();
        },
        toggle: toggleWidget,
        isOpen: function() {
            return isOpen;
        }
    };
    
    console.log('✅ College Buddy Widget loaded successfully');
})();
