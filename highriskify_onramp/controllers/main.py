# -*- coding: utf-8 -*-

import logging
import json
from html import escape

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .. import const

_logger = logging.getLogger(__name__)


class HighRiskifyOnrampController(http.Controller):
    _return_url = '/payment/highriskify_onramp/return'
    _callback_url = '/payment/highriskify_onramp/callback'

    @http.route('/payment/highriskify_onramp/go/<int:tx_id>/<string:nonce>', type='http', auth='public', methods=['GET', 'POST'], csrf=False, save_session=False)
    def highriskify_onramp_go(self, tx_id, nonce, **data):
        """No-referrer bridge to HighRiskify hosted checkout.

        This fixes the case where the exact pay.php URL works when copied into a
        fresh tab, but fails when the browser arrives there directly from Odoo.
        """
        tx = request.env['payment.transaction'].sudo().browse(tx_id).exists()
        if not tx or tx.provider_code != const.PROVIDER_CODE or not tx.highriskify_nonce or nonce != tx.highriskify_nonce:
            return request.not_found()

        amount = tx.highriskify_original_amount or tx.amount
        currency = tx.highriskify_original_currency or tx.currency_id.name or 'USD'
        checkout_url = tx._highriskify_build_pay_url(amount, currency)
        checkout_url_attr = escape(checkout_url, quote=True)
        checkout_url_js = json.dumps(checkout_url)

        body = """<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <meta name=\"referrer\" content=\"no-referrer\">
    <meta http-equiv=\"refresh\" content=\"1;url=%s\">
    <title>Redirecting to HighRiskify Checkout</title>
    <style>
        body { font-family: Arial, sans-serif; background:#f7f7fb; color:#20242c; display:flex; align-items:center; justify-content:center; min-height:100vh; margin:0; }
        .box { max-width:520px; background:#fff; border-radius:18px; padding:34px; box-shadow:0 14px 40px rgba(16,24,40,.10); text-align:center; }
        .btn { display:inline-block; margin-top:18px; padding:12px 18px; border-radius:10px; background:#6f4e6f; color:#fff; text-decoration:none; font-weight:700; }
        .muted { color:#667085; font-size:14px; line-height:1.5; }
    </style>
    <script>
        window.addEventListener('load', function () {
            setTimeout(function () { window.location.replace(%s); }, 150);
        });
    </script>
</head>
<body>
    <div class=\"box\">
        <h2>Redirecting to secure checkout…</h2>
        <p class=\"muted\">If it does not continue automatically, click the button below.</p>
        <a class=\"btn\" href=\"%s\" rel=\"noreferrer noopener\" referrerpolicy=\"no-referrer\">Continue to HighRiskify</a>
    </div>
</body>
</html>""" % (checkout_url_attr, checkout_url_js, checkout_url_attr)
        return request.make_response(body, headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Referrer-Policy', 'no-referrer'),
            ('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0'),
            ('Pragma', 'no-cache'),
        ])

    @http.route([_return_url, _callback_url], type='http', auth='public', methods=['GET', 'POST'], csrf=False, save_session=False)
    def highriskify_onramp_return(self, **data):
        """Process HighRiskify hosted checkout callback/IPN.

        Supports both the older /return URL and the newer /callback URL.
        Server-to-server IPNs receive a plain 'ok'. If the hosted checkout
        returns the customer through a normal browser GET, Odoo shows the
        standard payment status/confirmation page after processing.
        """
        try:
            tx_model = request.env['payment.transaction'].sudo()
            process_method = getattr(tx_model, '_process', None)
            if callable(process_method):
                process_method(const.PROVIDER_CODE, data)
            else:
                tx_model._handle_notification_data(const.PROVIDER_CODE, data)
        except ValidationError as exc:
            _logger.warning('HighRiskify callback rejected: %s. Payload: %s', exc, data)
            return request.make_response(str(exc), status=400, headers=[('Content-Type', 'text/plain; charset=utf-8'), ('Cache-Control', 'no-store')])
        except Exception:
            _logger.exception('HighRiskify callback processing failed. Payload: %s', data)
            return request.make_response('HighRiskify callback processing failed.', status=500, headers=[('Content-Type', 'text/plain; charset=utf-8'), ('Cache-Control', 'no-store')])

        accept = (request.httprequest.headers.get('Accept') or '').lower()
        if request.httprequest.method == 'GET' and 'text/html' in accept:
            return request.redirect('/payment/status')
        return request.make_response('ok', headers=[('Content-Type', 'text/plain; charset=utf-8'), ('Cache-Control', 'no-store')])
