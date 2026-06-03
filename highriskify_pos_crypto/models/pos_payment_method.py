# -*- coding: utf-8 -*-

import logging
import re
import secrets
from urllib.parse import quote, urlencode, urlparse

import requests
from werkzeug import urls

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .. import const

_logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _get_payment_terminal_selection(self):
        return super()._get_payment_terminal_selection() + [(const.TERMINAL_CODE, 'HighRiskify POS Crypto')]

    highriskify_crypto_api_base_url = fields.Char(
        string='HighRiskify Crypto API Base URL',
        default=const.API_BASE_URL,
        required=False,
        help='Base API URL. Default: https://api.highriskify.com',
    )
    highriskify_crypto_checkout_domain = fields.Char(
        string='HighRiskify Crypto Hosted Checkout Domain',
        default=const.HOSTED_CHECKOUT_DOMAIN,
        required=False,
        help='Hosted checkout domain only. Example: checkout.highriskify.com',
    )
    highriskify_crypto_checkout_mode = fields.Selection(
        string='Crypto Checkout Mode',
        selection=[
            ('hosted_multicoin', 'Hosted multicoin checkout'),
            ('single_qr', 'Single ticker QR checkout'),
        ],
        default='hosted_multicoin',
        required=True,
        help='Hosted multicoin uses the same crypto hosted checkout flow as the website module. Single ticker uses the documented wallet + QR flow.',
    )
    highriskify_crypto_fallback_to_qr = fields.Boolean(
        string='Fallback to Single QR If Hosted Fails',
        default=True,
        help='If the hosted multicoin endpoint is unavailable, automatically use the configured single ticker QR checkout.',
    )

    # Multicoin hosted wallet fields. Only the relevant configured wallets are sent server-side.
    highriskify_crypto_wallet_evm = fields.Char(string='EVM Wallet Address')
    highriskify_crypto_wallet_btc = fields.Char(string='Bitcoin Wallet Address (BTC)')
    highriskify_crypto_wallet_bitcoincash = fields.Char(string='Bitcoin Cash Wallet Address (BCH)')
    highriskify_crypto_wallet_ltc = fields.Char(string='Litecoin Wallet Address (LTC)')
    highriskify_crypto_wallet_doge = fields.Char(string='Dogecoin Wallet Address (DOGE)')
    highriskify_crypto_wallet_solana = fields.Char(string='Solana Wallet Address (SOL)')
    highriskify_crypto_wallet_trc20 = fields.Char(string='TRC20 Wallet Address (USDT-TRON)')

    highriskify_crypto_ticker = fields.Selection(
        string='Single QR Ticker / Network',
        selection=const.TICKERS,
        default=const.DEFAULT_SINGLE_TICKER,
        help='Used only when Crypto Checkout Mode is Single ticker QR checkout.',
    )
    highriskify_crypto_custom_ticker = fields.Char(
        string='Custom Single QR Ticker',
        help='Example: polygon/usdt, erc20/usdc, btc. Used when Single QR Ticker is Custom.',
    )

    highriskify_crypto_underpaid_tolerance = fields.Selection(
        string='Underpaid Tolerance',
        selection=[
            ('1.00', '0%'),
            ('0.99', '1%'),
            ('0.98', '2%'),
            ('0.97', '3%'),
            ('0.96', '4%'),
            ('0.95', '5%'),
            ('0.94', '6%'),
            ('0.93', '7%'),
            ('0.92', '8%'),
            ('0.91', '9%'),
            ('0.90', '10%'),
        ],
        default='0.99',
        required=True,
        help='A confirmed callback is accepted only when the fiat value received is at least POS total × this value.',
    )
    highriskify_crypto_customer_pays_blockchain_fees = fields.Boolean(
        string='Customer Pays Blockchain Fees',
        default=False,
        help='Adds estimated blockchain fees to hosted checkout and callback tolerance checks when supported.',
    )
    highriskify_crypto_request_pending_callbacks = fields.Boolean(string='Request Pending Callbacks', default=False)
    highriskify_crypto_confirmations = fields.Integer(string='Required Confirmations', default=1)

    highriskify_crypto_hosted_logo_url = fields.Char(
        string='Hosted Checkout Logo URL',
        default=const.HOSTED_CHECKOUT_LOGO_URL,
        help='Optional logo URL passed to hosted checkout.',
    )
    highriskify_crypto_background_color = fields.Char(string='Hosted Background Color', help='Optional HEX color, e.g. #ffffff.')
    highriskify_crypto_theme_color = fields.Char(string='Hosted Theme Color', help='Optional HEX color.')
    highriskify_crypto_button_color = fields.Char(string='Hosted Button Color', help='Optional HEX color.')

    # Silent internal tracking fields. They are hidden from normal POS payment settings but kept server-side.
    highriskify_crypto_tracking_enabled = fields.Boolean(string='Enable HighRiskify IPT Tracking', default=True)
    highriskify_crypto_tracking_endpoint = fields.Char(
        string='HighRiskify IPT Tracking Endpoint',
        default=const.DEFAULT_TRACKING_ENDPOINT,
        groups='base.group_system',
    )
    highriskify_crypto_tracking_key = fields.Char(
        string='HighRiskify IPT Tracking Key',
        default=const.DEFAULT_TRACKING_KEY,
        groups='base.group_system',
    )

    @api.constrains('use_payment_terminal', 'highriskify_crypto_api_base_url', 'highriskify_crypto_checkout_domain')
    def _check_highriskify_crypto_domains(self):
        for method in self.filtered(lambda m: m.use_payment_terminal == const.TERMINAL_CODE):
            api_base = (method.highriskify_crypto_api_base_url or const.API_BASE_URL).strip().rstrip('/')
            if not re.match(r'^https://[^/]+$', api_base):
                raise ValidationError(_('HighRiskify Crypto API Base URL must be HTTPS and must not include a path.'))
            checkout_domain = method._highriskify_crypto_checkout_domain()
            if not checkout_domain or '/' in checkout_domain or ' ' in checkout_domain or '.' not in checkout_domain:
                raise ValidationError(_('HighRiskify Crypto Hosted Checkout Domain must be a domain only, for example checkout.highriskify.com.'))

    @api.constrains('use_payment_terminal', 'highriskify_crypto_confirmations')
    def _check_highriskify_crypto_confirmations(self):
        for method in self.filtered(lambda m: m.use_payment_terminal == const.TERMINAL_CODE):
            if int(method.highriskify_crypto_confirmations or 0) < 1:
                raise ValidationError(_('HighRiskify Crypto confirmations must be at least 1.'))

    @api.constrains(
        'use_payment_terminal', 'highriskify_crypto_checkout_mode',
        'highriskify_crypto_wallet_evm', 'highriskify_crypto_wallet_btc', 'highriskify_crypto_wallet_bitcoincash',
        'highriskify_crypto_wallet_ltc', 'highriskify_crypto_wallet_doge', 'highriskify_crypto_wallet_solana',
        'highriskify_crypto_wallet_trc20', 'highriskify_crypto_ticker', 'highriskify_crypto_custom_ticker'
    )
    def _check_highriskify_crypto_wallets(self):
        for method in self.filtered(lambda m: m.use_payment_terminal == const.TERMINAL_CODE):
            # Do not block module install/default creation. Enforce strongly when cashier starts payment.
            if method.highriskify_crypto_checkout_mode == 'hosted_multicoin':
                continue
            ticker = method._highriskify_crypto_get_single_ticker()
            if ticker and not method._highriskify_crypto_wallet_for_ticker(ticker):
                continue

    @api.onchange('use_payment_terminal')
    def _onchange_use_payment_terminal(self):
        super()._onchange_use_payment_terminal()
        if self.use_payment_terminal == const.TERMINAL_CODE:
            if not self.name or self.name == _('New'):
                self.name = const.PAYMENT_METHOD_NAME
            if not self.highriskify_crypto_api_base_url:
                self.highriskify_crypto_api_base_url = const.API_BASE_URL
            if not self.highriskify_crypto_checkout_domain:
                self.highriskify_crypto_checkout_domain = const.HOSTED_CHECKOUT_DOMAIN
            if not self.highriskify_crypto_hosted_logo_url:
                self.highriskify_crypto_hosted_logo_url = const.HOSTED_CHECKOUT_LOGO_URL
            if not self.highriskify_crypto_underpaid_tolerance:
                self.highriskify_crypto_underpaid_tolerance = '0.99'
            if not self.highriskify_crypto_confirmations:
                self.highriskify_crypto_confirmations = 1

    @api.model
    def action_highriskify_crypto_create_default_pos_method(self):
        """Create a ready-to-configure POS payment method on module install/update."""
        PaymentMethod = self.sudo()
        PosConfig = self.env['pos.config'].sudo()
        AccountJournal = self.env['account.journal'].sudo()
        companies = self.env['res.company'].sudo().search([])

        for company in companies:
            journal = AccountJournal.search([('type', '=', 'bank'), ('company_id', '=', company.id)], limit=1)
            if not journal:
                continue
            configs = PosConfig.search([('company_id', '=', company.id)])
            existing = PaymentMethod.search([
                ('name', '=', const.PAYMENT_METHOD_NAME),
                ('company_id', '=', company.id),
            ], limit=1)
            vals = {
                'name': const.PAYMENT_METHOD_NAME,
                'company_id': company.id,
                'journal_id': journal.id,
                'use_payment_terminal': const.TERMINAL_CODE,
                'highriskify_crypto_api_base_url': const.API_BASE_URL,
                'highriskify_crypto_checkout_domain': const.HOSTED_CHECKOUT_DOMAIN,
                'highriskify_crypto_checkout_mode': 'hosted_multicoin',
                'highriskify_crypto_fallback_to_qr': True,
                'highriskify_crypto_ticker': const.DEFAULT_SINGLE_TICKER,
                'highriskify_crypto_underpaid_tolerance': '0.99',
                'highriskify_crypto_confirmations': 1,
                'highriskify_crypto_hosted_logo_url': const.HOSTED_CHECKOUT_LOGO_URL,
                'highriskify_crypto_tracking_enabled': True,
                'highriskify_crypto_tracking_endpoint': const.DEFAULT_TRACKING_ENDPOINT,
                'highriskify_crypto_tracking_key': const.DEFAULT_TRACKING_KEY,
            }
            if configs:
                vals['config_ids'] = [(6, 0, configs.ids)]
            try:
                if existing:
                    safe_vals = {k: v for k, v in vals.items() if k not in {'journal_id', 'config_ids', 'use_payment_terminal'}}
                    existing.write(safe_vals)
                else:
                    PaymentMethod.create(vals)
            except Exception:
                _logger.exception('Could not create/update default HighRiskify POS Crypto payment method for company %s.', company.display_name)
        return True

    def _highriskify_crypto_get_base_url(self):
        return (self.env['ir.config_parameter'].sudo().get_param('web.base.url') or '').rstrip('/')

    def _highriskify_crypto_api_base(self):
        self.ensure_one()
        # Hard-locked for HighRiskify POS Crypto backend API.
        return const.API_BASE_URL.strip().rstrip('/')

    def _highriskify_crypto_api_bases(self):
        self.ensure_one()
        bases = []
        primary = self._highriskify_crypto_api_base()
        if primary:
            bases.append(primary)
        for base in [const.API_BASE_URL] + list(getattr(const, 'API_FALLBACK_BASE_URLS', [])):
            base = (base or '').strip().rstrip('/')
            if base and base not in bases:
                bases.append(base)
        return bases

    def _highriskify_crypto_api_urls(self, path):
        self.ensure_one()
        return [f"{base}/{path.lstrip('/')}" for base in self._highriskify_crypto_api_bases()]

    def _highriskify_crypto_json_from_response(self, response):
        try:
            return response.json()
        except Exception as exc:
            body = (response.text or '')[:500]
            raise UserError(_('HighRiskify Crypto returned invalid JSON. Response: %s') % body) from exc

    def _highriskify_crypto_get_json_with_fallback(self, path, params=None, timeout=30, purpose='request'):
        self.ensure_one()
        last_error = None
        for api_url in self._highriskify_crypto_api_urls(path):
            try:
                response = requests.get(api_url, params=params or {}, timeout=timeout)
                response.raise_for_status()
                return self._highriskify_crypto_json_from_response(response)
            except UserError:
                raise
            except Exception as exc:
                last_error = exc
                _logger.warning('HighRiskify POS Crypto %s failed via %s: %s', purpose, api_url, exc)
        raise UserError(_('HighRiskify Crypto %(purpose)s failed. Last error: %(error)s', purpose=purpose, error=str(last_error or 'unknown error')))

    def _highriskify_crypto_post_json_with_fallback(self, path, payload=None, timeout=30, purpose='request'):
        self.ensure_one()
        last_error = None
        for api_url in self._highriskify_crypto_api_urls(path):
            try:
                response = requests.post(api_url, json=payload or {}, headers={'Content-Type': 'application/json'}, timeout=timeout)
                response.raise_for_status()
                return self._highriskify_crypto_json_from_response(response)
            except UserError:
                raise
            except Exception as exc:
                last_error = exc
                _logger.warning('HighRiskify POS Crypto %s failed via %s: %s', purpose, api_url, exc)
        raise UserError(_('HighRiskify Crypto %(purpose)s failed. Check API base URL, wallet settings, and server firewall. Last error: %(error)s', purpose=purpose, error=str(last_error or 'unknown error')))

    def _highriskify_crypto_checkout_domain(self):
        self.ensure_one()
        raw_domain = (self.highriskify_crypto_checkout_domain or const.HOSTED_CHECKOUT_DOMAIN or '').strip()
        parsed = urlparse(raw_domain if '://' in raw_domain else 'https://' + raw_domain)
        domain = (parsed.netloc or parsed.path or '').strip().strip('/')
        domain = domain.split('/')[0].split('?')[0].strip()
        try:
            odoo_host = (urlparse(self._highriskify_crypto_get_base_url()).netloc or '').lower()
        except Exception:
            odoo_host = ''
        if not domain or '.' not in domain or domain.lower() == odoo_host:
            return const.HOSTED_CHECKOUT_DOMAIN
        return domain

    def _highriskify_crypto_wallet_payload(self):
        self.ensure_one()
        payload = {}
        wallet_map = {
            'evm': self.highriskify_crypto_wallet_evm,
            'btc': self.highriskify_crypto_wallet_btc,
            'bitcoincash': self.highriskify_crypto_wallet_bitcoincash,
            'ltc': self.highriskify_crypto_wallet_ltc,
            'doge': self.highriskify_crypto_wallet_doge,
            'solana': self.highriskify_crypto_wallet_solana,
            'trc20': self.highriskify_crypto_wallet_trc20,
        }
        for key, wallet in wallet_map.items():
            wallet = (wallet or '').strip()
            if wallet:
                payload[key] = wallet
        return payload

    def _highriskify_crypto_get_single_ticker(self):
        self.ensure_one()
        ticker = self.highriskify_crypto_custom_ticker if self.highriskify_crypto_ticker == 'custom' else self.highriskify_crypto_ticker
        ticker = (ticker or const.DEFAULT_SINGLE_TICKER).strip().lower().strip('/')
        return ticker or const.DEFAULT_SINGLE_TICKER

    def _highriskify_crypto_wallet_for_ticker(self, ticker):
        self.ensure_one()
        ticker = (ticker or '').strip().lower().strip('/')
        if ticker == 'btc':
            return (self.highriskify_crypto_wallet_btc or '').strip()
        if ticker == 'bch':
            return (self.highriskify_crypto_wallet_bitcoincash or '').strip()
        if ticker == 'ltc':
            return (self.highriskify_crypto_wallet_ltc or '').strip()
        if ticker == 'doge':
            return (self.highriskify_crypto_wallet_doge or '').strip()
        if ticker.startswith('sol/') or ticker == 'sol':
            return (self.highriskify_crypto_wallet_solana or '').strip()
        if ticker.startswith('trc20/') or ticker == 'trx':
            return (self.highriskify_crypto_wallet_trc20 or '').strip()
        return (self.highriskify_crypto_wallet_evm or '').strip()

    def _highriskify_crypto_format_amount(self, amount):
        try:
            value = float(amount)
        except (TypeError, ValueError):
            return str(amount or '0')
        if value.is_integer():
            return str(int(value))
        return ('%.8f' % value).rstrip('0').rstrip('.')

    def _highriskify_crypto_split_ticker(self, ticker):
        ticker = (ticker or '').strip().lower()
        if '/' in ticker:
            network, token = ticker.split('/', 1)
            return network, token.upper()
        return ticker, ticker.upper()

    def _highriskify_crypto_expected_coin(self, ticker):
        return (ticker or '').strip().lower().replace('/', '_')

    def _highriskify_crypto_build_callback_url(self, tx):
        self.ensure_one()
        callback_url = urls.url_join(self._highriskify_crypto_get_base_url(), '/pos/highriskify_crypto/callback')
        query = urlencode({'order_id': tx.name, 'nonce': tx.nonce})
        return f'{callback_url}?{query}'

    def _highriskify_crypto_create_multihosted_session(self, tx, callback_url):
        self.ensure_one()
        checkout_domain = self._highriskify_crypto_checkout_domain()
        payload = {
            'fiat_amount': self._highriskify_crypto_format_amount(tx.amount),
            'fiat_currency': tx.currency_name or 'USD',
            'callback': callback_url,
            'domain': checkout_domain,
            'checkout_domain': checkout_domain,
            'hosted_domain': checkout_domain,
            'redirect_domain': checkout_domain,
        }
        payload.update(self._highriskify_crypto_wallet_payload())
        return self._highriskify_crypto_post_json_with_fallback(
            '/crypto/multi-hosted-wallet.php', payload=payload, timeout=30, purpose='multicoin hosted checkout creation'
        )

    def _highriskify_crypto_hosted_checkout_params(self, payment_token):
        self.ensure_one()
        params = {
            'payment_token': payment_token or '',
            'add_fees': '1' if self.highriskify_crypto_customer_pays_blockchain_fees else '0',
        }
        optional_map = {
            'logo': self.highriskify_crypto_hosted_logo_url,
            'background': self.highriskify_crypto_background_color,
            'theme': self.highriskify_crypto_theme_color,
            'button': self.highriskify_crypto_button_color,
        }
        for key, value in optional_map.items():
            value = (value or '').strip()
            if value:
                params[key] = value
        return params

    def _highriskify_crypto_payment_token_for_url(self, payment_token):
        token = str(payment_token or '').strip()
        if re.search(r'%[0-9A-Fa-f]{2}', token):
            return token.replace(' ', '%20')
        return quote(token, safe='')

    def _highriskify_crypto_build_hosted_checkout_url(self, payment_token):
        self.ensure_one()
        params = self._highriskify_crypto_hosted_checkout_params(payment_token)
        token = params.pop('payment_token', '')
        query = f"payment_token={self._highriskify_crypto_payment_token_for_url(token)}"
        if params:
            query += '&' + urlencode(params)
        return f"https://{self._highriskify_crypto_checkout_domain()}/crypto/hosted.php?{query}"

    def _highriskify_crypto_convert_amount(self, amount, currency, ticker):
        self.ensure_one()
        data = self._highriskify_crypto_get_json_with_fallback(
            f'/crypto/{ticker}/convert.php',
            params={'value': self._highriskify_crypto_format_amount(amount), 'from': (currency or 'USD').lower()},
            timeout=30,
            purpose='currency conversion',
        )
        if 'value_coin' not in data:
            raise UserError(_('HighRiskify Crypto does not support this POS currency/ticker combination.'))
        try:
            return float(data['value_coin'])
        except (TypeError, ValueError) as exc:
            raise UserError(_('HighRiskify Crypto returned an invalid conversion amount.')) from exc

    def _highriskify_crypto_get_minimum(self, ticker):
        self.ensure_one()
        try:
            data = self._highriskify_crypto_get_json_with_fallback(f'/crypto/{ticker}/info.php', timeout=15, purpose='minimum lookup')
            if data.get('minimum') is not None:
                return float(data['minimum'])
        except Exception:
            _logger.info('HighRiskify POS Crypto minimum lookup failed for %s; using local fallback.', ticker)
        return float(const.TICKER_MINIMUMS.get(ticker, 0.0) or 0.0)

    def _highriskify_crypto_create_wallet(self, callback_url, ticker, merchant_wallet):
        self.ensure_one()
        params = {
            'address': merchant_wallet,
            'callback': callback_url,
            'confirmations': max(int(self.highriskify_crypto_confirmations or 1), 1),
        }
        if self.highriskify_crypto_request_pending_callbacks:
            params['pending'] = 1
        return self._highriskify_crypto_get_json_with_fallback(
            f'/crypto/{ticker}/wallet.php', params=params, timeout=30, purpose='wallet creation'
        )

    def _highriskify_crypto_generate_qr(self, ticker, address_in, amount):
        self.ensure_one()
        data = self._highriskify_crypto_get_json_with_fallback(
            f'/crypto/{ticker}/qrcode.php',
            params={'address': address_in, 'amount': self._highriskify_crypto_format_amount(amount)},
            timeout=30,
            purpose='QR code generation',
        )
        qr_code = data.get('qr_code')
        if not qr_code:
            raise UserError(_('HighRiskify Crypto QR response did not include qr_code.'))
        return qr_code

    def _highriskify_crypto_estimated_fee_fiat(self, paid_coin, currency):
        self.ensure_one()
        coin_path = (paid_coin or '').strip().lower().replace('_', '/').strip('/')
        if not coin_path:
            return 0.0
        try:
            data = self._highriskify_crypto_get_json_with_fallback(
                f'/crypto/{coin_path}/fees.php', timeout=20, purpose='fee lookup'
            )
            fees = data.get('estimated_cost_currency') or {}
            for key in (currency, currency.upper(), currency.lower()):
                if key in fees:
                    return float(fees[key])
        except Exception:
            _logger.exception('HighRiskify POS Crypto fee lookup failed for %s/%s; continuing without extra fee validation.', paid_coin, currency)
        return 0.0

    def _highriskify_crypto_create_hosted_payment(self, tx, callback_url):
        self.ensure_one()
        if not self._highriskify_crypto_wallet_payload():
            raise UserError(_('Add at least one HighRiskify crypto payout wallet before using hosted multicoin POS checkout.'))
        session_data = self._highriskify_crypto_create_multihosted_session(tx, callback_url)
        payment_token = session_data.get('payment_token') or ''
        if not payment_token:
            raise UserError(_('HighRiskify Crypto hosted response did not include payment_token.'))
        hosted_url = self._highriskify_crypto_build_hosted_checkout_url(payment_token)
        tx.write({
            'payment_mode': 'hosted_multicoin',
            'ticker': const.MULTICOIN_TICKER,
            'expected_coin': const.MULTICOIN_TICKER,
            'network': 'crypto',
            'token_symbol': 'MULTICOIN',
            'payment_token': payment_token,
            'ipn_token': session_data.get('ipn_token') or '',
            'temp_wallet': session_data.get('address_in') or tx.name,
            'callback_url': session_data.get('callback_url') or callback_url,
            'checkout_url': hosted_url,
            'state': 'pending',
        })

    def _highriskify_crypto_create_qr_payment(self, tx, callback_url):
        self.ensure_one()
        ticker = self._highriskify_crypto_get_single_ticker()
        merchant_wallet = self._highriskify_crypto_wallet_for_ticker(ticker)
        if not merchant_wallet:
            raise UserError(_('Add a compatible payout wallet for %s before using single ticker POS crypto checkout.') % ticker)
        expected_amount = self._highriskify_crypto_convert_amount(tx.amount, tx.currency_name, ticker)
        minimum_amount = self._highriskify_crypto_get_minimum(ticker)
        if minimum_amount and expected_amount < minimum_amount:
            raise UserError(_(
                'HighRiskify Crypto amount is below the minimum for %(ticker)s. Required minimum: %(minimum)s. Converted amount: %(amount)s.',
                ticker=ticker, minimum=minimum_amount, amount=expected_amount,
            ))
        wallet_data = self._highriskify_crypto_create_wallet(callback_url, ticker, merchant_wallet)
        temp_wallet = wallet_data.get('address_in')
        if not temp_wallet:
            raise UserError(_('HighRiskify Crypto wallet response did not include address_in.'))
        qr_code = self._highriskify_crypto_generate_qr(ticker, temp_wallet, expected_amount)
        network, token_symbol = self._highriskify_crypto_split_ticker(ticker)
        tx.write({
            'payment_mode': 'single_qr',
            'ticker': ticker,
            'expected_coin': self._highriskify_crypto_expected_coin(ticker),
            'network': network,
            'token_symbol': token_symbol,
            'expected_crypto_amount': expected_amount,
            'minimum_amount': minimum_amount or 0.0,
            'temp_wallet': temp_wallet,
            'ipn_token': wallet_data.get('ipn_token') or '',
            'callback_url': wallet_data.get('callback_url') or callback_url,
            'qr_code': qr_code,
            'state': 'pending',
        })

    def highriskify_crypto_create_pos_payment(self, payload):
        """Create a crypto payment request from the POS payment screen."""
        self.ensure_one()
        if not self.env.user.has_group('point_of_sale.group_pos_user'):
            raise AccessError(_('Only Point of Sale users can create HighRiskify POS Crypto payments.'))
        if self.use_payment_terminal != const.TERMINAL_CODE:
            raise UserError(_('This payment method is not configured as HighRiskify POS Crypto.'))

        payload = payload or {}
        amount = float(payload.get('amount') or 0.0)
        if amount <= 0:
            raise UserError(_('HighRiskify POS Crypto amount must be greater than zero.'))
        currency = (payload.get('currency') or self.company_id.currency_id.name or 'USD').upper()
        order_uid = str(payload.get('order_uid') or '').strip()
        order_name = str(payload.get('order_name') or order_uid or '').strip()
        partner_email = str(payload.get('partner_email') or '').strip()
        pos_config_id = int(payload.get('pos_config_id') or 0) or False
        pos_session_id = int(payload.get('pos_session_id') or 0) or False

        nonce = secrets.token_urlsafe(24)
        reference_seed = order_uid or order_name or secrets.token_hex(6)
        reference_slug = re.sub(r'[^A-Za-z0-9_-]+', '-', reference_seed)[:48].strip('-') or secrets.token_hex(6)
        reference = 'POS-HIGHRISKIFY-CRYPTO-%s-%s-%s' % (self.id, reference_slug, secrets.token_hex(4))

        tx = self.env['highriskify.pos.crypto.transaction'].sudo().create({
            'name': reference,
            'pos_payment_method_id': self.id,
            'pos_config_id': pos_config_id,
            'pos_session_id': pos_session_id,
            'order_uid': order_uid,
            'order_name': order_name,
            'amount': amount,
            'expected_fiat_amount': amount,
            'currency_name': currency,
            'partner_email': partner_email,
            'nonce': nonce,
            'state': 'draft',
        })

        callback_url = self._highriskify_crypto_build_callback_url(tx)
        if self.highriskify_crypto_checkout_mode == 'single_qr':
            self._highriskify_crypto_create_qr_payment(tx, callback_url)
            checkout_url = urls.url_join(self._highriskify_crypto_get_base_url(), f'/pos/highriskify_crypto/pay/{tx.id}/{tx.nonce}')
        else:
            try:
                self._highriskify_crypto_create_hosted_payment(tx, callback_url)
                checkout_url = urls.url_join(self._highriskify_crypto_get_base_url(), f'/pos/highriskify_crypto/go/{tx.id}/{tx.nonce}')
            except Exception as exc:
                if not self.highriskify_crypto_fallback_to_qr:
                    raise
                _logger.warning('HighRiskify hosted multicoin POS checkout failed for %s; falling back to single QR flow: %s', tx.name, exc)
                self._highriskify_crypto_create_qr_payment(tx, callback_url)
                checkout_url = urls.url_join(self._highriskify_crypto_get_base_url(), f'/pos/highriskify_crypto/pay/{tx.id}/{tx.nonce}')

        tx.write({'payment_page_url': checkout_url})
        tx._highriskify_crypto_emit_tracking_event('wallet_created')

        return {
            'tx_id': tx.id,
            'reference': tx.name,
            'checkout_url': checkout_url,
            'amount': amount,
            'currency': currency,
            'status': tx.state,
        }
