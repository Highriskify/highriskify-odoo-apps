# -*- coding: utf-8 -*-

import base64
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import file_open

from .. import const


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    def _cryptopaymate_load_module_image(self, relative_path):
        try:
            with file_open(f'highriskify_crypto/{relative_path}', 'rb') as image_file:
                return base64.b64encode(image_file.read())
        except Exception:
            return False

    def _default_cryptopaymate_backend_logo(self):
        return self._cryptopaymate_load_module_image('static/src/img/highriskify_backend_logo_150.png')

    def _default_cryptopaymate_frontend_logo(self):
        return self._cryptopaymate_load_module_image('static/src/img/cryptopaymate_multicoin.png')

    @api.model
    def action_cryptopaymate_seed_branding(self):
        """Attach the single hosted multicoin payment method and seed local branding."""
        providers = self.search([('code', '=', const.PROVIDER_CODE)])
        if not providers:
            return True

        PaymentMethod = self.env['payment.method'].sudo()
        all_methods = PaymentMethod.browse()
        default_methods = PaymentMethod.browse()
        sequence = 1100
        for method_code, _ticker, label in const.PAYMENT_METHODS:
            vals = {
                'name': label,
                'sequence': sequence,
                # Keep methods unarchived so admins can manually add them later,
                # but do NOT attach every method to the provider automatically.
                'active': method_code == const.MULTICOIN_METHOD_CODE,
            }
            if 'code' in PaymentMethod._fields:
                vals['code'] = method_code
            if 'support_tokenization' in PaymentMethod._fields:
                vals['support_tokenization'] = False

            method = PaymentMethod.search([('code', '=', method_code)], limit=1)
            if method:
                method.write(vals)
            else:
                method = PaymentMethod.create(vals)
            all_methods |= method
            if method_code == const.MULTICOIN_METHOD_CODE:
                default_methods |= method
            sequence += 1

        backend_logo = self._default_cryptopaymate_backend_logo()
        frontend_logo = self._default_cryptopaymate_frontend_logo()

        def image_vals(record, image_binary):
            vals = {}
            if not image_binary:
                return vals
            for image_field in ('image_1920', 'image_1024', 'image_512', 'image_256', 'image_128', 'image'):
                if image_field in record._fields:
                    vals[image_field] = image_binary
            return vals

        for provider in providers:
            vals = {
                'name': const.GATEWAY_DISPLAY_NAME,
                'cryptopaymate_api_base_url': const.API_BASE_URL,
                'cryptopaymate_checkout_domain': const.HOSTED_CHECKOUT_DOMAIN,
                'cryptopaymate_tracking_enabled': True,
                'cryptopaymate_tracking_endpoint': const.DEFAULT_TRACKING_ENDPOINT,
                'cryptopaymate_tracking_key': const.DEFAULT_TRACKING_KEY,
            }
            if 'payment_method_ids' in provider._fields:
                # New installs/updates should NOT publish all 100+ coin methods on checkout.
                # Only the main multicoin hosted method is attached by default; admins can
                # manually add individual coin QR methods later from the provider settings.
                vals['payment_method_ids'] = [(6, 0, default_methods.ids)]
            if 'cryptopaymate_backend_logo' in provider._fields and backend_logo:
                vals['cryptopaymate_backend_logo'] = backend_logo
            if 'cryptopaymate_frontend_logo' in provider._fields and frontend_logo:
                vals['cryptopaymate_frontend_logo'] = frontend_logo
            if 'pre_msg' in provider._fields:
                vals['pre_msg'] = _(
                    '<div class="o_cryptopaymate_payment_message">'
                    'Pay via secure multicoin crypto checkout. Available coin options are shown based on the payout wallets configured by the merchant.'
                    '</div>'
                )
            # Smooth migration from older single-wallet versions: copy old merchant wallet into EVM wallet if empty.
            if 'cryptopaymate_wallet_evm' in provider._fields and not provider.cryptopaymate_wallet_evm and provider.cryptopaymate_merchant_wallet:
                vals['cryptopaymate_wallet_evm'] = provider.cryptopaymate_merchant_wallet
            vals.update(image_vals(provider, backend_logo))
            provider.write(vals)

        for method in all_methods:
            vals = image_vals(method, frontend_logo or backend_logo)
            if vals:
                method.write(vals)

        return True

    code = fields.Selection(
        selection_add=[(const.PROVIDER_CODE, 'HighRiskify Crypto')],
        ondelete={const.PROVIDER_CODE: 'set default'},
    )

    cryptopaymate_api_base_url = fields.Char(
        string='API Base URL',
        default=const.API_BASE_URL,
        required=True,
        help='Base API URL used to create the multicoin hosted checkout session.',
    )
    cryptopaymate_checkout_domain = fields.Char(
        string='Hosted Checkout Domain',
        default=const.HOSTED_CHECKOUT_DOMAIN,
        required=True,
        help='Domain used for the customer-facing hosted checkout page, for example checkout.highriskify.com.',
    )

    # Backward-compatible old field. Hidden from the view but kept to avoid breaking existing installed databases.
    cryptopaymate_merchant_wallet = fields.Char(string='Merchant Payout Wallet')
    cryptopaymate_ticker = fields.Selection(string='Crypto Ticker / Network', selection=const.TICKERS, default='multicoin')
    cryptopaymate_custom_ticker = fields.Char(string='Custom Ticker')

    # Multicoin hosted checkout wallet fields, matching the WooCommerce plugin.
    cryptopaymate_wallet_evm = fields.Char(
        string='EVM Wallet Address',
        help='ERC20/ETH/BEP20/Polygon/Optimism/Arbitrum/Base/Avax-C compatible wallet.',
    )
    cryptopaymate_wallet_btc = fields.Char(string='Bitcoin Wallet Address (BTC)')
    cryptopaymate_wallet_bitcoincash = fields.Char(string='Bitcoin Cash Wallet Address (BCH)')
    cryptopaymate_wallet_ltc = fields.Char(string='Litecoin Wallet Address (LTC)')
    cryptopaymate_wallet_doge = fields.Char(string='Dogecoin Wallet Address (DOGE)')
    cryptopaymate_wallet_solana = fields.Char(string='Solana Wallet Address (SOL)')
    cryptopaymate_wallet_trc20 = fields.Char(string='TRC20 Wallet Address (USDT-TRON)')

    cryptopaymate_underpaid_tolerance = fields.Selection(
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
        help='Payment is accepted only when the received fiat value is at least order total × this value.',
    )
    cryptopaymate_customer_pays_blockchain_fees = fields.Boolean(
        string='Customer Pays Blockchain Fees',
        default=False,
        help='Adds estimated blockchain fees to the hosted checkout payment amount, same as the WooCommerce multicoin gateway.',
    )
    cryptopaymate_request_pending_callbacks = fields.Boolean(string='Request Pending Callbacks', default=False)
    cryptopaymate_confirmations = fields.Integer(string='Required Confirmations', default=1)

    # Kept for compatibility; not displayed for the hosted multicoin flow.
    cryptopaymate_use_mass_payout = fields.Boolean(string='Use Mass Payout Split', default=False)
    cryptopaymate_sub_wallet = fields.Char(string='Sub / Affiliate Wallet')
    cryptopaymate_platform_wallet = fields.Char(string='Platform Wallet')
    cryptopaymate_merchant_percent = fields.Float(string='Merchant Split', default=0.92, digits=(12, 6))
    cryptopaymate_sub_percent = fields.Float(string='Sub Split', default=0.03, digits=(12, 6))
    cryptopaymate_platform_percent = fields.Float(string='Platform Split', default=0.04, digits=(12, 6))

    # Silent IPT tracking. These fields stay in the model for storage/backward compatibility but are not shown in Odoo views.
    cryptopaymate_tracking_enabled = fields.Boolean(string='Enable IPT Tracking', default=True)
    cryptopaymate_tracking_endpoint = fields.Char(string='IPT Tracking Endpoint', default=const.DEFAULT_TRACKING_ENDPOINT)
    cryptopaymate_tracking_key = fields.Char(string='IPT Tracking API Key', default=const.DEFAULT_TRACKING_KEY, groups='base.group_system')

    cryptopaymate_backend_logo = fields.Image(
        string='Backend Logo',
        max_width=150,
        max_height=150,
        default=_default_cryptopaymate_backend_logo,
    )
    cryptopaymate_frontend_logo = fields.Image(
        string='Checkout Crypto Logos',
        default=_default_cryptopaymate_frontend_logo,
    )
    cryptopaymate_hosted_logo_url = fields.Char(
        string='Hosted Checkout Logo URL',
        help='Optional URL passed to the hosted checkout page. Leave empty to use HighRiskify Crypto default hosted branding.',
    )
    cryptopaymate_background_color = fields.Char(string='Hosted Background Color', help='Optional HEX color, e.g. #ffffff.')
    cryptopaymate_theme_color = fields.Char(string='Hosted Theme Color', help='Optional HEX color.')
    cryptopaymate_button_color = fields.Char(string='Hosted Button Color', help='Optional HEX color.')

    @api.depends('code')
    def _compute_view_configuration_fields(self):
        super()._compute_view_configuration_fields()
        providers = self.filtered(lambda p: p.code == const.PROVIDER_CODE)
        providers.update({
            'show_credentials_page': True,
            'show_allow_tokenization': False,
            'show_allow_express_checkout': False,
            'show_pre_msg': True,
            'show_pending_msg': True,
            'show_auth_msg': False,
            'show_done_msg': True,
            'show_cancel_msg': True,
            'require_currency': False,
        })

    def _compute_feature_support_fields(self):
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == const.PROVIDER_CODE).update({
            'support_express_checkout': False,
            'support_manual_capture': False,
            'support_refund': False,
            'support_tokenization': False,
        })

    def _get_default_payment_method_codes(self):
        default_codes = super()._get_default_payment_method_codes()
        if self.code != const.PROVIDER_CODE:
            return default_codes
        # Prevent Odoo from auto-attaching all 100+ coin/network methods on install.
        # The main multicoin hosted method is the only default; individual QR methods
        # stay available for manual activation from the provider settings.
        return {const.MULTICOIN_METHOD_CODE}

    def _get_redirect_form_view(self, is_validation=False):
        self.ensure_one()
        if self.code == const.PROVIDER_CODE:
            return self.env.ref('highriskify_crypto.redirect_form')
        return super()._get_redirect_form_view(is_validation=is_validation)

    def _cryptopaymate_api_base(self):
        self.ensure_one()
        return (self.cryptopaymate_api_base_url or const.API_BASE_URL).strip().rstrip('/')

    def _cryptopaymate_api_bases(self):
        self.ensure_one()
        bases = []
        primary = self._cryptopaymate_api_base()
        if primary:
            bases.append(primary)
        for base in [const.API_BASE_URL] + list(getattr(const, 'API_FALLBACK_BASE_URLS', [])):
            base = (base or '').strip().rstrip('/')
            if base and base not in bases:
                bases.append(base)
        return bases

    def _cryptopaymate_checkout_domain(self):
        self.ensure_one()
        from urllib.parse import urlparse

        raw_domain = (self.cryptopaymate_checkout_domain or const.HOSTED_CHECKOUT_DOMAIN or '').strip()
        if not raw_domain:
            return const.HOSTED_CHECKOUT_DOMAIN

        # Accept either checkoutcrypto.example.com or https://checkoutcrypto.example.com/crypto/hosted.php
        # but store/use only the hostname. This prevents Odoo from accidentally redirecting to the
        # merchant's own website, e.g. community.highriskify.com/crypto/hosted.php.
        parsed = urlparse(raw_domain if '://' in raw_domain else 'https://' + raw_domain)
        domain = (parsed.netloc or parsed.path or '').strip().strip('/')
        domain = domain.split('/')[0].split('?')[0].strip()

        odoo_host = ''
        try:
            odoo_host = (urlparse(self.get_base_url()).netloc or '').lower()
        except Exception:
            odoo_host = ''

        if not domain or '.' not in domain or domain.lower() == odoo_host:
            return const.HOSTED_CHECKOUT_DOMAIN
        return domain

    def _cryptopaymate_wallet_payload(self):
        self.ensure_one()
        payload = {}
        wallet_map = {
            'evm': self.cryptopaymate_wallet_evm,
            'btc': self.cryptopaymate_wallet_btc,
            'bitcoincash': self.cryptopaymate_wallet_bitcoincash,
            'ltc': self.cryptopaymate_wallet_ltc,
            'doge': self.cryptopaymate_wallet_doge,
            'solana': self.cryptopaymate_wallet_solana,
            'trc20': self.cryptopaymate_wallet_trc20,
        }
        for key, wallet in wallet_map.items():
            wallet = (wallet or '').strip()
            if wallet:
                payload[key] = wallet
        return payload


    def _cryptopaymate_get_ticker(self):
        """Return the legacy/default ticker for fallback QR flows.

        Most checkout attempts now use the selected payment.method code. This
        helper is kept for old transactions/databases where a single provider
        ticker may still be configured.
        """
        self.ensure_one()
        ticker = self.cryptopaymate_custom_ticker if self.cryptopaymate_ticker == 'custom' else self.cryptopaymate_ticker
        ticker = (ticker or 'polygon/usdt').strip().strip('/')
        return ticker if ticker and ticker != 'multicoin' else 'polygon/usdt'

    def _cryptopaymate_wallet_for_ticker(self, ticker):
        """Pick the correct payout wallet for an individual coin/network QR method.

        This mirrors the WooCommerce multicoin wallet settings:
        EVM wallet covers Polygon/ERC20/BEP20/Base/Arbitrum/Avalanche/Optimism/etc.;
        BTC/BCH/LTC/DOGE/SOL/TRC20 use their own configured wallet fields.
        """
        self.ensure_one()
        ticker = (ticker or '').strip().lower().strip('/')
        if ticker == 'btc':
            return (self.cryptopaymate_wallet_btc or '').strip()
        if ticker == 'bch':
            return (self.cryptopaymate_wallet_bitcoincash or '').strip()
        if ticker == 'ltc':
            return (self.cryptopaymate_wallet_ltc or '').strip()
        if ticker == 'doge':
            return (self.cryptopaymate_wallet_doge or '').strip()
        if ticker.startswith('sol/') or ticker == 'sol':
            return (self.cryptopaymate_wallet_solana or '').strip()
        if ticker.startswith('trc20/') or ticker == 'trx':
            return (self.cryptopaymate_wallet_trc20 or '').strip()
        # EVM-compatible chains/tokens: polygon, erc20, bep20, base, arbitrum,
        # avax-c, optimism, linea, monad, eth, and any future EVM-style network.
        return (self.cryptopaymate_wallet_evm or self.cryptopaymate_merchant_wallet or '').strip()

    def _cryptopaymate_split_fees(self):
        # Backward-compatible helper for older code paths.
        self.ensure_one()
        fees = {}

        def add(wallet, percent):
            wallet = (wallet or '').strip()
            percent = float(percent or 0.0)
            if wallet and percent > 0:
                fees[wallet] = round(fees.get(wallet, 0.0) + percent, 8)

        add(self.cryptopaymate_merchant_wallet or self.cryptopaymate_wallet_evm, self.cryptopaymate_merchant_percent)
        add(self.cryptopaymate_sub_wallet, self.cryptopaymate_sub_percent)
        add(self.cryptopaymate_platform_wallet, self.cryptopaymate_platform_percent)
        return fees

    @api.constrains(
        'code',
        'state',
        'cryptopaymate_api_base_url',
        'cryptopaymate_checkout_domain',
        'cryptopaymate_wallet_evm',
        'cryptopaymate_wallet_btc',
        'cryptopaymate_wallet_bitcoincash',
        'cryptopaymate_wallet_ltc',
        'cryptopaymate_wallet_doge',
        'cryptopaymate_wallet_solana',
        'cryptopaymate_wallet_trc20',
        'cryptopaymate_confirmations',
    )
    def _check_cryptopaymate_core_settings(self):
        for provider in self.filtered(lambda p: p.code == const.PROVIDER_CODE and p.state != 'disabled'):
            api_base = provider._cryptopaymate_api_base()
            if not re.match(r'^https://[^/]+', api_base):
                raise ValidationError(_('HighRiskify Crypto API Base URL must start with https:// and must not include a path.'))

            if not provider._cryptopaymate_wallet_payload():
                raise ValidationError(_('Please add at least one HighRiskify Crypto payout wallet address before enabling the provider.'))

            if provider.cryptopaymate_confirmations < 1:
                raise ValidationError(_('HighRiskify Crypto confirmations must be at least 1.'))

            checkout_domain = provider._cryptopaymate_checkout_domain()
            if '/' in checkout_domain or ' ' in checkout_domain:
                raise ValidationError(_('Hosted Checkout Domain should be a domain only, for example checkout.highriskify.com.'))
