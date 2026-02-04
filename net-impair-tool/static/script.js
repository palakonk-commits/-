/**
 * Network Impairment Tool - Frontend JavaScript
 * UI control and communication with Flask backend
 */

// ============================================================================
// Global State
// ============================================================================

const AppState = {
    isRunning: false,
    updateInterval: null,
    config: {},
    previousStats: {}
};

// API endpoint
const API_BASE = 'http://127.0.0.1:5000/api';

// ============================================================================
// UI Elements Cache
// ============================================================================

const UI = {
    // Filter
    filterInput: document.getElementById('filterInput'),
    
    // Lag
    lagCheck: document.getElementById('lagCheck'),
    lagSlider: document.getElementById('lagSlider'),
    lagValue: document.getElementById('lagValue'),
    
    // Drop
    dropCheck: document.getElementById('dropCheck'),
    dropSlider: document.getElementById('dropSlider'),
    dropValue: document.getElementById('dropValue'),
    
    // Throttle
    throttleCheck: document.getElementById('throttleCheck'),
    throttleTimeSlider: document.getElementById('throttleTimeSlider'),
    throttleTimeValue: document.getElementById('throttleTimeValue'),
    throttleChanceSlider: document.getElementById('throttleChanceSlider'),
    throttleChanceValue: document.getElementById('throttleChanceValue'),
    
    // Duplicate
    duplicateCheck: document.getElementById('duplicateCheck'),
    duplicateCountSlider: document.getElementById('duplicateCountSlider'),
    duplicateCountValue: document.getElementById('duplicateCountValue'),
    duplicateChanceSlider: document.getElementById('duplicateChanceSlider'),
    duplicateChanceValue: document.getElementById('duplicateChanceValue'),
    
    // Out-of-Order
    oooCheck: document.getElementById('oooCheck'),
    oooChanceSlider: document.getElementById('oooChanceSlider'),
    oooChanceValue: document.getElementById('oooChanceValue'),
    
    // Tamper
    tamperCheck: document.getElementById('tamperCheck'),
    tamperChanceSlider: document.getElementById('tamperChanceSlider'),
    tamperChanceValue: document.getElementById('tamperChanceValue'),
    
    // Buttons
    startBtn: document.getElementById('startBtn'),
    stopBtn: document.getElementById('stopBtn'),
    deleteBtn: document.getElementById('deleteBtn'),
    resetStatsBtn: document.getElementById('resetStatsBtn'),
    
    // Status
    engineStatus: document.getElementById('engineStatus'),
    adminStatus: document.getElementById('adminStatus'),
    configDisplay: document.getElementById('configDisplay'),
    
    // Stats
    statProcessed: document.getElementById('statProcessed'),
    statDropped: document.getElementById('statDropped'),
    statDelayed: document.getElementById('statDelayed'),
    statDuplicated: document.getElementById('statDuplicated'),
    statTampered: document.getElementById('statTampered'),
    statOOO: document.getElementById('statOOO'),
    statQueueSize: document.getElementById('statQueueSize'),
};

// ============================================================================
// Utility Functions
// ============================================================================

function showToast(message, type = 'info') {
    /**
     * แสดง toast notification
     * @param {string} message - ข้อความ
     * @param {string} type - 'success', 'error', 'warning', 'info'
     */
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

async function apiCall(endpoint, method = 'GET', data = null) {
    /**
     * Generic API call wrapper
     */
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API call failed: ${error}`);
        showToast(`Error: ${error.message}`, 'error');
        return null;
    }
}

// ============================================================================
// Slider Event Listeners
// ============================================================================

function setupSliders() {
    /**
     * Setup slider value display updates
     */
    const sliders = [
        { slider: UI.lagSlider, output: UI.lagValue },
        { slider: UI.dropSlider, output: UI.dropValue },
        { slider: UI.throttleTimeSlider, output: UI.throttleTimeValue },
        { slider: UI.throttleChanceSlider, output: UI.throttleChanceValue },
        { slider: UI.duplicateCountSlider, output: UI.duplicateCountValue },
        { slider: UI.duplicateChanceSlider, output: UI.duplicateChanceValue },
        { slider: UI.oooChanceSlider, output: UI.oooChanceValue },
        { slider: UI.tamperChanceSlider, output: UI.tamperChanceValue },
    ];
    
    sliders.forEach(({ slider, output }) => {
        slider.addEventListener('input', (e) => {
            output.textContent = e.target.value;
        });
    });
}

// ============================================================================
// Config Management
// ============================================================================

function gatherConfigFromUI() {
    /**
     * รวมค่าปัจจุบันจาก UI เป็น config object
     */
    return {
        filter_str: UI.filterInput.value,
        lag_enabled: UI.lagCheck.checked,
        lag_ms: parseInt(UI.lagSlider.value),
        drop_enabled: UI.dropCheck.checked,
        drop_chance: parseFloat(UI.dropSlider.value),
        throttle_enabled: UI.throttleCheck.checked,
        throttle_ms: parseInt(UI.throttleTimeSlider.value),
        throttle_chance: parseFloat(UI.throttleChanceSlider.value),
        duplicate_enabled: UI.duplicateCheck.checked,
        duplicate_count: parseInt(UI.duplicateCountSlider.value),
        duplicate_chance: parseFloat(UI.duplicateChanceSlider.value),
        out_of_order_enabled: UI.oooCheck.checked,
        out_of_order_chance: parseFloat(UI.oooChanceSlider.value),
        tamper_enabled: UI.tamperCheck.checked,
        tamper_chance: parseFloat(UI.tamperChanceSlider.value),
    };
}

async function loadConfigFromServer() {
    /**
     * โหลด config จาก server แสดงใน UI
     */
    const config = await apiCall('/config');
    if (!config) return;
    
    AppState.config = config;
    
    // Update UI
    UI.filterInput.value = config.filter_str || 'outbound and udp';
    UI.lagCheck.checked = config.lag_enabled;
    UI.lagSlider.value = config.lag_ms;
    UI.lagValue.textContent = config.lag_ms;
    
    UI.dropCheck.checked = config.drop_enabled;
    UI.dropSlider.value = config.drop_chance;
    UI.dropValue.textContent = config.drop_chance;
    
    UI.throttleCheck.checked = config.throttle_enabled;
    UI.throttleTimeSlider.value = config.throttle_ms;
    UI.throttleTimeValue.textContent = config.throttle_ms;
    UI.throttleChanceSlider.value = config.throttle_chance;
    UI.throttleChanceValue.textContent = config.throttle_chance;
    
    UI.duplicateCheck.checked = config.duplicate_enabled;
    UI.duplicateCountSlider.value = config.duplicate_count;
    UI.duplicateCountValue.textContent = config.duplicate_count;
    UI.duplicateChanceSlider.value = config.duplicate_chance;
    UI.duplicateChanceValue.textContent = config.duplicate_chance;
    
    UI.oooCheck.checked = config.out_of_order_enabled;
    UI.oooChanceSlider.value = config.out_of_order_chance;
    UI.oooChanceValue.textContent = config.out_of_order_chance;
    
    UI.tamperCheck.checked = config.tamper_enabled;
    UI.tamperChanceSlider.value = config.tamper_chance;
    UI.tamperChanceValue.textContent = config.tamper_chance;
}

function updateConfigDisplay() {
    /**
     * แสดง active config ใน config display panel
     */
    const config = gatherConfigFromUI();
    const display = UI.configDisplay;
    
    let html = '';
    
    const items = [
        { key: 'Filter', value: config.filter_str },
        { key: 'Lag', value: config.lag_enabled ? `${config.lag_ms}ms` : 'Disabled' },
        { key: 'Drop', value: config.drop_enabled ? `${config.drop_chance}%` : 'Disabled' },
        { key: 'Throttle', value: config.throttle_enabled ? `${config.throttle_ms}ms (${config.throttle_chance}%)` : 'Disabled' },
        { key: 'Duplicate', value: config.duplicate_enabled ? `x${config.duplicate_count} (${config.duplicate_chance}%)` : 'Disabled' },
        { key: 'Out-of-Order', value: config.out_of_order_enabled ? `${config.out_of_order_chance}%` : 'Disabled' },
        { key: 'Tamper', value: config.tamper_enabled ? `${config.tamper_chance}%` : 'Disabled' },
    ];
    
    items.forEach(item => {
        html += `<div class="config-item">
            <span class="config-key">${item.key}:</span>
            <span class="config-value">${item.value}</span>
        </div>`;
    });
    
    display.innerHTML = html;
}

// ============================================================================
// Button Actions
// ============================================================================

async function startSimulation() {
    /**
     * เริ่ม network impairment
     */
    if (AppState.isRunning) {
        showToast('Simulation already running!', 'warning');
        return;
    }
    
    try {
        const config = gatherConfigFromUI();
        const response = await apiCall('/start', 'POST', config);
        
        if (response && response.status === 'running') {
            AppState.isRunning = true;
            updateUIState();
            showToast('✓ Network impairment started!', 'success');
            
            // Start stats polling
            startStatsPoll();
        }
    } catch (error) {
        showToast(`Failed to start: ${error}`, 'error');
    }
}

async function stopSimulation() {
    /**
     * หยุด network impairment
     */
    if (!AppState.isRunning) {
        showToast('Simulation not running!', 'warning');
        return;
    }
    
    try {
        const response = await apiCall('/stop', 'POST');
        
        if (response && response.status === 'stopped') {
            AppState.isRunning = false;
            updateUIState();
            stopStatsPoll();
            showToast('✓ Network impairment stopped!', 'success');
        }
    } catch (error) {
        showToast(`Failed to stop: ${error}`, 'error');
    }
}

async function resetStats() {
    /**
     * Reset statistics
     */
    try {
        const response = await apiCall('/reset-stats', 'POST');
        
        if (response && response.status === 'ok') {
            updateStats({ 
                processed: 0, 
                dropped: 0, 
                delayed: 0, 
                duplicated: 0, 
                tampered: 0, 
                out_of_order: 0, 
                queue_size: 0 
            });
            showToast('✓ Statistics reset!', 'success');
        }
    } catch (error) {
        showToast(`Failed to reset stats: ${error}`, 'error');
    }
}

async function exitAndDelete() {
    /**
     * Exit และ delete ตัวเอง
     */
    const confirmed = confirm(
        'Are you sure you want to exit and delete this application?\n\n' +
        'This action will:\n' +
        '- Stop the network impairment\n' +
        '- Close this window\n' +
        '- Delete the executable file'
    );
    
    if (!confirmed) return;
    
    try {
        // Stop simulation
        await stopSimulation();
        
        // Give it a moment to stop
        await new Promise(resolve => setTimeout(resolve, 500));
        
        showToast('Deleting application...', 'info');
        
        // Call delete endpoint (if implemented)
        // For now, just close the window
        // The server will handle self-deletion
        window.close();
        
    } catch (error) {
        showToast(`Error during exit: ${error}`, 'error');
    }
}

// ============================================================================
// UI State Management
// ============================================================================

function updateUIState() {
    /**
     * Update button states based on AppState
     */
    UI.startBtn.disabled = AppState.isRunning;
    UI.stopBtn.disabled = !AppState.isRunning;
    
    // Update status display
    if (AppState.isRunning) {
        UI.engineStatus.textContent = 'Running';
        UI.engineStatus.className = 'status-value running';
    } else {
        UI.engineStatus.textContent = 'Stopped';
        UI.engineStatus.className = 'status-value stopped';
    }
    
    updateConfigDisplay();
}

// ============================================================================
// Statistics Polling
// ============================================================================

function startStatsPoll() {
    /**
     * Start polling statistics every 500ms
     */
    if (AppState.updateInterval) {
        clearInterval(AppState.updateInterval);
    }
    
    AppState.updateInterval = setInterval(() => {
        updateStatsDisplay();
    }, 500);
}

function stopStatsPoll() {
    /**
     * Stop polling statistics
     */
    if (AppState.updateInterval) {
        clearInterval(AppState.updateInterval);
        AppState.updateInterval = null;
    }
}

async function updateStatsDisplay() {
    /**
     * โหลดและแสดง statistics
     */
    const stats = await apiCall('/stats');
    if (stats) {
        updateStats(stats);
    }
}

function updateStats(stats) {
    /**
     * Update stats display
     */
    UI.statProcessed.textContent = stats.processed || 0;
    UI.statDropped.textContent = stats.dropped || 0;
    UI.statDelayed.textContent = stats.delayed || 0;
    UI.statDuplicated.textContent = stats.duplicated || 0;
    UI.statTampered.textContent = stats.tampered || 0;
    UI.statOOO.textContent = stats.out_of_order || 0;
    UI.statQueueSize.textContent = stats.queue_size || 0;
    
    AppState.previousStats = stats;
}

// ============================================================================
// Initialization
// ============================================================================

async function initialize() {
    /**
     * Initialize the application
     */
    console.log('Initializing Network Impairment Tool...');
    
    try {
        // Setup sliders
        setupSliders();
        
        // Load initial config
        await loadConfigFromServer();
        
        // Setup event listeners
        UI.startBtn.addEventListener('click', startSimulation);
        UI.stopBtn.addEventListener('click', stopSimulation);
        UI.resetStatsBtn.addEventListener('click', resetStats);
        UI.deleteBtn.addEventListener('click', exitAndDelete);
        
        // Update config display when sliders change
        const configControls = [
            UI.filterInput,
            UI.lagCheck, UI.lagSlider,
            UI.dropCheck, UI.dropSlider,
            UI.throttleCheck, UI.throttleTimeSlider, UI.throttleChanceSlider,
            UI.duplicateCheck, UI.duplicateCountSlider, UI.duplicateChanceSlider,
            UI.oooCheck, UI.oooChanceSlider,
            UI.tamperCheck, UI.tamperChanceSlider,
        ];
        
        configControls.forEach(control => {
            if (control) {
                control.addEventListener('change', updateConfigDisplay);
                control.addEventListener('input', updateConfigDisplay);
            }
        });
        
        // Initial UI state
        updateUIState();
        
        // Try to check if running (first stats fetch)
        const initialStats = await apiCall('/stats');
        if (initialStats && initialStats.running) {
            AppState.isRunning = true;
            updateUIState();
            startStatsPoll();
        }
        
        console.log('Initialization complete!');
        showToast('✓ Application loaded', 'success');
        
    } catch (error) {
        console.error('Initialization error:', error);
        showToast(`Initialization error: ${error}`, 'error');
    }
}

// ============================================================================
// Entry Point
// ============================================================================

// Wait for DOM to be ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}
