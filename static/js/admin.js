// ─── Admin Panel JavaScript ────────────────────────────────────────────

// ─── User Actions ──────────────────────────────────────────────────────
async function userAction(username, action) {
    if (!confirm(`Are you sure you want to ${action} ${username}?`)) return;
    
    try {
        const r = await fetch(`/admin/user/${username}/${action}`, { method: 'POST' });
        const d = await r.json();
        if (d.success) {
            showToast(`✅ ${action} successful`, '#22c55e');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('❌ ' + (d.error || 'Action failed'), '#ef4444');
        }
    } catch(e) {
        showToast('❌ Error performing action', '#ef4444');
    }
}

// ─── Change Plan ──────────────────────────────────────────────────────
async function changePlan(username) {
    const plan = prompt('Enter plan (free/pro/business/enterprise):');
    if (!plan) return;
    
    try {
        const r = await fetch(`/admin/user/${username}/plan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ plan })
        });
        const d = await r.json();
        if (d.success) {
            showToast('✅ Plan updated', '#22c55e');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('❌ ' + (d.error || 'Failed'), '#ef4444');
        }
    } catch(e) {
        showToast('❌ Error updating plan', '#ef4444');
    }
}

// ─── Add Balance ──────────────────────────────────────────────────────
async function addBalance(username) {
    const amount = prompt('Enter amount to add:');
    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) return;
    
    try {
        const r = await fetch('/admin/balance/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, amount: parseFloat(amount) })
        });
        const d = await r.json();
        if (d.success) {
            showToast(`✅ Added $${amount} to ${username}`, '#22c55e');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('❌ ' + (d.error || 'Failed'), '#ef4444');
        }
    } catch(e) {
        showToast('❌ Error adding balance', '#ef4444');
    }
}

// ─── Create Announcement ──────────────────────────────────────────────
async function createAnnouncement() {
    const title = document.getElementById('annTitle').value.trim();
    const content = document.getElementById('annContent').value.trim();
    const priority = parseInt(document.getElementById('annPriority').value) || 0;
    
    if (!title || !content) {
        showToast('❌ Title and content required', '#ef4444');
        return;
    }
    
    try {
        const r = await fetch('/admin/announcement', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content, priority })
        });
        const d = await r.json();
        if (d.success) {
            showToast('✅ Announcement created', '#22c55e');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('❌ ' + (d.error || 'Failed'), '#ef4444');
        }
    } catch(e) {
        showToast('❌ Error creating announcement', '#ef4444');
    }
}

// ─── Backup ────────────────────────────────────────────────────────────
async function createBackup() {
    if (!confirm('Create full backup?')) return;
    
    try {
        const r = await fetch('/admin/backup', { method: 'POST' });
        const blob = await r.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `backup_${new Date().toISOString().slice(0,10)}.zip`;
        a.click();
        showToast('✅ Backup downloaded', '#22c55e');
    } catch(e) {
        showToast('❌ Backup failed', '#ef4444');
    }
}

// ─── Tab Switching ─────────────────────────────────────────────────────
function switchTab(tab, el) {
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    if (el) el.classList.add('active');
    }
