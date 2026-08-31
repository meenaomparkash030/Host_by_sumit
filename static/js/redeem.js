// ─── Redeem System JavaScript ──────────────────────────────────────────

// ─── Generate Redeem Code ──────────────────────────────────────────────
async function generateRedeemCode() {
    const amount = parseFloat(document.getElementById('redeemAmount').value);
    const max_uses = parseInt(document.getElementById('redeemMaxUses').value) || 1;
    const expires_in = parseInt(document.getElementById('redeemExpires').value) || 30;
    
    if (!amount || amount <= 0) {
        showToast('❌ Enter valid amount', '#ef4444');
        return;
    }
    
    try {
        const r = await fetch('/admin/redeem/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount, max_uses, expires_in })
        });
        const d = await r.json();
        if (d.success) {
            document.getElementById('newCodeDisplay').textContent = d.code;
            document.getElementById('newCodeAmount').textContent = '$' + d.amount;
            document.getElementById('newCodeResult').style.display = 'block';
            showToast('✅ Code generated: ' + d.code, '#22c55e');
        } else {
            showToast('❌ ' + (d.error || 'Failed'), '#ef4444');
        }
    } catch(e) {
        showToast('❌ Error generating code', '#ef4444');
    }
}

// ─── Copy Code ─────────────────────────────────────────────────────────
function copyRedeemCode() {
    const code = document.getElementById('newCodeDisplay').textContent;
    navigator.clipboard.writeText(code).then(() => {
        showToast('✅ Copied: ' + code, '#fbbf24');
    }).catch(() => {
        const ta = document.createElement('textarea');
        ta.value = code;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
        showToast('✅ Copied: ' + code, '#fbbf24');
    });
}

// ─── Redeem Code (User) ────────────────────────────────────────────────
async function redeemUserCode() {
    const code = document.getElementById('redeemUserInput').value.trim().toUpperCase();
    if (!code) {
        showToast('❌ Enter a code', '#ef4444');
        return;
    }
    
    try {
        const r = await fetch('/redeem', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });
        const d = await r.json();
        if (d.success) {
            showToast(`✅ Redeemed $${d.amount}! New balance: $${d.balance}`, '#22c55e');
            document.getElementById('redeemResult').innerHTML = 
                `<span style="color:#22c55e">✅ Redeemed $${d.amount}! New balance: $${d.balance}</span>`;
            setTimeout(() => location.reload(), 1500);
        } else {
            showToast('❌ ' + (d.error || 'Invalid code'), '#ef4444');
            document.getElementById('redeemResult').innerHTML = `<span style="color:#ef4444">❌ ${d.error}</span>`;
        }
    } catch(e) {
        showToast('❌ Error redeeming code', '#ef4444');
    }
}

// ─── Create Coupon ──────────────────────────────────────────────────────
async function createCoupon() {
    const code = document.getElementById('couponCode').value.toUpperCase();
    const type = document.getElementById('couponType').value;
    const value = parseFloat(document.getElementById('couponValue').value);
    const min_amount = parseFloat(document.getElementById('couponMinAmount').value) || 0;
    const max_discount = parseFloat(document.getElementById('couponMaxDiscount').value) || 0;
    const max_uses = parseInt(document.getElementById('couponMaxUses').value) || 1;
    const expires_in = parseInt(document.getElementById('couponExpires').value) || 30;
    
    if (!code || !value || value <= 0) {
        showToast('❌ Code and value required', '#ef4444');
        return;
    }
    
    try {
        const r = await fetch('/admin/coupon/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, type, value, min_amount, max_discount, max_uses, expires_in })
        });
        const d = await r.json();
        if (d.success) {
            showToast('✅ Coupon created: ' + code, '#22c55e');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('❌ ' + (d.error || 'Failed'), '#ef4444');
        }
    } catch(e) {
        showToast('❌ Error creating coupon', '#ef4444');
    }
}