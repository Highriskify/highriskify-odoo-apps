# -*- coding: utf-8 -*-

import json
import logging
from html import escape
from urllib.parse import urlparse

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .. import const

_logger = logging.getLogger(__name__)


class CryptoPayMateController(http.Controller):
    _callback_url = '/payment/cryptopaymate_crypto/callback'

    def _cryptopaymate_process_notification(self, notification_data):
        tx_model = request.env['payment.transaction'].sudo()
        handler = getattr(tx_model, '_handle_notification_data', None)
        if handler:
            return handler(const.PROVIDER_CODE, notification_data)

        tx = tx_model._search_by_reference(const.PROVIDER_CODE, notification_data)
        processor = getattr(tx, '_process', None)
        if processor:
            try:
                return processor(const.PROVIDER_CODE, notification_data)
            except TypeError:
                return processor(notification_data)
        return tx._apply_updates(notification_data)

    @http.route('/payment/cryptopaymate_crypto/redirect', type='http', auth='public', methods=['GET', 'POST'], csrf=False, save_session=False)
    def cryptopaymate_redirect_to_hosted(self, reference=None, status_nonce=None, payment_token=None, hosted_url=None, **data):
        reference = (reference or '').strip()
        status_nonce = (status_nonce or '').strip()
        tx = request.env['payment.transaction'].sudo().search([
            ('reference', '=', reference),
            ('provider_code', '=', const.PROVIDER_CODE),
        ], limit=1)
        if not tx or not tx.cryptopaymate_status_nonce or status_nonce != tx.cryptopaymate_status_nonce:
            _logger.warning('HighRiskify Crypto hosted redirect rejected. Reference=%s', reference)
            return request.not_found()

        # Always rebuild the hosted URL from the saved token instead of trusting a URL
        # submitted through the browser or stored by an older module version. This prevents
        # payment_token double-encoding such as %252B, which hosted.php rejects.
        token = tx.cryptopaymate_payment_token or payment_token
        target_url = tx._cryptopaymate_build_hosted_checkout_url(token) if token else ''

        if not target_url or 'payment_token=' not in target_url:
            _logger.error('HighRiskify Crypto hosted redirect missing payment token for transaction %s.', tx.reference)
            return request.make_response(
                'HighRiskify Crypto payment token was not generated. Please go back and try again.',
                status=400,
                headers=[('Content-Type', 'text/plain; charset=utf-8'), ('Cache-Control', 'no-store')],
            )

        # Use a raw 302 Location header. This avoids any Odoo/base_url normalization
        # that can accidentally turn the external hosted checkout URL into the Odoo
        # website domain, e.g. community.highriskify.com/crypto/hosted.php.
        parsed = urlparse(target_url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            _logger.error('HighRiskify Crypto hosted redirect produced invalid URL for %s: %s', tx.reference, target_url)
            return request.make_response(
                'HighRiskify Crypto hosted checkout URL is invalid. Please check provider settings.',
                status=400,
                headers=[('Content-Type', 'text/plain; charset=utf-8'), ('Cache-Control', 'no-store')],
            )
        _logger.info('HighRiskify Crypto redirecting transaction %s to hosted checkout domain %s', tx.reference, parsed.netloc)
        return request.make_response(
            '',
            status=302,
            headers=[('Location', target_url), ('Cache-Control', 'no-store')],
        )

    @http.route('/payment/cryptopaymate_crypto/pay/<int:tx_id>/<string:status_nonce>', type='http', auth='public', methods=['GET', 'POST'], csrf=False, save_session=False)
    def cryptopaymate_payment_page(self, tx_id, status_nonce, **data):
        tx = request.env['payment.transaction'].sudo().browse(tx_id).exists()
        if not tx or tx.provider_code != const.PROVIDER_CODE or not tx.cryptopaymate_status_nonce or status_nonce != tx.cryptopaymate_status_nonce:
            return request.not_found()

        qr_src = ''
        if tx.cryptopaymate_qr_code:
            qr_src = f"data:image/png;base64,{escape(tx.cryptopaymate_qr_code, quote=True)}"

        amount = tx._cryptopaymate_format_amount(tx.cryptopaymate_expected_amount)
        ticker_label = escape((tx.cryptopaymate_ticker or '').upper(), quote=False)
        wallet = escape(tx.cryptopaymate_temp_wallet or '', quote=False)
        reference = escape(tx.reference or '', quote=False)
        status_url = escape(f'/payment/cryptopaymate_crypto/status/{tx.id}/{tx.cryptopaymate_status_nonce}', quote=True)
        check_url = escape(f'/payment/cryptopaymate_crypto/check/{tx.id}/{tx.cryptopaymate_status_nonce}', quote=True)
        payment_status_url = escape('/payment/status', quote=True)
        state = escape(tx.state or '', quote=False)
        txid_out = escape(tx.cryptopaymate_txid_out or '', quote=False)

        html = f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Crypto payment</title>
    <style>
        :root {{
            --bg: #f4f7fb;
            --card: #ffffff;
            --ink: #111827;
            --muted: #667085;
            --line: #e5e7eb;
            --brand: #2563eb;
            --brand-dark: #1d4ed8;
            --good: #16a34a;
            --warn: #f59e0b;
            --bad: #dc2626;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background:
                radial-gradient(circle at top left, rgba(37,99,235,.18), transparent 36%),
                radial-gradient(circle at bottom right, rgba(16,185,129,.12), transparent 32%),
                var(--bg);
            color: var(--ink);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }}
        .wrap {{ width: min(1050px, 100%); }}
        .shell {{
            display: grid;
            grid-template-columns: 1fr 1.15fr;
            gap: 18px;
            align-items: stretch;
        }}
        .card {{
            background: rgba(255,255,255,.92);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(229,231,235,.9);
            border-radius: 28px;
            box-shadow: 0 24px 80px rgba(15, 23, 42, .13);
            overflow: hidden;
        }}
        .left {{
            padding: 28px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }}
        .brand {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 8px 13px;
            border: 1px solid var(--line);
            border-radius: 999px;
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 18px;
            background: #fff;
        }}
        .dot {{ width: 9px; height: 9px; border-radius: 999px; background: var(--brand); box-shadow: 0 0 0 5px rgba(37,99,235,.12); }}
        h1 {{ margin: 0 0 9px; font-size: clamp(28px, 4vw, 44px); letter-spacing: -0.04em; line-height: 1; }}
        .subtitle {{ color: var(--muted); margin: 0 0 22px; line-height: 1.55; max-width: 420px; }}
        .qrbox {{
            width: min(310px, 100%);
            aspect-ratio: 1;
            border-radius: 24px;
            background: #fff;
            border: 1px solid var(--line);
            box-shadow: inset 0 0 0 10px #f9fafb;
            padding: 22px;
            display:flex;
            align-items:center;
            justify-content:center;
        }}
        .qrbox img {{ width: 100%; height: 100%; object-fit: contain; }}
        .right {{ padding: 28px; }}
        .amount {{
            border-radius: 22px;
            padding: 22px;
            background: linear-gradient(135deg, #111827, #1f2937);
            color: #fff;
            margin-bottom: 16px;
        }}
        .label {{ color: rgba(255,255,255,.68); font-size: 13px; margin-bottom: 7px; }}
        .crypto {{ font-size: clamp(26px, 4vw, 42px); font-weight: 800; letter-spacing: -0.035em; word-break: break-word; }}
        .ticker {{ color: #bfdbfe; font-weight: 750; margin-top: 6px; }}
        .grid {{ display: grid; gap: 12px; }}
        .info {{
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 15px;
            background: #fff;
        }}
        .info .k {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; font-weight: 700; }}
        .info .v {{ margin-top: 7px; font-weight: 700; word-break: break-all; line-height: 1.45; }}
        .actions {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 16px; }}
        button, a.btn {{
            border: 0;
            border-radius: 14px;
            padding: 12px 15px;
            font-weight: 800;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        .primary {{ background: var(--brand); color: #fff; }}
        .primary:hover {{ background: var(--brand-dark); }}
        .ghost {{ background: #eef2ff; color: #1e40af; }}
        .status {{
            margin-top: 16px;
            border-radius: 18px;
            padding: 14px 15px;
            background: #fffbeb;
            color: #92400e;
            border: 1px solid #fde68a;
            font-weight: 750;
        }}
        .status.done {{ background: #ecfdf5; color: #166534; border-color: #bbf7d0; }}
        .status.error {{ background: #fef2f2; color: #991b1b; border-color: #fecaca; }}
        .tiny {{ color: var(--muted); font-size: 12px; line-height: 1.5; margin-top: 12px; }}
        @media (max-width: 860px) {{
            body {{ padding: 14px; align-items: flex-start; }}
            .shell {{ grid-template-columns: 1fr; }}
            .left, .right {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
    <main class="wrap">
        <section class="shell">
            <div class="card left">
                <div class="brand"><span class="dot"></span> HighRiskify Crypto secure crypto checkout</div>
                <h1>Scan & Pay</h1>
                <p class="subtitle">Send the exact amount below to this unique receiving wallet. Your order will update automatically after confirmed payment.</p>
                <div class="qrbox">{'<img src="' + qr_src + '" alt="Crypto payment QR code">' if qr_src else '<strong>QR unavailable</strong>'}</div>
            </div>
            <div class="card right">
                <div class="amount">
                    <div class="label">Amount to send</div>
                    <div class="crypto" id="payAmount">{escape(amount, quote=False)}</div>
                    <div class="ticker">{ticker_label}</div>
                </div>

                <div class="grid">
                    <div class="info">
                        <div class="k">Receiving wallet</div>
                        <div class="v" id="walletAddress">{wallet}</div>
                    </div>
                    <div class="info">
                        <div class="k">Order reference</div>
                        <div class="v">{reference}</div>
                    </div>
                    <div class="info">
                        <div class="k">Current status</div>
                        <div class="v" id="currentState">{state}{(' — TXID Out: ' + txid_out) if txid_out else ''}</div>
                    </div>
                </div>

                <div class="actions">
                    <button class="primary" onclick="copyText('walletAddress')">Copy wallet</button>
                    <button class="ghost" onclick="copyText('payAmount')">Copy amount</button>
                    <button class="ghost" id="checkBtn" onclick="manualCheck()">I've paid — check status</button>
                    <a class="btn ghost" href="{payment_status_url}">Return to order status</a>
                </div>

                <div class="status" id="statusBox">Waiting for confirmed blockchain payment…</div>
                <p class="tiny">Do not send from an unsupported network. Sending the wrong coin/network may delay or lose the payment. Only confirmed callbacks complete the Odoo order.</p>
            </div>
        </section>
    </main>
    <script>
        const statusUrl = "{status_url}";
        const checkUrl = "{check_url}";
        const statusBox = document.getElementById('statusBox');
        const stateEl = document.getElementById('currentState');

        async function copyText(id) {{
            const text = document.getElementById(id).innerText.trim();
            try {{
                await navigator.clipboard.writeText(text);
                statusBox.textContent = 'Copied.';
                statusBox.className = 'status done';
                setTimeout(refreshStatus, 1300);
            }} catch (e) {{
                statusBox.textContent = text;
            }}
        }}

        function renderStatus(data) {{
            let label = data.state || 'pending';
            if (data.txid_out) label += ' — TXID Out: ' + data.txid_out;
            stateEl.textContent = label;

            if (data.state === 'done') {{
                statusBox.textContent = 'Payment confirmed. Redirecting to order status…';
                statusBox.className = 'status done';
                setTimeout(() => window.location.href = "{payment_status_url}", 1800);
            }} else if (data.state === 'error' || data.state === 'cancel') {{
                statusBox.textContent = data.message || 'Payment could not be completed. Please contact support.';
                statusBox.className = 'status error';
            }} else {{
                statusBox.textContent = 'Waiting for confirmed blockchain payment…';
                statusBox.className = 'status';
            }}
        }}

        async function refreshStatus() {{
            try {{
                const res = await fetch(statusUrl, {{ cache: 'no-store' }});
                if (res.ok) renderStatus(await res.json());
            }} catch(e) {{}}
        }}

        async function manualCheck() {{
            const btn = document.getElementById('checkBtn');
            btn.disabled = true;
            statusBox.textContent = 'Checking blockchain/payment status…';
            statusBox.className = 'status';
            try {{
                const res = await fetch(checkUrl, {{ cache: 'no-store' }});
                if (res.ok) renderStatus(await res.json());
                else statusBox.textContent = 'Status check failed. The callback may still arrive automatically.';
            }} catch(e) {{
                statusBox.textContent = 'Status check failed. The callback may still arrive automatically.';
            }}
            btn.disabled = false;
        }}

        refreshStatus();
        setInterval(refreshStatus, 8000);
    </script>
</body>
</html>"""
        return request.make_response(html, headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0'),
            ('Pragma', 'no-cache'),
        ])

    @http.route('/payment/cryptopaymate_crypto/status/<int:tx_id>/<string:status_nonce>', type='http', auth='public', methods=['GET'], csrf=False, save_session=False)
    def cryptopaymate_status(self, tx_id, status_nonce, **data):
        tx = request.env['payment.transaction'].sudo().browse(tx_id).exists()
        if not tx or tx.provider_code != const.PROVIDER_CODE or status_nonce != tx.cryptopaymate_status_nonce:
            return request.not_found()

        payload = {
            'state': tx.state,
            'message': tx.state_message or '',
            'reference': tx.reference,
            'txid_in': tx.cryptopaymate_txid_in or '',
            'txid_out': tx.cryptopaymate_txid_out or '',
            'paid_amount': tx.cryptopaymate_paid_amount or 0.0,
            'paid_coin': tx.cryptopaymate_paid_coin or '',
        }
        return request.make_response(json.dumps(payload), headers=[
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Cache-Control', 'no-store'),
        ])

    @http.route('/payment/cryptopaymate_crypto/check/<int:tx_id>/<string:status_nonce>', type='http', auth='public', methods=['GET'], csrf=False, save_session=False)
    def cryptopaymate_check_remote_status(self, tx_id, status_nonce, **data):
        tx = request.env['payment.transaction'].sudo().browse(tx_id).exists()
        if not tx or tx.provider_code != const.PROVIDER_CODE or status_nonce != tx.cryptopaymate_status_nonce:
            return request.not_found()

        try:
            remote = tx._cryptopaymate_remote_status()
            tx.sudo().write({'cryptopaymate_remote_status': str(remote.get('status') or '')})
            if str(remote.get('status') or '').lower() == 'paid':
                notification = dict(remote)
                notification.update({
                    'order_id': tx.reference,
                    'nonce': tx.cryptopaymate_nonce,
                    'address_in': tx.cryptopaymate_temp_wallet,
                    'pending': '0',
                })
                self._cryptopaymate_process_notification(notification)
        except Exception:
            _logger.exception('HighRiskify Crypto manual remote status check failed for transaction %s.', tx.reference)

        tx = tx.sudo().browse(tx.id)
        payload = {
            'state': tx.state,
            'message': tx.state_message or '',
            'reference': tx.reference,
            'txid_in': tx.cryptopaymate_txid_in or '',
            'txid_out': tx.cryptopaymate_txid_out or '',
            'paid_amount': tx.cryptopaymate_paid_amount or 0.0,
            'paid_coin': tx.cryptopaymate_paid_coin or '',
        }
        return request.make_response(json.dumps(payload), headers=[
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Cache-Control', 'no-store'),
        ])

    @http.route(_callback_url, type='http', auth='public', methods=['GET', 'POST'], csrf=False, save_session=False)
    def cryptopaymate_callback(self, **data):
        try:
            self._cryptopaymate_process_notification(data)
        except ValidationError as exc:
            _logger.warning('HighRiskify Crypto callback rejected: %s. Payload: %s', exc, data)
            return request.make_response(str(exc), status=400, headers=[('Content-Type', 'text/plain; charset=utf-8')])
        except Exception:
            _logger.exception('HighRiskify Crypto callback processing failed. Payload: %s', data)
            return request.make_response('HighRiskify Crypto callback processing failed.', status=500, headers=[('Content-Type', 'text/plain; charset=utf-8')])
        return request.make_response('ok', headers=[
            ('Content-Type', 'text/plain; charset=utf-8'),
            ('Cache-Control', 'no-store'),
        ])
