// ─── Dashboard Specific JavaScript ──────────────────────────────────────

// ─── Server Stats Update ────────────────────────────────────────────────
function updateServerStats() {
    fetch('/api/servers')
        .then(r => r.json())
        .then(servers => {
            servers.forEach(server => {
                const name = server.name;
                const cpuEl = document.getElementById('cpu-' + name);
                const memEl = document.getElementById('mem-' + name);
                if (cpuEl) cpuEl.textContent = '⚡ CPU: ' + (server.cpu || 0).toFixed(1) + '%';
                if (memEl) memEl.textContent = '💾 RAM: ' + (server.memory || 0).toFixed(1) + '%';
            });
        })
        .catch(() => {});
}

// ─── Redeem Code ────────────────────────────────────────────────────────
async function redeemCode() {
    const code = document.getElementById('redeemInput').value.trim().toUpperCase();
    if (!code) {
        showToast('Enter a code', '#ef4444');
        return;
    }
    
    try {
        const r = await fetch('/redeem', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });
        const d = await r.json();
        const result = document.getElementById('redeemResult');
        if (d.success) {
            result.innerHTML = `<span style="color:#22c55e">✅ Redeemed $${d.amount}! New balance: $${d.balance}</span>`;
            setTimeout(() => location.reload(), 1500);
        } else {
            result.innerHTML = `<span style="color:#ef4444">❌ ${d.error}</span>`;
        }
    } catch(e) {
        document.getElementById('redeemResult').innerHTML = `<span style="color:#ef4444">❌ Error redeeming code</span>`;
    }
}

// ─── Balance Modal ──────────────────────────────────────────────────────
function showBalanceModal() {
    document.getElementById('balanceModal').classList.add('show');
}

function closeBalanceModal() {
    document.getElementById('balanceModal').classList.remove('show');
}

// ─── Create Server ──────────────────────────────────────────────────────
async function createServer() {
    const form = document.getElementById('createServerForm');
    const formData = new FormData(form);
    
    try {
        const r = await fetch('/server/create', {
            method: 'POST',
            body: formData
        });
        const d = await r.json();
        if (d.success) {
            showToast('Server created successfully!', '#22c55e');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Error: ' + (d.error || 'Unknown error'), '#ef4444');
        }
    } catch(e) {
        showToast('Error creating server', '#ef4444');
    }
}

// ─── Initialize Dashboard ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
    // Update stats every 5 seconds
    updateServerStats();
    setInterval(updateServerStats, 5000);
    
    // Socket.io connection
    const socket = io();
    socket.on('connect', () => console.log('Socket connected'));
    socket.on('server_stats', (stats) => {
        for (const [name, data] of Object.entries(stats)) {
            const cpuEl = document.getElementById('cpu-' + name);
            const memEl = document.getElementById('mem-' + name);
            if (cpuEl) cpuEl.textContent = '⚡ CPU: ' + (data.cpu || 0).toFixed(1) + '%';
            if (memEl) memEl.textContent = '💾 RAM: ' + (data.memory || 0).toFixed(1) + '%';
        }
    });
    socket.on('new_alert', (data) => {
        showToast('⚠️ ' + data.message, '#ef4444');
    });
    socket.on('new_announcement', (data) => {
        showToast('📢 ' + data.title + ' - ' + data.content, '#fbbf24');
    });
});