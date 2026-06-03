# -*- coding: utf-8 -*-

import hashlib
import hmac
import json
import logging
import re
import time
from urllib.parse import quote, unquote, urlencode, urlparse

import requests
from werkzeug import urls

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools import html_escape

from .. import const

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    cryptopaymate_temp_wallet = fields.Char(string='HighRiskify Crypto Tracking Key', readonly=True)
    cryptopaymate_payment_token = fields.Text(string='HighRiskify Crypto Hosted Payment Token', readonly=True, groups='base.group_system')
    cryptopaymate_hosted_url = fields.Text(string='HighRiskify Crypto Hosted Checkout URL', readonly=True, groups='base.group_system')
    cryptopaymate_ipn_token = fields.Char(string='HighRiskify Crypto IPN Token', readonly=True, groups='base.group_system')
    cryptopaymate_callback_url = fields.Char(string='HighRiskify Crypto Callback URL', readonly=True)
    cryptopaymate_qr_code = fields.Text(string='HighRiskify Crypto QR Code Base64', readonly=True, groups='base.group_system')
    cryptopaymate_ticker = fields.Char(string='HighRiskify Crypto Ticker', readonly=True)
    cryptopaymate_expected_coin = fields.Char(string='HighRiskify Crypto Expected Coin', readonly=True)
    cryptopaymate_network = fields.Char(string='HighRiskify Crypto Network', readonly=True)
    cryptopaymate_token_symbol = fields.Char(string='HighRiskify Crypto Token Symbol', readonly=True)
    cryptopaymate_expected_amount = fields.Float(string='HighRiskify Crypto Expected Crypto Amount', readonly=True, digits=(16, 8))
    cryptopaymate_minimum_amount = fields.Float(string='HighRiskify Crypto Minimum Crypto Amount', readonly=True, digits=(16, 8))
    cryptopaymate_original_amount = fields.Float(string='HighRiskify Crypto Original Amount', readonly=True)
    cryptopaymate_original_currency = fields.Char(string='HighRiskify Crypto Original Currency', readonly=True)
    cryptopaymate_received_fiat_amount = fields.Float(string='HighRiskify Crypto Received Fiat Value', readonly=True)
    cryptopaymate_nonce = fields.Char(string='HighRiskify Crypto Callback Nonce', readonly=True, groups='base.group_system')
    cryptopaymate_status_nonce = fields.Char(string='HighRiskify Crypto Status Nonce', readonly=True, groups='base.group_system')
    cryptopaymate_txid_in = fields.Char(string='HighRiskify Crypto TXID In', readonly=True)
    cryptopaymate_txid_out = fields.Char(string='HighRiskify Crypto TXID Out', readonly=True)
    cryptopaymate_paid_amount = fields.Float(string='HighRiskify Crypto Paid Crypto Amount', readonly=True, digits=(16, 8))
    cryptopaymate_paid_coin = fields.Char(string='HighRiskify Crypto Paid Coin', readonly=True)
    cryptopaymate_value_forwarded_coin = fields.Float(string='HighRiskify Crypto Forwarded Coin Amount', readonly=True, digits=(16, 8))
    cryptopaymate_provider_payload = fields.Text(string='HighRiskify Crypto Last Callback Payload', readonly=True, groups='base.group_system')
    cryptopaymate_remote_status = fields.Char(string='HighRiskify Crypto Remote Status', readonly=True)

    def _get_specific_rendering_values(self, processing_values):
        rendering_values = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != const.PROVIDER_CODE:
            return rendering_values

        self.ensure_one()
        if not self.cryptopaymate_nonce:
            self.cryptopaymate_nonce = self._cryptopaymate_make_nonce('callback')
        if not self.cryptopaymate_status_nonce:
            self.cryptopaymate_status_nonce = self._cryptopaymate_make_nonce('status')

        if self._cryptopaymate_is_multicoin_hosted_method():
            return self._cryptopaymate_render_multicoin_hosted()
        return self._cryptopaymate_render_individual_qr()

    def _cryptopaymate_is_multicoin_hosted_method(self):
        self.ensure_one()
        method = getattr(self, 'payment_method_id', False)
        return bool(method and getattr(method, 'code', '') == const.MULTICOIN_METHOD_CODE)

    def _cryptopaymate_render_multicoin_hosted(self):
        self.ensure_one()
        provider = self.provider_id
        if not provider._cryptopaymate_wallet_payload():
            raise ValidationError(_('HighRiskify Crypto needs at least one payout wallet address configured.'))

        original_amount = self.amount
        original_currency = self.currency_id.name or 'USD'
        vals = {
            'cryptopaymate_ticker': 'multicoin',
            'cryptopaymate_expected_coin': 'multicoin',
            'cryptopaymate_network': 'crypto',
            'cryptopaymate_token_symbol': 'multicoin',
            'cryptopaymate_expected_amount': 0.0,
            'cryptopaymate_minimum_amount': 0.0,
            'cryptopaymate_original_amount': original_amount,
            'cryptopaymate_original_currency': original_currency,
            'cryptopaymate_temp_wallet': self.reference,
        }

        payment_token_for_redirect = self.cryptopaymate_payment_token or ''
        hosted_url_for_redirect = self.cryptopaymate_hosted_url or ''

        if not payment_token_for_redirect or not hosted_url_for_redirect:
            callback_url = self._cryptopaymate_build_callback_url()
            session_data = self._cryptopaymate_create_multihosted_session(callback_url)
            payment_token_for_redirect = session_data.get('payment_token') or ''
            if not payment_token_for_redirect:
                raise ValidationError(_('HighRiskify Crypto multicoin response did not include payment_token.'))

            vals.update({
                'cryptopaymate_payment_token': payment_token_for_redirect,
                'cryptopaymate_ipn_token': session_data.get('ipn_token') or '',
                'cryptopaymate_callback_url': session_data.get('callback_url') or callback_url,
            })
            hosted_url_for_redirect = self._cryptopaymate_build_hosted_checkout_url(payment_token_for_redirect)
            vals['cryptopaymate_hosted_url'] = hosted_url_for_redirect
            self.write(vals)
            self._cryptopaymate_emit_tracking_event('wallet_created')
            self._cryptopaymate_mark_order_payment_started('Multicoin hosted checkout started')
        else:
            self.write(vals)

        redirect_params = self._cryptopaymate_hosted_checkout_params(payment_token_for_redirect)
        return {
            'api_url': '/payment/cryptopaymate_crypto/redirect',
            'reference': self.reference,
            'status_nonce': self.cryptopaymate_status_nonce,
            'payment_token': payment_token_for_redirect,
            'hosted_url': hosted_url_for_redirect,
            'add_fees': redirect_params.get('add_fees'),
            'logo': redirect_params.get('logo'),
            'background': redirect_params.get('background'),
            'theme': redirect_params.get('theme'),
            'button': redirect_params.get('button'),
        }

    def _cryptopaymate_render_individual_qr(self):
        self.ensure_one()
        provider = self.provider_id
        ticker = self._cryptopaymate_get_selected_ticker()
        merchant_wallet = provider._cryptopaymate_wallet_for_ticker(ticker)
        if not merchant_wallet:
            raise ValidationError(_('Please add a compatible payout wallet for %(ticker)s in HighRiskify Crypto settings.', ticker=ticker))

        expected_coin = self._cryptopaymate_expected_coin(ticker)
        network, token_symbol = self._cryptopaymate_split_ticker(ticker)
        original_amount = self.amount
        original_currency = self.currency_id.name or 'USD'
        expected_amount = self._cryptopaymate_convert_amount(original_amount, original_currency, ticker)
        minimum_amount = self._cryptopaymate_get_minimum(ticker)

        if minimum_amount and float_compare(expected_amount, minimum_amount, precision_rounding=0.00000001) < 0:
            raise ValidationError(_(
                'HighRiskify Crypto amount is below the minimum for %(ticker)s. Required minimum: %(minimum)s. Converted amount: %(amount)s.',
                ticker=ticker, minimum=minimum_amount, amount=expected_amount,
            ))

        vals = {
            'cryptopaymate_ticker': ticker,
            'cryptopaymate_expected_coin': expected_coin,
            'cryptopaymate_network': network,
            'cryptopaymate_token_symbol': token_symbol,
            'cryptopaymate_expected_amount': expected_amount,
            'cryptopaymate_minimum_amount': minimum_amount or 0.0,
            'cryptopaymate_original_amount': original_amount,
            'cryptopaymate_original_currency': original_currency,
            'cryptopaymate_payment_token': False,
            'cryptopaymate_hosted_url': False,
        }

        if not self.cryptopaymate_temp_wallet or self.cryptopaymate_ticker != ticker:
            callback_url = self._cryptopaymate_build_callback_url()
            wallet_data = self._cryptopaymate_create_wallet(callback_url, ticker, merchant_wallet)
            temp_wallet = wallet_data.get('address_in')
            if not temp_wallet:
                raise ValidationError(_('HighRiskify Crypto wallet response did not include address_in.'))
            qr_code = self._cryptopaymate_generate_qr(ticker, temp_wallet, expected_amount)
            vals.update({
                'cryptopaymate_temp_wallet': temp_wallet,
                'cryptopaymate_ipn_token': wallet_data.get('ipn_token') or '',
                'cryptopaymate_callback_url': wallet_data.get('callback_url') or callback_url,
                'cryptopaymate_qr_code': qr_code,
            })
            self.write(vals)
            self._cryptopaymate_emit_tracking_event('wallet_created')
            self._cryptopaymate_mark_order_payment_started('Multicoin hosted checkout started')
        else:
            self.write(vals)

        return {
            'api_url': self._cryptopaymate_build_payment_page_url(),
            'reference': self.reference,
        }

    def _cryptopaymate_find_transaction_from_data(self, notification_data):
        reference = notification_data.get('reference') or notification_data.get('order_id')
        if not reference:
            raise ValidationError(_('HighRiskify Crypto callback is missing the transaction reference/order_id.'))

        tx = self.search([('reference', '=', reference), ('provider_code', '=', const.PROVIDER_CODE)], limit=1)
        if not tx:
            raise ValidationError(_('No HighRiskify Crypto transaction found matching reference %s.') % reference)
        return tx

    def _cryptopaymate_set_pending(self, message):
        try:
            return self._set_pending(state_message=message)
        except TypeError:
            return self._set_pending(message)

    def _cryptopaymate_set_done(self, message):
        try:
            return self._set_done(state_message=message)
        except TypeError:
            return self._set_done(message)

    def _cryptopaymate_set_error(self, message):
        try:
            return self._set_error(state_message=message)
        except TypeError:
            return self._set_error(message)

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        if provider_code != const.PROVIDER_CODE:
            return super()._get_tx_from_notification_data(provider_code, notification_data)
        return self._cryptopaymate_find_transaction_from_data(notification_data)

    @api.model
    def _search_by_reference(self, provider_code, payment_data):
        if provider_code != const.PROVIDER_CODE:
            return super()._search_by_reference(provider_code, payment_data)
        return self._cryptopaymate_find_transaction_from_data(payment_data)

    def _apply_updates(self, payment_data):
        if self.provider_code != const.PROVIDER_CODE:
            return super()._apply_updates(payment_data)
        return self._process_notification_data(payment_data)

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != const.PROVIDER_CODE:
            return

        self.ensure_one()
        self.cryptopaymate_provider_payload = json.dumps(notification_data, sort_keys=True, default=str)

        received_nonce = notification_data.get('nonce')
        if not received_nonce or received_nonce != self.cryptopaymate_nonce:
            raise ValidationError(_('HighRiskify Crypto callback nonce is invalid.'))

        raw_value = notification_data.get('value_coin') or notification_data.get('amount_paid') or notification_data.get('amount') or 0.0
        try:
            paid_amount = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(_('HighRiskify Crypto callback has an invalid value_coin amount.')) from exc

        paid_coin = (notification_data.get('coin') or '').strip().lower()
        txid_in = notification_data.get('txid_in') or ''
        txid_out = notification_data.get('txid_out') or notification_data.get('transaction_id') or notification_data.get('txid') or ''
        try:
            forwarded_amount = float(notification_data.get('value_forwarded_coin') or 0.0)
        except (TypeError, ValueError):
            forwarded_amount = 0.0

        pending_flag = str(notification_data.get('pending', '0')).lower() in ('1', 'true', 'yes', 'pending')
        currency = self.cryptopaymate_original_currency or self.currency_id.name or 'USD'
        received_fiat = self._cryptopaymate_received_fiat_value(paid_amount, paid_coin, currency)

        self.write({
            'provider_reference': txid_out or txid_in or f'cryptopaymate-{self.reference}',
            'cryptopaymate_txid_in': txid_in,
            'cryptopaymate_txid_out': txid_out,
            'cryptopaymate_paid_amount': paid_amount,
            'cryptopaymate_paid_coin': paid_coin,
            'cryptopaymate_value_forwarded_coin': forwarded_amount,
            'cryptopaymate_received_fiat_amount': received_fiat,
            'cryptopaymate_remote_status': 'pending' if pending_flag else 'paid',
            'cryptopaymate_network': self._cryptopaymate_paid_coin_url_path(paid_coin).split('/')[0] if paid_coin else 'crypto',
            'cryptopaymate_token_symbol': paid_coin.upper() if paid_coin else 'multicoin',
        })
        self._cryptopaymate_log_sale_order(
            'Crypto callback received',
            {
                'Remote status': 'pending/unconfirmed' if pending_flag else 'paid/confirmed',
                'Paid coin': paid_coin or '-',
                'Paid amount': paid_amount,
                'Received fiat value': f'{received_fiat:.2f} {currency}',
                'TXID In': txid_in or '-',
                'TXID Out': txid_out or '-',
            }
        )

        if self.state == 'done':
            _logger.info('Ignoring duplicate HighRiskify Crypto callback for transaction %s.', self.reference)
            return

        if pending_flag:
            if self.state not in ('pending', 'done'):
                self._cryptopaymate_set_pending(_('HighRiskify Crypto pending/unconfirmed callback received. Waiting for confirmed callback.'))
            self._cryptopaymate_emit_tracking_event('payment_pending', {
                'amount_paid': paid_amount,
                'amount_paid_usdc': received_fiat if currency == 'USD' else 0.0,
                'txid_in': txid_in,
                'txid_out': txid_out,
            })
            self._cryptopaymate_log_sale_order('Crypto payment is pending/unconfirmed', {'TXID In': txid_in or '-', 'Coin': paid_coin or '-', 'Amount': paid_amount})
            return

        tolerance = float(self.provider_id.cryptopaymate_underpaid_tolerance or 1.0)
        expected_fiat = self.cryptopaymate_original_amount or self.amount or 0.0
        minimum_accepted = expected_fiat * tolerance
        if self.provider_id.cryptopaymate_customer_pays_blockchain_fees and paid_coin:
            minimum_accepted += self._cryptopaymate_estimated_fee_fiat(paid_coin, currency)

        if expected_fiat and float_compare(received_fiat, minimum_accepted, precision_rounding=0.01) < 0:
            message = _(
                'HighRiskify Crypto payment received is below the configured tolerance. '
                'Expected minimum: %(minimum).2f %(currency)s. Received: %(received).2f %(currency)s from %(paid)s %(coin)s. TXID: %(txid)s',
                minimum=minimum_accepted,
                received=received_fiat,
                currency=currency,
                paid=paid_amount,
                coin=paid_coin or '-',
                txid=txid_out or txid_in or '-',
            )
            self._cryptopaymate_set_error(message)
            self._cryptopaymate_emit_tracking_event('payment_failed_partial', {
                'amount_paid': paid_amount,
                'amount_paid_usdc': received_fiat if currency == 'USD' else 0.0,
                'expected_amount': expected_fiat,
                'minimum_accepted': minimum_accepted,
                'txid_in': txid_in,
                'txid_out': txid_out,
            })
            return

        self._cryptopaymate_set_done(_('HighRiskify Crypto multicoin payment confirmed. TXID Out: %s') % (txid_out or '-'))
        self._cryptopaymate_confirm_sale_orders_after_payment()
        self._cryptopaymate_log_sale_order('Crypto payment confirmed and Odoo transaction marked Done', {'TXID In': txid_in or '-', 'TXID Out': txid_out or '-', 'Coin': paid_coin or '-', 'Amount': paid_amount})
        self._cryptopaymate_emit_tracking_event('payment_confirmed', {
            'amount_paid': paid_amount,
            'amount_paid_usdc': received_fiat if currency == 'USD' else 0.0,
            'txid_in': txid_in,
            'txid_out': txid_out,
            'value_forwarded_coin': forwarded_amount,
        })


    def _cryptopaymate_get_sale_orders(self):
        """Return sale orders linked to this transaction, across Odoo variants."""
        self.ensure_one()
        SaleOrder = self.env['sale.order'].sudo()
        orders = SaleOrder.browse()
        if 'sale_order_ids' in self._fields:
            orders |= self.sudo().sale_order_ids
        if 'sale_order_id' in self._fields and self.sudo().sale_order_id:
            orders |= self.sudo().sale_order_id
        try:
            if 'transaction_ids' in SaleOrder._fields:
                orders |= SaleOrder.search([('transaction_ids', 'in', self.id)])
        except Exception:
            _logger.debug('HighRiskify Crypto could not search sale.order transaction_ids for %s', self.reference, exc_info=True)
        try:
            if self.reference:
                orders |= SaleOrder.search(['|', ('name', '=', self.reference), ('client_order_ref', '=', self.reference)])
        except Exception:
            _logger.debug('HighRiskify Crypto could not search sale.order by reference for %s', self.reference, exc_info=True)
        return orders

    def _cryptopaymate_log_sale_order(self, title, details=None):
        self.ensure_one()
        orders = self._cryptopaymate_get_sale_orders()
        if not orders:
            _logger.info('HighRiskify Crypto order note skipped because no sale order was linked to transaction %s. %s %s', self.reference, title, details or {})
            return
        lines = [f'<b>{html_escape(title)}</b>', f'Reference: {html_escape(self.reference or "-")}', f'Transaction state: {html_escape(self.state or "-")}']
        for key, value in (details or {}).items():
            lines.append(f'{html_escape(str(key))}: {html_escape(str(value))}')
        body = '<br/>'.join(lines)
        for order in orders:
            try:
                order.message_post(body=body)
            except Exception:
                _logger.debug('HighRiskify Crypto could not post message on sale order %s', order.id, exc_info=True)

    def _cryptopaymate_mark_order_payment_started(self, title):
        """Keep unpaid crypto attempts visible without confirming the sale order.

        Important business rule for this gateway:
        - Opening the hosted checkout or QR page is only an attempted/unpaid payment.
        - The sale order must remain a quotation / unpaid order until HighRiskify Crypto sends a confirmed callback.
        - We still store transaction fields and add sale-order chatter notes so admins can see what happened.
        """
        self.ensure_one()
        details = {
            'Payment stage': 'Unpaid / waiting for crypto payment',
            'Payment method': self.payment_method_id.name if self.payment_method_id else const.GATEWAY_DISPLAY_NAME,
            'Ticker': self.cryptopaymate_ticker or 'multicoin',
            'Expected amount': self.cryptopaymate_expected_amount or self.cryptopaymate_original_amount or self.amount,
            'Wallet / session': self.cryptopaymate_temp_wallet or self.reference or '-',
            'Callback URL': self.cryptopaymate_callback_url or '-',
        }
        try:
            if self.state not in ('pending', 'done'):
                self._cryptopaymate_set_pending(_('Crypto payment session started. Waiting for confirmed HighRiskify Crypto callback.'))
        except Exception:
            _logger.debug('HighRiskify Crypto could not set transaction %s to pending on payment start.', self.reference, exc_info=True)
        self._cryptopaymate_log_sale_order(title, details)

    def _cryptopaymate_confirm_sale_orders_after_payment(self):
        """Confirm linked website sale orders only after confirmed crypto payment."""
        self.ensure_one()
        orders = self._cryptopaymate_get_sale_orders()
        for order in orders:
            try:
                if order.state in ('draft', 'sent'):
                    order.action_confirm()
                    order.message_post(body='<b>Crypto payment confirmed</b><br/>Order confirmed after HighRiskify Crypto callback validation.')
            except Exception:
                _logger.exception('HighRiskify Crypto could not confirm paid sale order %s for transaction %s.', order.id, self.reference)

    def _cryptopaymate_make_nonce(self, label):
        self.ensure_one()
        raw = f'{label}|{self.reference}|{time.time()}|{self.id}'.encode('utf-8')
        return hashlib.sha256(raw).hexdigest()


    def _cryptopaymate_get_selected_ticker(self):
        self.ensure_one()
        method = getattr(self, 'payment_method_id', False)
        code = ''
        if method and getattr(method, 'code', False):
            code = method.code
        ticker = const.PAYMENT_METHOD_TICKER_MAP.get(code)
        if ticker and ticker != 'multicoin':
            return ticker.strip().strip('/')
        return self.provider_id._cryptopaymate_get_ticker()

    def _cryptopaymate_split_ticker(self, ticker):
        ticker = (ticker or '').strip().lower()
        if '/' in ticker:
            network, token = ticker.split('/', 1)
            return network, token.upper()
        return ticker, ticker.upper()

    def _cryptopaymate_expected_coin(self, ticker):
        return (ticker or '').strip().lower().replace('/', '_')

    def _cryptopaymate_convert_amount(self, amount, currency, ticker):
        self.ensure_one()
        data = self._cryptopaymate_get_json_with_fallback(
            f'/crypto/{ticker}/convert.php',
            params={'value': self._cryptopaymate_format_amount(amount), 'from': (currency or 'USD').lower()},
            timeout=30,
            purpose='currency conversion',
        )
        if 'value_coin' not in data:
            raise ValidationError(_('HighRiskify Crypto does not support the current checkout currency/ticker combination.'))
        try:
            return float(data['value_coin'])
        except (TypeError, ValueError) as exc:
            raise ValidationError(_('HighRiskify Crypto returned an invalid conversion amount.')) from exc

    def _cryptopaymate_get_minimum(self, ticker):
        self.ensure_one()
        try:
            data = self._cryptopaymate_get_json_with_fallback(
                f'/crypto/{ticker}/info.php', timeout=15, purpose='minimum lookup'
            )
            if data.get('minimum') is not None:
                return float(data['minimum'])
        except Exception:
            _logger.info('HighRiskify Crypto minimum lookup via API failed for %s; using local fallback if available.', ticker)
        return float(const.TICKER_MINIMUMS.get(ticker, 0.0) or 0.0)

    def _cryptopaymate_create_wallet(self, callback_url, ticker, merchant_wallet):
        self.ensure_one()
        provider = self.provider_id
        params = {
            'address': merchant_wallet,
            'callback': callback_url,
            'confirmations': max(int(provider.cryptopaymate_confirmations or 1), 1),
        }
        if provider.cryptopaymate_request_pending_callbacks:
            params['pending'] = 1
        return self._cryptopaymate_get_json_with_fallback(
            f'/crypto/{ticker}/wallet.php', params=params, timeout=30, purpose='wallet creation'
        )

    def _cryptopaymate_generate_qr(self, ticker, address_in, amount):
        self.ensure_one()
        data = self._cryptopaymate_get_json_with_fallback(
            f'/crypto/{ticker}/qrcode.php',
            params={'address': address_in, 'amount': self._cryptopaymate_format_amount(amount)},
            timeout=30,
            purpose='QR code generation',
        )
        qr_code = data.get('qr_code')
        if not qr_code:
            raise ValidationError(_('HighRiskify Crypto QR response did not include qr_code.'))
        return qr_code

    def _cryptopaymate_format_amount(self, amount):
        try:
            value = float(amount)
        except (TypeError, ValueError):
            return str(amount or '0')
        if value.is_integer():
            return str(int(value))
        return ('%.8f' % value).rstrip('0').rstrip('.')

    def _cryptopaymate_json_from_response(self, response):
        try:
            return response.json()
        except Exception as exc:
            body = (response.text or '')[:400]
            raise ValidationError(_('HighRiskify Crypto returned invalid JSON. Response: %s') % body) from exc

    def _cryptopaymate_get_json_with_fallback(self, path, params=None, timeout=30, purpose='request'):
        last_error = None
        for api_url in self._cryptopaymate_api_urls(path):
            try:
                response = requests.get(api_url, params=params or {}, timeout=timeout)
                response.raise_for_status()
                return self._cryptopaymate_json_from_response(response)
            except ValidationError:
                raise
            except Exception as exc:
                last_error = exc
                _logger.warning('HighRiskify Crypto %s failed via %s: %s', purpose, api_url, exc)
        raise ValidationError(_('HighRiskify Crypto %(purpose)s failed. Last error: %(error)s', purpose=purpose, error=str(last_error or 'unknown error')))

    def _cryptopaymate_post_json_with_fallback(self, path, payload=None, timeout=30, purpose='request'):
        last_error = None
        for api_url in self._cryptopaymate_api_urls(path):
            try:
                response = requests.post(
                    api_url,
                    json=payload or {},
                    headers={'Content-Type': 'application/json'},
                    timeout=timeout,
                )
                response.raise_for_status()
                return self._cryptopaymate_json_from_response(response)
            except ValidationError:
                raise
            except Exception as exc:
                last_error = exc
                _logger.warning('HighRiskify Crypto %s failed via %s: %s', purpose, api_url, exc)
        raise ValidationError(_('HighRiskify Crypto %(purpose)s failed. Please check API base URL, payout wallet settings, and server firewall. Last error: %(error)s', purpose=purpose, error=str(last_error or 'unknown error')))

    def _cryptopaymate_api_urls(self, path):
        self.ensure_one()
        return [f"{base}/{path.lstrip('/')}" for base in self.provider_id._cryptopaymate_api_bases()]

    def _cryptopaymate_create_multihosted_session(self, callback_url):
        self.ensure_one()
        provider = self.provider_id
        checkout_domain = provider._cryptopaymate_checkout_domain()
        payload = {
            'fiat_amount': self._cryptopaymate_format_amount(self.amount),
            'fiat_currency': self.currency_id.name or 'USD',
            'callback': callback_url,
            # Send the configured hosted checkout domain to the API too. The API may
            # ignore some aliases, but including them keeps the Odoo flow aligned with
            # hosted/multicoin implementations that bind tokens to a checkout domain.
            'domain': checkout_domain,
            'checkout_domain': checkout_domain,
            'hosted_domain': checkout_domain,
            'redirect_domain': checkout_domain,
        }
        payload.update(provider._cryptopaymate_wallet_payload())
        return self._cryptopaymate_post_json_with_fallback(
            '/crypto/multi-hosted-wallet.php',
            payload=payload,
            timeout=30,
            purpose='multicoin hosted checkout creation',
        )

    def _cryptopaymate_build_callback_url(self):
        self.ensure_one()
        base_url = self.provider_id.get_base_url()
        callback_url = urls.url_join(base_url, '/payment/cryptopaymate_crypto/callback')
        query = urlencode({'order_id': self.reference, 'nonce': self.cryptopaymate_nonce})
        return f'{callback_url}?{query}'

    def _cryptopaymate_hosted_checkout_base_url(self):
        self.ensure_one()
        provider = self.provider_id
        domain = provider._cryptopaymate_checkout_domain()

        # Final safety guard: never allow the Odoo website/base URL to become the hosted
        # checkout domain. This was the bug that produced
        # https://community.highriskify.com/crypto/hosted.php?... instead of the backend
        # configured checkout domain.
        try:
            odoo_host = (urlparse(provider.get_base_url()).netloc or '').lower()
        except Exception:
            odoo_host = ''
        clean_domain = (domain or '').strip().lower().split('/')[0]
        if not clean_domain or clean_domain == odoo_host:
            clean_domain = const.HOSTED_CHECKOUT_DOMAIN
        return f'https://{clean_domain}/crypto/hosted.php'

    def _cryptopaymate_hosted_checkout_params(self, payment_token):
        self.ensure_one()
        provider = self.provider_id
        params = {
            'payment_token': payment_token or '',
            'add_fees': '1' if provider.cryptopaymate_customer_pays_blockchain_fees else '0',
        }
        optional_map = {
            'logo': provider.cryptopaymate_hosted_logo_url,
            'background': provider.cryptopaymate_background_color,
            'theme': provider.cryptopaymate_theme_color,
            'button': provider.cryptopaymate_button_color,
        }
        for key, value in optional_map.items():
            value = (value or '').strip()
            if value:
                params[key] = value
        return params

    def _cryptopaymate_build_hosted_checkout_url(self, payment_token):
        self.ensure_one()
        params = self._cryptopaymate_hosted_checkout_params(payment_token)
        token = params.pop('payment_token', '')
        token_for_url = self._cryptopaymate_payment_token_for_url(token)
        query = f'payment_token={token_for_url}'
        if params:
            query += '&' + urlencode(params)
        base_url = self._cryptopaymate_hosted_checkout_base_url()
        return f'{base_url}?{query}'

    def _cryptopaymate_payment_token_for_url(self, payment_token):
        token = str(payment_token or '').strip()
        # The multicoin API/WooCommerce flow returns a token that is usually already URL-safe
        # encoded (%2B, %2F, %3D). Preserve it exactly. Encoding it again creates %252B and
        # hosted.php rejects the token. If a raw token is ever returned, encode it once.
        if re.search(r'%[0-9A-Fa-f]{2}', token):
            return token.replace(' ', '%20')
        return quote(token, safe='')

    def _cryptopaymate_build_payment_page_url(self):
        self.ensure_one()
        base_url = self.provider_id.get_base_url()
        return urls.url_join(base_url, f'/payment/cryptopaymate_crypto/pay/{self.id}/{self.cryptopaymate_status_nonce}')

    def _cryptopaymate_paid_coin_url_path(self, paid_coin):
        coin = (paid_coin or '').strip().lower().replace('_', '/')
        return coin.strip('/')

    def _cryptopaymate_price_for_paid_coin(self, paid_coin, currency):
        coin_path = self._cryptopaymate_paid_coin_url_path(paid_coin)
        if not coin_path:
            raise ValidationError(_('HighRiskify Crypto callback is missing paid coin.'))
        data = self._cryptopaymate_get_json_with_fallback(
            f'/crypto/{coin_path}/info.php',
            timeout=30,
            purpose='paid coin price lookup',
        )
        prices = data.get('prices') or {}
        for key in (currency, currency.upper(), currency.lower()):
            if key in prices:
                return float(prices[key])

        # Safe fallback for USD-like stablecoin payments if API price lookup lacks the currency key.
        if currency.upper() == 'USD' and any(token in coin_path for token in ('usdt', 'usdc', 'dai', 'usd1', 'pyusd', 'tusd', 'usdd')):
            return 1.0
        raise ValidationError(_('HighRiskify Crypto price data does not include %(currency)s for %(coin)s.', currency=currency, coin=paid_coin))

    def _cryptopaymate_received_fiat_value(self, paid_amount, paid_coin, currency):
        price = self._cryptopaymate_price_for_paid_coin(paid_coin, currency)
        return float(paid_amount or 0.0) * price

    def _cryptopaymate_estimated_fee_fiat(self, paid_coin, currency):
        coin_path = self._cryptopaymate_paid_coin_url_path(paid_coin)
        if not coin_path:
            return 0.0
        try:
            data = self._cryptopaymate_get_json_with_fallback(
                f'/crypto/{coin_path}/fees.php',
                timeout=20,
                purpose='paid coin fee lookup',
            )
            fees = data.get('estimated_cost_currency') or {}
            for key in (currency, currency.upper(), currency.lower()):
                if key in fees:
                    return float(fees[key])
        except Exception:
            _logger.exception('HighRiskify Crypto fee lookup failed for %s/%s; continuing without extra fee validation.', paid_coin, currency)
        return 0.0

    def _cryptopaymate_remote_status(self):
        self.ensure_one()
        if self.cryptopaymate_ipn_token and self.cryptopaymate_ticker and self.cryptopaymate_ticker != 'multicoin':
            return self._cryptopaymate_get_json_with_fallback(
                '/crypto/payment-status.php',
                params={'ipn_token': self.cryptopaymate_ipn_token, 'ticker': self.cryptopaymate_ticker},
                timeout=20, purpose='payment status lookup'
            )
        return {'status': self.cryptopaymate_remote_status or self.state}

    def _cryptopaymate_tracking_event_id(self, payload):
        parts = [
            payload.get('merchant_site', ''),
            payload.get('order_id', ''),
            payload.get('event_type', ''),
            payload.get('txid_out', ''),
            payload.get('txid_in', ''),
        ]
        return hashlib.sha1('|'.join(str(part) for part in parts).encode('utf-8')).hexdigest()

    def _cryptopaymate_tracking_headers(self, payload, provider):
        body = json.dumps(payload, separators=(',', ':'), sort_keys=True, default=str)
        timestamp = str(int(time.time()))
        key = const.DEFAULT_TRACKING_KEY
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

    def _cryptopaymate_emit_tracking_event(self, event_type, extra=None):
        self.ensure_one()
        provider = self.provider_id
        endpoint = const.DEFAULT_TRACKING_ENDPOINT
        if not endpoint:
            return

        payload = {
            'ipt_version': const.TRACKING_PLUGIN_VERSION,
            'schema': 2,
            'event_type': event_type,
            'platform': 'custom-crypto',
            'merchant_site': self.provider_id.get_base_url().replace('https://', '').replace('http://', '').rstrip('/'),
            'api_domain': provider._cryptopaymate_api_base(),
            'checkout_domain': provider._cryptopaymate_checkout_domain(),
            'order_id': self.reference,
            'client_email': self.partner_email or self.partner_id.email or '',
            'temp_wallet': self.reference or '',
            'network': self.cryptopaymate_network or 'crypto',
            'token_symbol': self.cryptopaymate_token_symbol or 'multicoin',
            'expected_amount': self.cryptopaymate_original_amount or self.amount or 0.0,
            'order_total_usd': self.cryptopaymate_original_amount if self.cryptopaymate_original_currency == 'USD' else self.amount,
            'gateway_name': const.GATEWAY_DISPLAY_NAME,
            'merchant_wallet': provider.cryptopaymate_wallet_evm or provider.cryptopaymate_wallet_btc or '',
            'sub_wallet': '',
            'platform_wallet': '',
            'ticker': self.cryptopaymate_ticker or 'multicoin',
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
        payload['event_id'] = self._cryptopaymate_tracking_event_id(payload)

        try:
            body, headers = self._cryptopaymate_tracking_headers(payload, provider)
            requests.post(endpoint, data=body, headers=headers, timeout=10)
        except Exception:
            _logger.exception('Failed to emit HighRiskify Crypto tracking event %s for transaction %s.', event_type, self.reference)
