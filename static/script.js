/**
 * Cloud Resource Manager - Frontend JavaScript
 * Handles API communication, UI rendering, and user interactions
 */

const API_BASE = '';
let currentAction = 'request';
let systemState = null;

// ===== DOM Elements =====
const resourcesGrid = document.getElementById('resourcesGrid');
const tableHeader = document.getElementById('tableHeader');
const tableBody = document.getElementById('tableBody');
const serviceSelect = document.getElementById('serviceSelect');
const resourceInputs = document.getElementById('resourceInputs');
const resourceForm = document.getElementById('resourceForm');
const responseMessage = document.getElementById('responseMessage');
const logContainer = document.getElementById('logContainer');
const statusBadge = document.getElementById('statusBadge');
const statusText = document.getElementById('statusText');
const safeSequence = document.getElementById('safeSequence');
const safeSequenceText = document.getElementById('safeSequenceText');
const resetBtn = document.getElementById('resetBtn');
const submitBtn = document.getElementById('submitBtn');

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    loadState();
    setupScenarioButtons();
    setupActionToggle();
    setupForm();
    setupResetButton();
});

// ===== API Functions =====
async function loadState() {
    try {
        const response = await fetch(`${API_BASE}/api/state`);
        systemState = await response.json();
        renderAll();
    } catch (error) {
        console.error('Failed to load state:', error);
        showResponse('Failed to connect to server. Make sure the Flask app is running.', 'error');
    }
}

async function loadScenario(scenario) {
    try {
        await fetch(`${API_BASE}/api/scenario/${scenario}`, { method: 'POST' });
        await loadState();
    } catch (error) {
        console.error('Failed to load scenario:', error);
    }
}

async function submitRequest(serviceId, resources) {
    const endpoint = currentAction === 'request' ? '/api/request' : '/api/release';
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ service_id: serviceId, resources })
        });
        const result = await response.json();
        await loadState();
        return result;
    } catch (error) {
        console.error('Request failed:', error);
        return { success: false, message: 'Failed to connect to server.' };
    }
}

async function resetSystem() {
    try {
        await fetch(`${API_BASE}/api/reset`, { method: 'POST' });
        await loadState();
        showResponse('System has been reset to default state.', 'success');
    } catch (error) {
        console.error('Reset failed:', error);
    }
}

// ===== Rendering =====
function renderAll() {
    if (!systemState) return;
    renderResources();
    renderTable();
    renderServiceSelect();
    renderResourceInputs();
    renderSafeSequence();
    renderStatusBadge();
    renderActivityLog();
}

function renderResources() {
    resourcesGrid.innerHTML = '';
    const totalResources = systemState.available.map((avail, i) => {
        const allocated = systemState.allocation.reduce((sum, row) => sum + row[i], 0);
        return allocated + avail;
    });

    const barColors = ['cpu', 'memory', 'gpu', 'network'];

    systemState.available.forEach((avail, i) => {
        const total = totalResources[i];
        const usagePercent = total > 0 ? ((total - avail) / total) * 100 : 0;
        const colorClass = barColors[i] || 'default';

        const card = document.createElement('div');
        card.className = 'resource-card';
        card.innerHTML = `
            <div class="resource-name">${systemState.resource_names[i]}</div>
            <div class="resource-value">${avail}</div>
            <div class="resource-bar-container">
                <div class="resource-bar ${colorClass}" style="width: ${usagePercent}%"></div>
            </div>
        `;
        resourcesGrid.appendChild(card);
    });
}

function renderTable() {
    // Header
    tableHeader.innerHTML = '<th>Service</th>';
    systemState.resource_names.forEach(name => {
        const th = document.createElement('th');
        th.textContent = name;
        tableHeader.appendChild(th);
    });

    // Body - show Allocation, Maximum, Need
    tableBody.innerHTML = '';

    const sections = [
        { label: 'Allocation', data: systemState.allocation },
        { label: 'Maximum', data: systemState.maximum },
        { label: 'Need', data: systemState.need }
    ];

    sections.forEach(section => {
        // Section header row
        const headerRow = document.createElement('tr');
        headerRow.innerHTML = `<td colspan="${systemState.num_resources + 1}" style="background: var(--bg-secondary); font-weight: 600; color: var(--accent-blue); font-size: 0.8rem; text-transform: uppercase;">${section.label}</td>`;
        tableBody.appendChild(headerRow);

        section.data.forEach((row, i) => {
            const tr = document.createElement('tr');
            const nameTd = document.createElement('td');
            nameTd.textContent = systemState.service_names[i];
            tr.appendChild(nameTd);

            row.forEach(val => {
                const td = document.createElement('td');
                td.textContent = val;
                tr.appendChild(td);
            });

            tableBody.appendChild(tr);
        });
    });
}

function renderServiceSelect() {
    serviceSelect.innerHTML = '';
    systemState.service_names.forEach((name, i) => {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = name;
        serviceSelect.appendChild(option);
    });
}

function renderResourceInputs() {
    resourceInputs.innerHTML = '';
    systemState.resource_names.forEach((name, i) => {
        const group = document.createElement('div');
        group.className = 'input-group';
        group.innerHTML = `
            <label>${name}</label>
            <input type="number" name="resource_${i}" min="0" value="0" placeholder="0">
        `;
        resourceInputs.appendChild(group);
    });
}

function renderSafeSequence() {
    if (systemState.is_safe && systemState.safe_sequence_names.length > 0) {
        safeSequence.className = 'safe-sequence';
        safeSequenceText.textContent = systemState.safe_sequence_names.join(' \u2192 ');
    } else {
        safeSequence.className = 'safe-sequence unsafe';
        safeSequenceText.textContent = 'NO SAFE SEQUENCE - UNSAFE STATE';
    }
}

function renderStatusBadge() {
    if (systemState.is_safe) {
        statusBadge.className = 'status-badge';
        statusText.textContent = 'SAFE';
    } else {
        statusBadge.className = 'status-badge unsafe';
        statusText.textContent = 'UNSAFE';
    }
}

function renderActivityLog() {
    if (!systemState.request_log || systemState.request_log.length === 0) {
        logContainer.innerHTML = '<p class="empty-log">No activity yet. Request or release resources to see the log.</p>';
        return;
    }

    logContainer.innerHTML = '';
    // Show most recent first
    const reversed = [...systemState.request_log].reverse();

    reversed.forEach(entry => {
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';

        let statusClass = 'granted';
        let statusText = 'GRANTED';
        if (entry.status === 'DENIED-UNSAFE') {
            statusClass = 'denied';
            statusText = 'DENIED';
        } else if (entry.status === 'RELEASED') {
            statusClass = 'released';
            statusText = 'RELEASED';
        }

        const serviceName = systemState.service_names[entry.service_id] || `Service ${entry.service_id}`;
        const resourceDetails = entry.request.join(', ');
        const time = new Date(entry.timestamp).toLocaleTimeString();

        logEntry.innerHTML = `
            <span class="log-status ${statusClass}">${statusText}</span>
            <div class="log-content">
                <div class="log-service">${serviceName}</div>
                <div class="log-details">Resources: [${resourceDetails}]</div>
            </div>
            <span class="log-time">${time}</span>
        `;
        logContainer.appendChild(logEntry);
    });
}

// ===== Event Handlers =====
function setupScenarioButtons() {
    document.querySelectorAll('.scenario-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.scenario-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadScenario(btn.dataset.scenario);
        });
    });
}

function setupActionToggle() {
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.action-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentAction = btn.dataset.action;
            submitBtn.textContent = currentAction === 'request' ? 'Submit Request' : 'Release Resources';
        });
    });
}

function setupForm() {
    resourceForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const serviceId = parseInt(serviceSelect.value);
        const resources = [];

        systemState.resource_names.forEach((_, i) => {
            const input = resourceForm.querySelector(`[name="resource_${i}"]`);
            resources.push(parseInt(input.value) || 0);
        });

        // Validate
        if (resources.every(r => r === 0)) {
            showResponse('Please enter at least one resource value greater than 0.', 'error');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';

        const result = await submitRequest(serviceId, resources);

        if (result.success) {
            showResponse(result.message, 'success');
            // Reset input values
            resourceForm.querySelectorAll('input[type="number"]').forEach(input => input.value = 0);
        } else {
            showResponse(result.message, 'error');
        }

        submitBtn.disabled = false;
        submitBtn.textContent = currentAction === 'request' ? 'Submit Request' : 'Release Resources';
    });
}

function setupResetButton() {
    resetBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to reset the system to its default state?')) {
            await resetSystem();
        }
    });
}

// ===== Utilities =====
function showResponse(message, type) {
    responseMessage.textContent = message;
    responseMessage.className = `response-message ${type}`;

    // Auto-hide after 5 seconds
    setTimeout(() => {
        responseMessage.className = 'response-message';
    }, 5000);
}
