// ─── SHAPPNO VPS ─── Main JavaScript ──────────────────────────────────

// ─── Color Cycling ──────────────────────────────────────────────────────
let hue = 0;
setInterval(() => {
    hue = (hue + 6) % 360;
    const ac = `hsl(${hue}, 90%, 58%)`;
    document.documentElement.style.setProperty('--ac', ac);
    document.documentElement.style.setProperty('--ac-dim', `hsla(${hue}, 90%, 58%, 0.55)`);
    document.documentElement.style.setProperty('--ac-lite', `hsla(${hue}, 90%, 58%, 0.10)`);
}, 100);

// ─── Toast Notification ────────────────────────────────────────────────
function showToast(message, color) {
    const toast = document.getElementById('toast');
    if (!toast) {
        const t = document.createElement('div');
        t.id = 'toast';
        t.textContent = message;
        t.style.cssText = `
            position: fixed; bottom: 80px; right: 20px;
            background: #0a0008; border: 1px solid ${color || 'var(--ac)'};
            border-radius: 10px; padding: 12px 18px; font-size: 13px;
            color: ${color || 'var(--ac)'}; transform: translateY(80px);
            opacity: 0; transition: all 0.3s; z-index: 200;
            box-shadow: 0 0 20px var(--ac-lite);
            font-family: 'JetBrains Mono', monospace;
        `;
        document.body.appendChild(t);
        setTimeout(() => {
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 3000);
        }, 100);
        return;
    }
    toast.textContent = message;
    toast.style.borderColor = color || getComputedStyle(document.documentElement).getPropertyValue('--ac').trim();
    toast.style.color = color || getComputedStyle(document.documentElement).getPropertyValue('--ac').trim();
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

// ─── Fetch Stats ────────────────────────────────────────────────────────
async function fetchStats() {
    try {
        const r = await fetch('/api/stats');
        const d = await r.json();
        const cpu = document.getElementById('statCpu');
        const ram = document.getElementById('statRam');
        const disk = document.getElementById('statDisk');
        const uptime = document.getElementById('statUptime');
        if (cpu) cpu.textContent = 'CPU: ' + d.cpu.toFixed(1) + '%';
        if (ram) ram.textContent = 'RAM: ' + d.ram.toFixed(1) + '%';
        if (disk) disk.textContent = 'DISK: ' + d.disk.toFixed(1) + '%';
        if (uptime) uptime.textContent = Math.floor(d.uptime / 3600) + 'h';
    } catch(e) {}
}

// ─── Modal Helpers ─────────────────────────────────────────────────────
function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('show');
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove('show');
}

// ─── Copy to Clipboard ─────────────────────────────────────────────────
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied: ' + text, '#fbbf24');
    }).catch(() => {
        // Fallback
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
        showToast('Copied: ' + text, '#fbbf24');
    });
}

// ─── Initialize ────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
    fetchStats();
    setInterval(fetchStats, 5000);
});