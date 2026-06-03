# -*- coding: utf-8 -*-

import hashlib
import hmac
import json
import logging
import time

import requests

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.float_utils import float_compare

from .. import const

_logger = logging.getLogger(__name__)


class HighriskifyPosCryptoTransaction(models.Model):
    _name = 'highriskify.pos.crypto.transaction'
    _description = 'HighRiskify POS Crypto Transaction'
    _order = 'id desc'

    name = fields.Char(string='Reference', required=True, readonly=True, index=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('error', 'Error'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        readonly=True,
        index=True,
    )
    pos_payment_method_id = fields.Many2one('pos.payment.method', string='Payment Method', required=True, readonly=True, ondelete='restrict')
    pos_config_id = fields.Many2one('pos.config', string='Point of Sale', readonly=True, ondelete='set null')
    pos_session_id = fields.Many2one('pos.session', string='POS Session', readonly=True, ondelete='set null')
    order_uid = fields.Char(string='POS Order UID', readonly=True, index=True)
    order_name = fields.Char(string='POS Order Name', readonly=True)
    amount = fields.Float(string='Original Amount', readonly=True)
    expected_fiat_amount = fields.Float(string='Expected Fiat Amount', readonly=True)
    currency_name = fields.Char(string='Currency', readonly=True)
    partner_email = fields.Char(string='Customer Email', readonly=True)
    nonce = fields.Char(string='Nonce', readonly=True, groups='base.group_system')

    payment_mode = fields.Selection(
        [('hosted_multicoin', 'Hosted Multicoin'), ('single_qr', 'Single QR')],
        string='Payment Mode', readonly=True,
    )
    ticker = fields.Char(string='Ticker', readonly=True)
    expected_coin = fields.Char(string='Expected Coin', readonly=True)
    network = fields.Char(string='Network', readonly=True)
    token_symbol = fields.Char(string='Token Symbol', readonly=True)
    expected_crypto_amount = fields.Float(string='Expected Crypto Amount', digits=(16, 8), readonly=True)
    minimum_amount = fields.Float(string='Minimum Crypto Amount', digits=(16, 8), readonly=True)

    temp_wallet = fields.Char(string='Temporary Wallet / Session', readonly=True)
    ipn_token = fields.Char(string='IPN Token', readonly=True, groups='base.group_system')
    payment_token = fields.Char(string='Hosted Payment Token', readonly=True, groups='base.group_system')
    callback_url = fields.Char(string='Callback URL', readonly=True, groups='base.group_system')
    checkout_url = fields.Char(string='Hosted Checkout URL', readonly=True)
    payment_page_url = fields.Char(string='POS Payment Page URL', readonly=True)
    qr_code = fields.Text(string='QR Code Base64', readonly=True, groups='base.group_system')

    txid_in = fields.Char(string='TXID In', readonly=True)
    txid_out = fields.Char(string='TXID Out', readonly=True)
    paid_amount = fields.Float(string='Paid Crypto Amount', digits=(16, 8), readonly=True)
    paid_coin = fields.Char(string='Paid Coin', readonly=True)
    received_fiat_amount = fields.Float(string='Received Fiat Amount', readonly=True)
    value_forwarded_coin = fields.Float(string='Value Forwarded Coin', digits=(16, 8), readonly=True)
    remote_status = fields.Char(string='Remote Status', readonly=True)
    error_message = fields.Text(string='Error Message', readonly=True)
    provider_payload = fields.Text(string='Last Callback Payload', readonly=True, groups='base.group_system')

    @api.model
    def highriskify_crypto_check_status(self, tx_id):
        if not self.env.user.has_group('point_of_sale.group_pos_user'):
            raise AccessError(_('Only Point of Sale users can check HighRiskify POS Crypto payments.'))
        tx = self.sudo().browse(int(tx_id)).exists()
        if not tx:
            return {'state': 'missing', 'message': _('Payment request was not found.')}
        return tx._highriskify_crypto_status_payload()

    @api.model
    def highriskify_crypto_cancel_payment(self, tx_id):
        if not self.env.user.has_group('point_of_sale.group_pos_user'):
            raise AccessError(_('Only Point of Sale users can cancel HighRiskify POS Crypto payments.'))
        tx = self.sudo().browse(int(tx_id)).exists()
        if not tx:
            return True
        if tx.state in ('draft', 'pending'):
            tx.write({'state': 'cancel', 'error_message': _('Cancelled from POS.')})
        return True

    def _highriskify_crypto_status_payload(self):
        self.ensure_one()
        return {
            'tx_id': self.id,
            'reference': self.name,
            'state': self.state,
            'txid_in': self.txid_in or '',
            'txid_out': self.txid_out or '',
            'paid_amount': self.paid_amount or 0.0,
            'paid_coin': self.paid_coin or '',
            'received_fiat_amount': self.received_fiat_amount or 0.0,
            'message': self.error_message or '',
        }

    def _highriskify_crypto_paid_coin_url_path(self, paid_coin):
        coin = (paid_coin or '').strip().lower().replace('_', '/')
        return coin.strip('/')

    def _highriskify_crypto_price_for_paid_coin(self, paid_coin, currency):
        self.ensure_one()
        coin_path = self._highriskify_crypto_paid_coin_url_path(paid_coin)
        if not coin_path:
            raise ValidationError(_('HighRiskify POS Crypto callback is missing paid coin.'))

        method = self.pos_payment_method_id
        try:
            data = method._highriskify_crypto_get_json_with_fallback(
                f'/crypto/{coin_path}/info.php', timeout=30, purpose='paid coin price lookup'
            )
            prices = data.get('prices') or {}
            for key in (currency, currency.upper(), currency.lower()):
                if key in prices:
                    return float(prices[key])
        except Exception:
            _logger.exception('HighRiskify POS Crypto price lookup failed for %s/%s.', paid_coin, currency)

        if currency.upper() == 'USD' and any(token in coin_path for token in const.USD_LIKE_TOKENS):
            return 1.0
        raise ValidationError(_('HighRiskify POS Crypto price data does not include %(currency)s for %(coin)s.', currency=currency, coin=paid_coin))

    def _highriskify_crypto_received_fiat_value(self, paid_amount, paid_coin, currency):
        self.ensure_one()
        price = self._highriskify_crypto_price_for_paid_coin(paid_coin, currency)
        return float(paid_amount or 0.0) * price

    def _highriskify_crypto_process_notification_data(self, notification_data):
        self.ensure_one()
        self.provider_payload = json.dumps(notification_data, sort_keys=True, default=str)

        received_nonce = notification_data.get('nonce')
        if not received_nonce or received_nonce != self.nonce:
            raise ValidationError(_('HighRiskify POS Crypto callback nonce is invalid.'))

        raw_value = notification_data.get('value_coin') or notification_data.get('amount_paid') or notification_data.get('amount') or 0.0
        try:
            paid_amount = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(_('HighRiskify POS Crypto callback has an invalid value_coin amount.')) from exc

        paid_coin = (notification_data.get('coin') or self.expected_coin or self.ticker or '').strip().lower()
        txid_in = notification_data.get('txid_in') or ''
        txid_out = notification_data.get('txid_out') or notification_data.get('transaction_id') or notification_data.get('txid') or ''
        address_in = notification_data.get('address_in') or ''
        try:
            forwarded_amount = float(notification_data.get('value_forwarded_coin') or 0.0)
        except (TypeError, ValueError):
            forwarded_amount = 0.0

        pending_flag = str(notification_data.get('pending', '0')).lower() in ('1', 'true', 'yes', 'pending')
        currency = self.currency_name or 'USD'
        received_fiat = self._highriskify_crypto_received_fiat_value(paid_amount, paid_coin, currency)
        network, token_symbol = self.pos_payment_method_id._highriskify_crypto_split_ticker(self._highriskify_crypto_paid_coin_url_path(paid_coin))

        vals = {
            'txid_in': txid_in,
            'txid_out': txid_out,
            'paid_amount': paid_amount,
            'paid_coin': paid_coin,
            'value_forwarded_coin': forwarded_amount,
            'received_fiat_amount': received_fiat,
            'remote_status': 'pending' if pending_flag else 'paid',
            'network': network or self.network,
            'token_symbol': token_symbol or self.token_symbol,
        }
        if address_in and not self.temp_wallet:
            vals['temp_wallet'] = address_in

        if self.state == 'done':
            self.write(vals)
            _logger.info('Ignoring duplicate HighRiskify POS Crypto callback for transaction %s.', self.name)
            return

        if pending_flag:
            vals.update({'state': 'pending'})
            self.write(vals)
            self._highriskify_crypto_emit_tracking_event('payment_pending', {
                'amount_paid': paid_amount,
                'amount_paid_usdc': received_fiat if currency.upper() == 'USD' else 0.0,
                'txid_in': txid_in,
                'txid_out': txid_out,
                'value_forwarded_coin': forwarded_amount,
            })
            return

        tolerance = float(self.pos_payment_method_id.highriskify_crypto_underpaid_tolerance or 1.0)
        expected_fiat = self.expected_fiat_amount or self.amount or 0.0
        minimum_accepted = expected_fiat * tolerance
        if self.pos_payment_method_id.highriskify_crypto_customer_pays_blockchain_fees and paid_coin:
            minimum_accepted += self.pos_payment_method_id._highriskify_crypto_estimated_fee_fiat(paid_coin, currency)

        if expected_fiat and float_compare(received_fiat, minimum_accepted, precision_rounding=0.01) < 0:
            message = _(
                'HighRiskify POS Crypto payment received is below the configured tolerance. '
                'Expected minimum: %(minimum).2f %(currency)s. Received: %(received).2f %(currency)s from %(paid)s %(coin)s. TXID: %(txid)s',
                minimum=minimum_accepted,
                received=received_fiat,
                currency=currency,
                paid=paid_amount,
                coin=paid_coin or '-',
                txid=txid_out or txid_in or '-',
            )
            vals.update({'state': 'error', 'error_message': message})
            self.write(vals)
            self._highriskify_crypto_emit_tracking_event('payment_failed_partial', {
                'amount_paid': paid_amount,
                'amount_paid_usdc': received_fiat if currency.upper() == 'USD' else 0.0,
                'expected_amount': expected_fiat,
                'minimum_accepted': minimum_accepted,
                'txid_in': txid_in,
                'txid_out': txid_out,
                'value_forwarded_coin': forwarded_amount,
            })
            return

        vals.update({'state': 'done', 'error_message': False})
        self.write(vals)
        self._highriskify_crypto_emit_tracking_event('payment_confirmed', {
            'amount_paid': paid_amount,
            'amount_paid_usdc': received_fiat if currency.upper() == 'USD' else 0.0,
            'txid_in': txid_in,
            'txid_out': txid_out,
            'value_forwarded_coin': forwarded_amount,
        })

    def _highriskify_crypto_tracking_event_id(self, payload):
        parts = [
            payload.get('merchant_site', ''),
            payload.get('order_id', ''),
            payload.get('event_type', ''),
            payload.get('txid_out', ''),
            payload.get('txid_in', ''),
        ]
        return hashlib.sha1('|'.join(str(part) for part in parts).encode('utf-8')).hexdigest()

    def _highriskify_crypto_tracking_headers(self, payload, method):
        body = json.dumps(payload, separators=(',', ':'), sort_keys=True, default=str)
        timestamp = str(int(time.time()))
        key = method.highriskify_crypto_tracking_key or const.DEFAULT_TRACKING_KEY
        signature = hmac.new(
            key.encode('utf-8'),
            f'{timestamp}.{body}'.encode('utf-8'),
            hashlib.sha256,
        ).hexdigest()
        return body, {
            'Content-Type': 'application/json',
            'X-IPT-Key': key,
            'X-IPT-Signature': signature,
            'X-IPT-Timestamp': timestamp,
            'X-IPT-Version': const.TRACKING_PLUGIN_VERSION,
        }

    def _highriskify_crypto_emit_tracking_event(self, event_type, extra=None):
        self.ensure_one()
        method = self.pos_payment_method_id
        if not method.highriskify_crypto_tracking_enabled:
            return
        endpoint = method.highriskify_crypto_tracking_endpoint or const.DEFAULT_TRACKING_ENDPOINT
        if not endpoint:
            return

        base_url = (self.env['ir.config_parameter'].sudo().get_param('web.base.url') or '').replace('https://', '').replace('http://', '').rstrip('/')
        wallet_payload = method._highriskify_crypto_wallet_payload()
        payload = {
            'ipt_version': const.TRACKING_PLUGIN_VERSION,
            'schema': 2,
            'event_type': event_type,
            'platform': 'custom-crypto',
            'merchant_site': base_url,
            'api_domain': method._highriskify_crypto_api_base(),
            'checkout_domain': method._highriskify_crypto_checkout_domain(),
            'order_id': self.name,
            'pos_order_uid': self.order_uid,
            'pos_order_name': self.order_name,
            'pos_config_id': self.pos_config_id.id if self.pos_config_id else False,
            'pos_config_name': self.pos_config_id.display_name if self.pos_config_id else '',
            'gateway_id': const.TERMINAL_CODE,
            'gateway_name': method.name or const.PAYMENT_METHOD_NAME,
            'payment_method_code': const.TERMINAL_CODE,
            'payment_method_name': method.name or const.PAYMENT_METHOD_NAME,
            'temp_wallet': self.temp_wallet or self.name or '',
            'network': self.network or 'crypto',
            'token_symbol': self.token_symbol or 'MULTICOIN',
            'expected_amount': self.expected_crypto_amount or self.expected_fiat_amount or self.amount or 0.0,
            'order_total_usd': self.expected_fiat_amount if (self.currency_name or '').upper() == 'USD' else self.amount,
            'client_email': self.partner_email or '',
            'merchant_wallet': wallet_payload.get('evm') or wallet_payload.get('btc') or wallet_payload.get('trc20') or '',
            'sub_wallet': '',
            'platform_wallet': '',
            'ticker': self.ticker or const.MULTICOIN_TICKER,
            'payment_mode': self.payment_mode or '',
        }
        if event_type == 'wallet_created':
            payload['created_at'] = fields.Datetime.now()
        elif event_type == 'payment_confirmed':
            payload['confirmed_at'] = fields.Datetime.now()
        elif event_type.startswith('payment_failed'):
            payload['failed_at'] = fields.Datetime.now()
        else:
            payload['occurred_at'] = fields.Datetime.now()
        if extra:
            payload.update(extra)
        payload['event_id'] = self._highriskify_crypto_tracking_event_id(payload)

        try:
            body, headers = self._highriskify_crypto_tracking_headers(payload, method)
            requests.post(endpoint, data=body, headers=headers, timeout=10)
        except Exception:
            _logger.exception('Failed to emit HighRiskify POS Crypto tracking event %s for transaction %s.', event_type, self.name)
