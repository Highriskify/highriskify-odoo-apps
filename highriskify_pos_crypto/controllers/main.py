# -*- coding: utf-8 -*-

import json
import logging
from html import escape
from urllib.parse import urlparse

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class HighriskifyPosCryptoController(http.Controller):

    @http.route('/pos/highriskify_crypto/go/<int:tx_id>/<string:nonce>', type='http', auth='public', methods=['GET', 'POST'], csrf=False, save_session=False)
    def highriskify_pos_crypto_go(self, tx_id, nonce, **data):
        """Validated bridge/redirect to HighRiskify hosted crypto checkout."""
        tx = request.env['highriskify.pos.crypto.transaction'].sudo().browse(tx_id).exists()
        if not tx or not tx.nonce or nonce != tx.nonce or not tx.checkout_url:
            return request.not_found()

        target_url = tx.checkout_url
        parsed = urlparse(target_url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            _logger.error('HighRiskify POS Crypto invalid hosted checkout URL for %s: %s', tx.name, target_url)
            return request.make_response(
                'HighRiskify hosted checkout URL is invalid. Please check POS payment method settings.',
                status=400,
                headers=[('Content-Type', 'text/plain; charset=utf-8'), ('Cache-Control', 'no-store')],
            )
        return request.make_response(
            '',
            status=302,
            headers=[
                ('Location', target_url),
                ('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0'),
                ('Pragma', 'no-cache'),
                ('Referrer-Policy', 'no-referrer'),
            ],
        )

    @http.route('/pos/highriskify_crypto/pay/<int:tx_id>/<string:nonce>', type='http', auth='public', methods=['GET', 'POST'], csrf=False, save_session=False)
    def highriskify_pos_crypto_payment_page(self, tx_id, nonce, **data):
        """Internal QR payment page for documented single-network wallet/QR flow."""
        tx = request.env['highriskify.pos.crypto.transaction'].sudo().browse(tx_id).exists()
        if not tx or not tx.nonce or nonce != tx.nonce:
            return request.not_found()

        qr_src = ''
        if tx.qr_code:
            qr_src = f"data:image/png;base64,{escape(tx.qr_code, quote=True)}"
        amount = tx.pos_payment_method_id._highriskify_crypto_format_amount(tx.expected_crypto_amount or tx.amount)
        ticker_label = escape((tx.ticker or '').upper(), quote=False)
        wallet = escape(tx.temp_wallet or '', quote=False)
        reference = escape(tx.name or '', quote=False)
        status_url = escape(f'/pos/highriskify_crypto/status/{tx.id}/{tx.nonce}', quote=True)
        state = escape(tx.state or '', quote=False)
        txid_out = escape(tx.txid_out or '', quote=False)
        currency = escape(tx.currency_name or 'USD', quote=False)
        fiat_amount = escape(tx.pos_payment_method_id._highriskify_crypto_format_amount(tx.amount), quote=False)

        html = f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="referrer" content="no-referrer">
    <title>HighRiskify POS Crypto Payment</title>
    <style>
        :root {{ --bg:#f4f7fb; --card:#fff; --ink:#111827; --muted:#667085; --line:#e5e7eb; --brand:#2563eb; --brand-dark:#1d4ed8; --good:#16a34a; --warn:#f59e0b; --bad:#dc2626; }}
        * {{ box-sizing:border-box; }}
        body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif; background:radial-gradient(circle at top left,rgba(37,99,235,.18),transparent 36%),radial-gradient(circle at bottom right,rgba(16,185,129,.12),transparent 32%),var(--bg); color:var(--ink); min-height:100vh; display:flex; align-items:center; justify-content:center; padding:24px; }}
        .wrap {{ width:min(1050px,100%); }}
        .shell {{ display:grid; grid-template-columns:1fr 1.15fr; gap:18px; align-items:stretch; }}
        .card {{ background:rgba(255,255,255,.94); backdrop-filter:blur(12px); border:1px solid rgba(229,231,235,.9); border-radius:28px; box-shadow:0 24px 80px rgba(15,23,42,.13); overflow:hidden; }}
        .left {{ padding:28px; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; }}
        .brand {{ display:inline-flex; align-items:center; gap:10px; padding:8px 13px; border:1px solid var(--line); border-radius:999px; color:var(--muted); font-size:13px; margin-bottom:18px; background:#fff; }}
        .dot {{ width:9px; height:9px; border-radius:999px; background:var(--brand); box-shadow:0 0 0 5px rgba(37,99,235,.12); }}
        h1 {{ margin:0 0 9px; font-size:clamp(28px,4vw,44px); letter-spacing:-.04em; line-height:1; }}
        .subtitle {{ color:var(--muted); margin:0 0 22px; line-height:1.55; max-width:420px; }}
        .qrbox {{ width:min(310px,100%); aspect-ratio:1; border-radius:24px; background:#fff; border:1px solid var(--line); box-shadow:inset 0 0 0 10px #f9fafb; padding:22px; display:flex; align-items:center; justify-content:center; }}
        .qrbox img {{ width:100%; height:100%; object-fit:contain; }}
        .right {{ padding:28px; }}
        .amount {{ border-radius:22px; padding:22px; background:linear-gradient(135deg,#111827,#1f2937); color:#fff; margin-bottom:16px; }}
        .label {{ color:rgba(255,255,255,.68); font-size:13px; margin-bottom:7px; }}
        .crypto {{ font-size:clamp(26px,4vw,42px); font-weight:800; letter-spacing:-.035em; word-break:break-word; }}
        .ticker {{ color:#bfdbfe; font-weight:750; margin-top:6px; }}
        .grid {{ display:grid; gap:12px; }}
        .info {{ border:1px solid var(--line); border-radius:18px; padding:15px; background:#fff; }}
        .info .k {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.08em; font-weight:700; }}
        .info .v {{ margin-top:7px; font-weight:700; word-break:break-all; line-height:1.45; }}
        .actions {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:16px; }}
        button {{ border:0; border-radius:14px; padding:12px 15px; font-weight:800; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; gap:8px; }}
        .primary {{ background:var(--brand); color:#fff; }} .primary:hover {{ background:var(--brand-dark); }}
        .ghost {{ background:#eef2ff; color:#1e40af; }}
        .status {{ margin-top:16px; border-radius:18px; padding:14px 15px; background:#fffbeb; color:#92400e; border:1px solid #fde68a; font-weight:750; }}
        .status.done {{ background:#ecfdf5; color:#166534; border-color:#bbf7d0; }} .status.error {{ background:#fef2f2; color:#991b1b; border-color:#fecaca; }}
        .tiny {{ color:var(--muted); font-size:12px; line-height:1.5; margin-top:12px; }}
        @media (max-width:860px) {{ body {{ padding:14px; align-items:flex-start; }} .shell {{ grid-template-columns:1fr; }} .left,.right {{ padding:20px; }} }}
    </style>
</head>
<body>
    <main class="wrap">
        <section class="shell">
            <div class="card left">
                <div class="brand"><span class="dot"></span> HighRiskify secure crypto checkout</div>
                <h1>Scan & Pay</h1>
                <p class="subtitle">Send the exact crypto amount below to this unique receiving wallet. The POS payment line will update after confirmed payment.</p>
                <div class="qrbox">{'<img src="' + qr_src + '" alt="Crypto payment QR code">' if qr_src else '<strong>QR unavailable</strong>'}</div>
            </div>
            <div class="card right">
                <div class="amount">
                    <div class="label">Amount to send</div>
                    <div class="crypto" id="payAmount">{escape(amount, quote=False)}</div>
                    <div class="ticker">{ticker_label}</div>
                </div>
                <div class="grid">
                    <div class="info"><div class="k">POS amount</div><div class="v">{fiat_amount} {currency}</div></div>
                    <div class="info"><div class="k">Receiving wallet</div><div class="v" id="walletAddress">{wallet}</div></div>
                    <div class="info"><div class="k">Order reference</div><div class="v">{reference}</div></div>
                    <div class="info"><div class="k">Current status</div><div class="v" id="currentState">{state}{(' — TXID Out: ' + txid_out) if txid_out else ''}</div></div>
                </div>
                <div class="actions">
                    <button class="primary" onclick="copyText('walletAddress')">Copy wallet</button>
                    <button class="ghost" onclick="copyText('payAmount')">Copy amount</button>
                    <button class="ghost" onclick="pollStatus(true)">I've paid — check status</button>
                </div>
                <div class="status" id="statusBox">Waiting for confirmed crypto payment…</div>
                <p class="tiny">Do not close the POS payment screen. This page only displays payment instructions; the POS screen is polling Odoo for the confirmed callback.</p>
            </div>
        </section>
    </main>
    <script>
        const statusUrl = "{status_url}";
        function copyText(id) {{
            const el = document.getElementById(id);
            const txt = el ? el.innerText.trim() : '';
            if (txt && navigator.clipboard) navigator.clipboard.writeText(txt);
        }}
        async function pollStatus(manual) {{
            try {{
                const res = await fetch(statusUrl, {{ cache: 'no-store' }});
                const data = await res.json();
                const state = data.state || 'pending';
                const txid = data.txid_out || data.txid_in || '';
                const current = document.getElementById('currentState');
                const box = document.getElementById('statusBox');
                current.innerText = state + (txid ? ' — TXID: ' + txid : '');
                box.className = 'status';
                if (state === 'done') {{ box.className = 'status done'; box.innerText = 'Payment confirmed. You can return to POS.'; }}
                else if (state === 'error' || state === 'cancel') {{ box.className = 'status error'; box.innerText = data.message || 'Payment was not completed.'; }}
                else {{ box.innerText = manual ? 'Still waiting for confirmed payment…' : 'Waiting for confirmed crypto payment…'; }}
            }} catch (e) {{}}
        }}
        setInterval(() => pollStatus(false), 5000);
        pollStatus(false);
    </script>
</body>
</html>"""
        return request.make_response(html, headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Referrer-Policy', 'no-referrer'),
            ('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0'),
            ('Pragma', 'no-cache'),
        ])

    @http.route('/pos/highriskify_crypto/status/<int:tx_id>/<string:nonce>', type='http', auth='public', methods=['GET'], csrf=False, save_session=False)
    def highriskify_pos_crypto_public_status(self, tx_id, nonce, **data):
        tx = request.env['highriskify.pos.crypto.transaction'].sudo().browse(tx_id).exists()
        if not tx or not tx.nonce or nonce != tx.nonce:
            return request.make_response(json.dumps({'state': 'missing'}), status=404, headers=[('Content-Type', 'application/json')])
        payload = tx._highriskify_crypto_status_payload()
        return request.make_response(json.dumps(payload), headers=[('Content-Type', 'application/json'), ('Cache-Control', 'no-store')])

    @http.route('/pos/highriskify_crypto/callback', type='http', auth='public', methods=['GET', 'POST'], csrf=False, save_session=False)
    def highriskify_pos_crypto_callback(self, **data):
        """Process HighRiskify crypto callbacks for POS payment requests."""
        try:
            reference = data.get('reference') or data.get('order_id')
            if not reference:
                raise ValidationError('HighRiskify POS Crypto callback is missing order_id/reference.')
            tx = request.env['highriskify.pos.crypto.transaction'].sudo().search([('name', '=', reference)], limit=1)
            if not tx:
                raise ValidationError('No HighRiskify POS Crypto transaction found matching reference %s.' % reference)
            tx._highriskify_crypto_process_notification_data(data)
        except ValidationError as exc:
            _logger.warning('HighRiskify POS Crypto callback rejected: %s. Payload: %s', exc, data)
            return request.make_response(str(exc), status=400, headers=[('Content-Type', 'text/plain; charset=utf-8')])
        except Exception:
            _logger.exception('HighRiskify POS Crypto callback processing failed. Payload: %s', data)
            return request.make_response('HighRiskify POS Crypto callback processing failed.', status=500, headers=[('Content-Type', 'text/plain; charset=utf-8')])
        return request.make_response('ok', headers=[('Content-Type', 'text/plain; charset=utf-8')])
