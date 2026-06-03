# -*- coding: utf-8 -*-

import hashlib
import hmac
import json
import logging
import secrets
import time
from urllib.parse import quote, unquote, urlencode

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

    highriskify_tracking_address = fields.Char(string='HighRiskify Tracking Address', readonly=True)
    highriskify_polygon_wallet = fields.Char(string='HighRiskify Temporary Polygon Wallet', readonly=True)
    highriskify_callback_url = fields.Char(string='HighRiskify Callback URL', readonly=True)
    highriskify_expected_amount = fields.Float(string='HighRiskify Expected USD Amount', readonly=True)
    highriskify_original_amount = fields.Float(string='HighRiskify Original Amount', readonly=True)
    highriskify_original_currency = fields.Char(string='HighRiskify Original Currency', readonly=True)
    highriskify_nonce = fields.Char(string='HighRiskify Callback Nonce', readonly=True, groups='base.group_system')
    highriskify_txid_out = fields.Char(string='HighRiskify TXID Out', readonly=True)
    highriskify_paid_amount = fields.Float(string='HighRiskify Paid USD Amount', readonly=True)
    highriskify_paid_coin = fields.Char(string='HighRiskify Paid Coin', readonly=True)
    highriskify_provider_payload = fields.Text(string='HighRiskify Last Callback Payload', readonly=True, groups='base.group_system')

    def _get_specific_rendering_values(self, processing_values):
        """Prepare hosted checkout redirect values for HighRiskify."""
        rendering_values = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != const.PROVIDER_CODE:
            return rendering_values

        self.ensure_one()
        provider = self.provider_id
        if not provider.highriskify_wallet_address:
            raise ValidationError(_('HighRiskify payout wallet address is missing on the payment provider.'))

        original_currency = self.currency_id.name
        original_amount = self.amount
        self._highriskify_emit_tracking_event('checkout_started')
        expected_usd_amount = original_amount if original_currency == 'USD' else self._highriskify_convert_to_usd(original_amount, original_currency)

        if not self.highriskify_nonce:
            self.highriskify_nonce = secrets.token_urlsafe(24)

        if not self.highriskify_tracking_address:
            callback_url = self._highriskify_build_callback_url()
            wallet_data = self._highriskify_create_wallet(callback_url)
            self.write({
                'highriskify_tracking_address': wallet_data.get('address_in'),
                'highriskify_polygon_wallet': wallet_data.get('polygon_address_in'),
                'highriskify_callback_url': wallet_data.get('callback_url') or callback_url,
                'highriskify_expected_amount': expected_usd_amount,
                'highriskify_original_amount': original_amount,
                'highriskify_original_currency': original_currency,
            })
            self._highriskify_emit_tracking_event('wallet_created')
            self._highriskify_mark_order_payment_started('HighRiskify onramp checkout started')
        else:
            self.write({
                'highriskify_expected_amount': expected_usd_amount,
                'highriskify_original_amount': original_amount,
                'highriskify_original_currency': original_currency,
            })

        # Do not send the browser directly to checkout.highriskify.com from the
        # Odoo payment form. The hosted checkout can misbehave when opened with
        # the Odoo referrer. Instead, go through a tiny Odoo bridge page which
        # sends Referrer-Policy: no-referrer and then moves to the exact Woo-style
        # pay.php URL.
        return {
            'api_url': self._highriskify_build_bridge_url(),
            'reference': self.reference,
        }

    def _highriskify_set_pending(self, message):
        """Set pending state using a signature compatible with Odoo 17/18/19."""
        try:
            return self._set_pending(state_message=message)
        except TypeError:
            return self._set_pending(message)

    def _highriskify_set_done(self, message):
        """Set done state using a signature compatible with Odoo 17/18/19."""
        try:
            return self._set_done(state_message=message)
        except TypeError:
            return self._set_done(message)

    def _highriskify_set_error(self, message):
        """Set error state using a signature compatible with Odoo 17/18/19."""
        try:
            return self._set_error(state_message=message)
        except TypeError:
            return self._set_error(message)

    @api.model
    def _highriskify_get_reference_from_notification_data(self, notification_data):
        """Return the Odoo transaction reference from HighRiskify callback data."""
        reference = notification_data.get('reference') or notification_data.get('order_id')
        if not reference:
            raise ValidationError(_('HighRiskify callback is missing the transaction reference.'))
        return reference

    @api.model
    def _highriskify_find_transaction_from_notification_data(self, notification_data):
        """Find the HighRiskify payment transaction from callback data."""
        reference = self._highriskify_get_reference_from_notification_data(notification_data)
        tx = self.search([('reference', '=', reference), ('provider_code', '=', const.PROVIDER_CODE)], limit=1)
        if not tx:
            raise ValidationError(_('No HighRiskify transaction found matching reference %s.') % reference)
        return tx

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Odoo 17/18 notification lookup hook."""
        if provider_code != const.PROVIDER_CODE:
            return super()._get_tx_from_notification_data(provider_code, notification_data)
        return self._highriskify_find_transaction_from_notification_data(notification_data)

    @api.model
    def _search_by_reference(self, provider_code, payment_data):
        """Odoo 19 notification lookup hook."""
        if provider_code != const.PROVIDER_CODE:
            return super()._search_by_reference(provider_code, payment_data)
        return self._highriskify_find_transaction_from_notification_data(payment_data)

    def _process_notification_data(self, notification_data):
        """Odoo 17/18 notification processing hook."""
        super()._process_notification_data(notification_data)
        if self.provider_code != const.PROVIDER_CODE:
            return
        return self._highriskify_process_notification_payload(notification_data)

    def _apply_updates(self, payment_data):
        """Odoo 19 notification processing hook."""
        if self.provider_code != const.PROVIDER_CODE:
            return super()._apply_updates(payment_data)
        return self._highriskify_process_notification_payload(payment_data)

    def _highriskify_process_notification_payload(self, notification_data):
        """Validate and apply HighRiskify callback/IPN data to the transaction."""
        self.ensure_one()
        self.highriskify_provider_payload = json.dumps(notification_data, sort_keys=True, default=str)

        received_nonce = notification_data.get('nonce')
        if not received_nonce or received_nonce != self.highriskify_nonce:
            raise ValidationError(_('HighRiskify callback nonce is invalid.'))

        txid_in = notification_data.get('txid_in') or notification_data.get('hash_in') or ''
        txid_out = notification_data.get('txid_out') or notification_data.get('transaction_id') or notification_data.get('txid') or ''
        raw_value = notification_data.get('value_coin') or notification_data.get('amount_paid') or notification_data.get('amount') or 0.0
        paid_coin = notification_data.get('coin') or notification_data.get('token_symbol') or 'USDC'
        pending_raw = notification_data.get('pending') or notification_data.get('is_pending') or notification_data.get('status') or ''
        pending_flag = str(pending_raw).strip().lower() in ('1', 'true', 'yes', 'pending', 'unconfirmed', 'processing')

        try:
            paid_amount = float(raw_value or 0.0)
        except (TypeError, ValueError):
            raise ValidationError(_('HighRiskify callback has an invalid paid amount.'))

        paid_amount_usd = self._highriskify_paid_amount_to_usd(paid_amount, paid_coin)
        tolerance = float(self.provider_id.highriskify_tolerance_ratio or 0)
        expected = self.highriskify_expected_amount or self.amount
        threshold = expected * tolerance

        self.write({
            'provider_reference': txid_out or txid_in or f'highriskify-{self.reference}',
            'highriskify_txid_out': txid_out,
            'highriskify_paid_amount': paid_amount_usd,
            'highriskify_paid_coin': paid_coin,
        })

        if self.state == 'done':
            _logger.info('Ignoring duplicate HighRiskify callback for transaction %s.', self.reference)
            self._highriskify_log_sale_order('Duplicate HighRiskify callback ignored', {
                'TXID In': txid_in or '-',
                'TXID Out': txid_out or '-',
                'Coin': paid_coin or '-',
                'Amount paid': paid_amount,
            })
            return

        # Match CryptoPayMate behavior: pending/unconfirmed callbacks must never
        # confirm the sale order. They only keep the transaction/order visible and
        # add an audit trail in the order chatter.
        if pending_flag:
            if self.state not in ('pending', 'done'):
                self._highriskify_set_pending(_('HighRiskify onramp pending/unconfirmed callback received. Waiting for confirmed callback.'))
            self._highriskify_log_sale_order('HighRiskify onramp payment is pending/unconfirmed', {
                'TXID In': txid_in or '-',
                'TXID Out': txid_out or '-',
                'Coin': paid_coin or '-',
                'Amount paid': paid_amount,
                'USD-equivalent amount': paid_amount_usd,
                'Temporary wallet': self.highriskify_polygon_wallet or self.highriskify_tracking_address or '-',
            })
            self._highriskify_emit_tracking_event('payment_pending', {
                'amount_paid': paid_amount_usd,
                'txid_in': txid_in,
                'txid_out': txid_out,
            })
            return

        if tolerance and float_compare(paid_amount_usd, threshold, precision_rounding=0.01) < 0:
            message = _(
                'HighRiskify payment received is below the configured tolerance. '
                'Expected USD amount: %(expected).2f. Received USD-equivalent amount: %(paid).2f. TXID: %(txid)s',
                expected=expected,
                paid=paid_amount_usd,
                txid=txid_out or txid_in or '-',
            )
            self._highriskify_set_error(message)
            self._highriskify_log_sale_order('HighRiskify onramp payment failed tolerance validation', {
                'Expected USD amount': expected,
                'Received USD-equivalent amount': paid_amount_usd,
                'Threshold': threshold,
                'TXID In': txid_in or '-',
                'TXID Out': txid_out or '-',
                'Coin': paid_coin or '-',
            })
            self._highriskify_emit_tracking_event('payment_failed_partial', {
                'amount_paid': paid_amount_usd,
                'threshold': threshold,
                'txid_in': txid_in,
                'txid_out': txid_out,
            })
            return

        self._highriskify_set_done(_('HighRiskify onramp payment confirmed. TXID: %s') % (txid_out or txid_in or '-'))
        self._highriskify_confirm_sale_orders_after_payment()
        self._highriskify_log_sale_order('HighRiskify onramp payment confirmed and Odoo transaction marked Done', {
            'TXID In': txid_in or '-',
            'TXID Out': txid_out or '-',
            'Coin': paid_coin or '-',
            'Amount paid': paid_amount,
            'USD-equivalent amount': paid_amount_usd,
            'Temporary wallet': self.highriskify_polygon_wallet or self.highriskify_tracking_address or '-',
            'Callback data': json.dumps(notification_data, sort_keys=True, default=str),
        })
        self._highriskify_emit_tracking_event('payment_confirmed', {
            'amount_paid': paid_amount_usd,
            'txid_in': txid_in,
            'txid_out': txid_out,
        })

    def _highriskify_convert_to_usd(self, amount, currency):
        self.ensure_one()
        api_url = f"https://{self.provider_id.highriskify_api_domain}/control/convert.php"
        try:
            response = requests.get(api_url, params={'value': amount, 'from': currency.lower()}, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            _logger.exception('HighRiskify currency conversion failed for %s %s.', amount, currency)
            raise ValidationError(_('HighRiskify currency conversion failed. Please try again.')) from exc

        if 'value_coin' not in data:
            raise ValidationError(_('HighRiskify does not support the current checkout currency: %s.') % currency)
        try:
            return float(data['value_coin'])
        except (TypeError, ValueError) as exc:
            raise ValidationError(_('HighRiskify returned an invalid conversion amount.')) from exc

    def _highriskify_create_wallet(self, callback_url):
        self.ensure_one()
        api_url = f"https://{self.provider_id.highriskify_api_domain}/control/wallet.php"
        try:
            response = requests.get(
                api_url,
                params={'address': self.provider_id.highriskify_wallet_address, 'callback': callback_url},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            _logger.exception('HighRiskify wallet creation failed for transaction %s.', self.reference)
            raise ValidationError(_('HighRiskify wallet creation failed. Please check the payout wallet settings.')) from exc

        if not data.get('address_in'):
            raise ValidationError(_('HighRiskify wallet response did not include address_in.'))
        return data

    def _highriskify_build_callback_url(self):
        self.ensure_one()
        base_url = self.provider_id.get_base_url()
        callback_url = urls.url_join(base_url, '/payment/highriskify_onramp/callback')
        # Match the WooCommerce hosted Insta-Onramp logic: the gateway callback
        # receives order_id + nonce in the callback URL and later appends
        # txid_out, value_coin, and coin. In Odoo, order_id stores the payment
        # transaction reference so callbacks can reliably find the transaction.
        query = urlencode({'order_id': self.reference, 'nonce': self.highriskify_nonce})
        return f'{callback_url}?{query}'

    def _highriskify_build_bridge_url(self):
        """Build an internal Odoo bridge URL with auth data in the path.

        The URL intentionally has no query string because browser GET form
        submissions can strip or replace query parameters.
        """
        self.ensure_one()
        base_url = self.provider_id.get_base_url()
        return urls.url_join(base_url, f'/payment/highriskify_onramp/go/{self.id}/{self.highriskify_nonce}')

    def _highriskify_format_amount_for_checkout(self, amount):
        """Format the amount like the WooCommerce plugin's `(float)$total` redirect."""
        try:
            value = float(amount)
        except (TypeError, ValueError):
            return str(amount or '0')
        if value.is_integer():
            return str(int(value))
        return ('%.8f' % value).rstrip('0').rstrip('.')

    def _highriskify_get_selected_method_config(self):
        """Return the selected HighRiskify payment method config.

        In normal Insta Onramp use, this remains highriskify_onramp and the
        redirect stays exactly the working Woo-style pay.php URL.
        """
        self.ensure_one()
        method_code = const.PROVIDER_CODE
        if 'payment_method_id' in self._fields and self.payment_method_id and self.payment_method_id.code:
            method_code = self.payment_method_id.code
        return const.PAYMENT_METHOD_MAP.get(method_code, const.PAYMENT_METHOD_MAP[const.PROVIDER_CODE])

    def _highriskify_build_pay_url(self, amount, currency):
        self.ensure_one()
        partner = self.partner_id
        method_config = self._highriskify_get_selected_method_config()

        checkout_domain = (self.provider_id.highriskify_checkout_domain or 'checkout.highriskify.com').strip()
        if checkout_domain in ('community.highriskify.com', 'highriskify.com'):
            checkout_domain = 'checkout.highriskify.com'

        checkout_address = quote(unquote(str(self.highriskify_tracking_address or '')), safe='')
        email = quote(partner.email or '', safe='')
        checkout_amount = self._highriskify_format_amount_for_checkout(amount)
        checkout_currency_value = method_config.get('force_currency') or currency or 'USD'
        checkout_currency = quote(checkout_currency_value, safe='')
        checkout_path = method_config.get('path') or 'pay.php'

        pay_url = (
            f"https://{checkout_domain}/{checkout_path}"
            f"?address={checkout_address}"
            f"&amount={checkout_amount}"
        )
        provider_slug = method_config.get('slug')
        if provider_slug:
            pay_url += f"&provider={quote(str(provider_slug), safe='')}"
        pay_url += (
            f"&email={email}"
            f"&currency={checkout_currency}"
        )

        # Only hosted Insta Onramp supports these branding params.
        # The hosted page currently reads logo/colors only, so we do not send unused text params.
        if method_config.get('code') == const.PROVIDER_CODE or checkout_path == 'pay.php':
            optional_map = {
                'logo': self.provider_id.highriskify_logo_url,
                'background': self.provider_id.highriskify_background_color,
                'theme': self.provider_id.highriskify_theme_color,
                'button': self.provider_id.highriskify_button_color,
            }
            for key, value in optional_map.items():
                if value:
                    pay_url += f"&{key}={quote(str(value), safe='')}"
        return pay_url

    def _highriskify_paid_amount_to_usd(self, amount, coin):
        self.ensure_one()
        # Match the WooCommerce hosted Insta-Onramp callback logic exactly:
        # only POL / ETH / BNB native coin callbacks are converted via the
        # crypto info endpoint. Stablecoin amounts are treated as USD-equivalent.
        if coin not in ('polygon_pol', 'eth', 'bep20_bnb'):
            return amount

        coin_path = coin.replace('_', '/')
        api_url = f"https://{self.provider_id.highriskify_api_domain}/crypto/{coin_path}/info.php"
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            usd_price = float(data['prices']['USD'])
            return amount * usd_price
        except Exception:
            _logger.exception('HighRiskify coin price lookup failed for %s; using raw callback amount.', coin)
            return amount

    def _highriskify_get_sale_orders(self):
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
            _logger.debug('HighRiskify could not search sale.order transaction_ids for %s', self.reference, exc_info=True)
        try:
            if self.reference:
                orders |= SaleOrder.search(['|', ('name', '=', self.reference), ('client_order_ref', '=', self.reference)])
        except Exception:
            _logger.debug('HighRiskify could not search sale.order by reference for %s', self.reference, exc_info=True)
        return orders

    def _highriskify_log_sale_order(self, title, details=None):
        self.ensure_one()
        orders = self._highriskify_get_sale_orders()
        if not orders:
            _logger.info('HighRiskify order note skipped because no sale order was linked to transaction %s. %s %s', self.reference, title, details or {})
            return
        lines = [
            f'<b>{html_escape(title)}</b>',
            f'Reference: {html_escape(self.reference or "-")}',
            f'Transaction state: {html_escape(self.state or "-")}',
        ]
        for key, value in (details or {}).items():
            lines.append(f'{html_escape(str(key))}: {html_escape(str(value))}')
        body = '<br/>'.join(lines)
        for order in orders:
            try:
                order.message_post(body=body)
            except Exception:
                _logger.debug('HighRiskify could not post message on sale order %s', order.id, exc_info=True)

    def _highriskify_mark_order_payment_started(self, title):
        """Keep unpaid onramp attempts visible without confirming the sale order.

        Opening the hosted checkout is only an unpaid attempt. The order should
        only be confirmed after a confirmed HighRiskify callback/IPN validates.
        """
        self.ensure_one()
        try:
            if self.state not in ('pending', 'done'):
                self._highriskify_set_pending(_('HighRiskify onramp checkout started. Waiting for confirmed callback.'))
        except Exception:
            _logger.debug('HighRiskify could not set transaction %s pending on checkout start.', self.reference, exc_info=True)
        self._highriskify_log_sale_order(title, {
            'Payment stage': 'Unpaid / waiting for onramp payment',
            'Payment method': self.payment_method_id.name if self.payment_method_id else self.provider_id.name,
            'Expected USD amount': self.highriskify_expected_amount or self.amount,
            'Temporary wallet': self.highriskify_polygon_wallet or self.highriskify_tracking_address or '-',
            'Callback URL': self.highriskify_callback_url or '-',
        })

    def _highriskify_confirm_sale_orders_after_payment(self):
        """Confirm linked website sale orders only after confirmed onramp payment."""
        self.ensure_one()
        orders = self._highriskify_get_sale_orders()
        for order in orders:
            try:
                if order.state in ('draft', 'sent'):
                    order.action_confirm()
                    order.message_post(body='<b>HighRiskify onramp payment confirmed</b><br/>Order confirmed after callback validation.')
            except Exception:
                _logger.exception('HighRiskify could not confirm paid sale order %s for transaction %s.', order.id, self.reference)

    def _highriskify_tracking_event_id(self, payload):
        parts = [
            payload.get('merchant_site', ''),
            payload.get('order_id', ''),
            payload.get('event_type', ''),
            payload.get('txid_out', ''),
        ]
        return hashlib.sha1('|'.join(str(part) for part in parts).encode('utf-8')).hexdigest()

    def _highriskify_tracking_headers(self, payload, provider):
        body = json.dumps(payload, separators=(',', ':'), sort_keys=True, default=str)
        timestamp = str(int(time.time()))
        key = provider.highriskify_tracking_key or const.DEFAULT_TRACKING_KEY
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

    def _highriskify_emit_tracking_event(self, event_type, extra=None):
        self.ensure_one()
        provider = self.provider_id
        endpoint = provider.highriskify_tracking_endpoint or const.DEFAULT_TRACKING_ENDPOINT
        if not endpoint:
            return

        payload = {
            'ipt_version': const.TRACKING_PLUGIN_VERSION,
            'schema': 2,
            'event_type': event_type,
            'platform': 'odoo',
            'merchant_site': self.provider_id.get_base_url().replace('https://', '').replace('http://', '').rstrip('/'),
            'api_domain': provider.highriskify_api_domain,
            'checkout_domain': provider.highriskify_checkout_domain,
            'order_id': self.reference,
            'gateway_id': const.PROVIDER_CODE,
            'gateway_suffix': self._highriskify_get_selected_method_config().get('gateway_suffix', 'hostedinstaonrampdotto'),
            'gateway_name': provider.name,
            'payment_method_code': self._highriskify_get_selected_method_config().get('code', const.PROVIDER_CODE),
            'payment_method_name': self._highriskify_get_selected_method_config().get('name', provider.name),
            'temp_wallet': self.highriskify_polygon_wallet or self.highriskify_tracking_address or f'onramp-{self.reference}',
            'merchant_wallet': provider.highriskify_wallet_address,
            'network': 'polygon',
            'token_symbol': 'USDC',
            'order_total_usd': self.highriskify_expected_amount or self.amount,
            'expected_amount': self.highriskify_expected_amount or self.amount,
            'converted_amount': self.highriskify_original_amount or self.amount,
            'client_email': self.partner_email or self.partner_id.email or '',
        }
        if event_type == 'wallet_created':
            payload['created_at'] = fields.Datetime.now()
        elif event_type == 'payment_confirmed':
            payload['confirmed_at'] = fields.Datetime.now()
        elif event_type == 'payment_failed_partial':
            payload['failed_at'] = fields.Datetime.now()
        else:
            payload['occurred_at'] = fields.Datetime.now()
        if extra:
            payload.update(extra)
        payload['event_id'] = self._highriskify_tracking_event_id(payload)

        try:
            body, headers = self._highriskify_tracking_headers(payload, provider)
            requests.post(endpoint, data=body, headers=headers, timeout=10)
        except Exception:
            _logger.exception('Failed to emit HighRiskify tracking event %s for transaction %s.', event_type, self.reference)
