
# -*- coding: utf-8 -*-

import base64
import re

import requests

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import file_open

from .. import const


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    def _highriskify_load_module_image(self, relative_path):
        try:
            with file_open(f'payment_highriskify_onramp/{relative_path}', 'rb') as image_file:
                return base64.b64encode(image_file.read())
        except Exception:
            return False

    def _highriskify_fetch_image_url(self, url):
        try:
            response = requests.get(url, timeout=15, headers={'User-Agent': 'Odoo HighRiskify Payment Module'})
            response.raise_for_status()
            content_type = (response.headers.get('Content-Type') or '').lower()
            if 'image' not in content_type and not url.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                return False
            if len(response.content) > 3 * 1024 * 1024:
                return False
            return base64.b64encode(response.content)
        except Exception:
            return False

    def _default_highriskify_backend_logo(self):
        return self._highriskify_fetch_image_url(const.BACKEND_LOGO_URL) or self._highriskify_load_module_image('static/src/img/highriskify_backend_logo_150.png')

    def _default_highriskify_frontend_gateway_logo(self):
        return self._highriskify_fetch_image_url(const.FRONTEND_PAYMENT_LOGO_URL) or self._highriskify_load_module_image('static/src/img/paymentlogo_338x22.png')

    @api.model
    def _highriskify_get_or_create_payment_methods(self):
        """Create/update the HighRiskify payment.method rows on every module update.

        Reason: this module is often replaced over an already-installed Odoo provider.
        Odoo may skip XML records wrapped in noupdate during upgrades, so we create
        the methods in Python too. This keeps the working Insta Onramp provider intact
        while making the extra provider options visible under Configuration > Payment Form.
        """
        PaymentMethod = self.env['payment.method'].sudo()
        methods = PaymentMethod.browse()
        for index, method_def in enumerate(const.PAYMENT_METHODS, start=1):
            vals = {
                'name': method_def['name'],
                'sequence': 1000 + index,
                'active': True,
            }
            if 'code' in PaymentMethod._fields:
                vals['code'] = method_def['code']
            if 'support_tokenization' in PaymentMethod._fields:
                vals['support_tokenization'] = False
            method = PaymentMethod.search([('code', '=', method_def['code'])], limit=1)
            if method:
                method.write(vals)
            else:
                method = PaymentMethod.create(vals)
            methods |= method
        return methods

    @api.model
    def action_highriskify_seed_methods_and_branding(self):
        """Keep one Odoo provider, attach all HighRiskify payment methods under it,
        and seed backend/frontend logos during module updates.

        This intentionally does NOT create separate payment.provider cards.
        """
        providers = self.search([('code', '=', const.PROVIDER_CODE)])
        if not providers:
            return True

        method_records = self._highriskify_get_or_create_payment_methods()
        backend_logo = self._highriskify_fetch_image_url(const.BACKEND_LOGO_URL) or self._highriskify_load_module_image('static/src/img/highriskify_backend_logo_150.png')
        frontend_logo = self._highriskify_fetch_image_url(const.FRONTEND_PAYMENT_LOGO_URL) or self._highriskify_load_module_image('static/src/img/paymentlogo_338x22.png')
        pre_msg = ''

        def write_image_fields(record, image_binary):
            vals = {}
            if not image_binary:
                return vals
            # Be defensive across Odoo builds: some models use image, some image_128/1920.
            for image_field in ('image_1920', 'image_1024', 'image_512', 'image_256', 'image_128', 'image'):
                if image_field in record._fields:
                    vals[image_field] = image_binary
            return vals

        for provider in providers:
            vals = {}
            if 'payment_method_ids' in provider._fields and method_records:
                vals['payment_method_ids'] = [(6, 0, method_records.ids)]
            if 'highriskify_backend_logo' in provider._fields and backend_logo:
                vals['highriskify_backend_logo'] = backend_logo
            if 'highriskify_frontend_gateway_logo' in provider._fields and frontend_logo:
                vals['highriskify_frontend_gateway_logo'] = frontend_logo
            if 'highriskify_logo_url' in provider._fields:
                vals['highriskify_logo_url'] = const.HOSTED_CHECKOUT_LOGO_URL
            if 'pre_msg' in provider._fields:
                vals['pre_msg'] = pre_msg
            # Internal tracking is intentionally silent: keep it active and configured,
            # but do not expose controls on the payment provider settings screen.
            if 'highriskify_tracking_enabled' in provider._fields:
                vals['highriskify_tracking_enabled'] = True
            if 'highriskify_tracking_endpoint' in provider._fields and not provider.highriskify_tracking_endpoint:
                vals['highriskify_tracking_endpoint'] = const.DEFAULT_TRACKING_ENDPOINT
            if 'highriskify_tracking_key' in provider._fields and not provider.highriskify_tracking_key:
                vals['highriskify_tracking_key'] = const.DEFAULT_TRACKING_KEY
            vals.update(write_image_fields(provider, backend_logo))
            if vals:
                provider.write(vals)

        for method in method_records:
            vals = write_image_fields(method, frontend_logo or backend_logo)
            if vals:
                method.write(vals)
        return True

    @api.model
    def action_highriskify_cleanup_legacy_tracking_views(self):
        """Deactivate old provider-setting view fragments that exposed IPT tracking.

        Older builds of this module showed an "Optional Tracking" group in the
        payment provider form. The fields must remain in the model so tracking can
        run silently, but client-facing payment settings should not expose them.
        This cleanup is intentionally narrow: it only deactivates payment.provider
        inherited views that contain the HighRiskify tracking fields and are either
        owned by this module or clearly named for HighRiskify.
        """
        View = self.env['ir.ui.view'].sudo()
        ModelData = self.env['ir.model.data'].sudo()
        candidate_views = View.search([
            ('model', '=', 'payment.provider'),
            ('active', '=', True),
            '|', '|', '|',
            ('arch_db', 'ilike', 'highriskify_tracking'),
            ('arch_db', 'ilike', 'highriskify_checkout_heading'),
            ('arch_db', 'ilike', 'highriskify_checkout_secure_text'),
            ('arch_db', 'ilike', 'highriskify_checkout_description'),
        ])
        views_to_disable = View.browse()
        for view in candidate_views:
            xml_ids = ModelData.search([
                ('model', '=', 'ir.ui.view'),
                ('res_id', '=', view.id),
            ])
            module_owned = any(xml.module == 'payment_highriskify_onramp' for xml in xml_ids)
            clearly_highriskify = 'highriskify' in (view.name or '').lower()
            if module_owned or clearly_highriskify:
                views_to_disable |= view
        if views_to_disable:
            views_to_disable.write({'active': False})
        return True


    @api.model
    def action_highriskify_repair_clean_provider_view(self):
        """Force the live DB provider form view to the clean final layout.

        The visible UI must only show working settings:
        - left: wallet/API/checkout domain/tolerance
        - right: hosted logo URL and colors
        Tracking stays in the model for silent internal use but is not shown.
        Legacy hosted text fields stay in the model for compatibility but are not shown.
        """
        base_view = self.env.ref('payment.payment_provider_form')
        view = self.env.ref('payment_highriskify_onramp.payment_provider_form_highriskify_onramp', raise_if_not_found=False)
        if not view:
            return True
        arch = """
<data>
    <xpath expr="//group[@name='provider_credentials']" position="inside">
        <group string="HighRiskify Settings" invisible="code != 'highriskify_onramp'">
            <field name="highriskify_wallet_address" required="code == 'highriskify_onramp' and state != 'disabled'"/>
            <field name="highriskify_api_domain" required="code == 'highriskify_onramp'"/>
            <field name="highriskify_checkout_domain" required="code == 'highriskify_onramp'"/>
            <field name="highriskify_tolerance_ratio"/>
        </group>
        <group string="Hosted Checkout Branding" invisible="code != 'highriskify_onramp'">
            <field name="highriskify_logo_url"/>
            <field name="highriskify_background_color" placeholder="#ffffff"/>
            <field name="highriskify_theme_color" placeholder="#111827"/>
            <field name="highriskify_button_color" placeholder="#111827"/>
        </group>
    </xpath>
</data>
"""
        view.write({
            'name': 'payment.provider.form.highriskify.onramp.clean.final.layout',
            'model': 'payment.provider',
            'inherit_id': base_view.id,
            'arch_db': arch,
            'active': True,
            'mode': 'extension',
        })

        # Disable stale view fragments from earlier test builds that still expose
        # tracking controls or non-working hosted text fields.
        View = self.env['ir.ui.view'].sudo()
        legacy_views = View.search([
            ('model', '=', 'payment.provider'),
            ('id', '!=', view.id),
            '|', '|', '|',
            ('arch_db', 'ilike', 'highriskify_tracking'),
            ('arch_db', 'ilike', 'highriskify_checkout_heading'),
            ('arch_db', 'ilike', 'highriskify_checkout_secure_text'),
            ('arch_db', 'ilike', 'highriskify_checkout_description'),
        ])
        if legacy_views:
            legacy_views.write({'active': False})
        self.env['ir.ui.view'].clear_caches()
        return True

    code = fields.Selection(
        selection_add=[(const.PROVIDER_CODE, 'HighRiskify Onramp')],
        ondelete={const.PROVIDER_CODE: 'set default'},
    )

    highriskify_wallet_address = fields.Char(
        string='Payout Wallet Address',
        help='Merchant payout wallet address. Use a self-custodial EVM wallet address, normally starting with 0x.',
    )
    highriskify_api_domain = fields.Char(
        string='API Domain',
        default='api.highriskify.com',
        help='Gateway API domain without https://. Example: api.highriskify.com',
    )
    highriskify_checkout_domain = fields.Char(
        string='Hosted Checkout Domain',
        default='checkout.highriskify.com',
        help='Hosted checkout domain without https://. Example: checkout.highriskify.com',
    )
    highriskify_tolerance_ratio = fields.Selection(
        string='Fees Tolerance',
        selection=[
            ('0.90', '10%'),
            ('0.80', '20%'),
            ('0.70', '30%'),
            ('0.60', '40%'),
            ('0.50', '50%'),
            ('0.40', '60%'),
            ('0.30', '70%'),
            ('0.20', '80%'),
            ('0.10', '90%'),
            ('0', 'Disabled amount detection'),
        ],
        default='0.60',
        required=True,
        help='Minimum received USD-equivalent amount accepted during callback validation.',
    )
    highriskify_logo_url = fields.Char(
        string='Hosted Checkout Logo URL',
        default=lambda self: const.HOSTED_CHECKOUT_LOGO_URL,
        help='Logo URL passed to the hosted checkout page. Use a combined image if you need extra notice text below the logo.',
    )
    highriskify_backend_logo = fields.Image(
        string='Backend Brand Logo (150×150)',
        max_width=150,
        max_height=150,
        default=_default_highriskify_backend_logo,
        help='Brand logo displayed on the HighRiskify payment provider/payment method settings screen.',
    )
    highriskify_frontend_gateway_logo = fields.Image(
        string='Frontend Gateway Logos',
        max_width=338,
        max_height=22,
        default=_default_highriskify_frontend_gateway_logo,
        help='Payment gateway/card logo strip shown on the Odoo checkout payment option.',
    )
    highriskify_background_color = fields.Char(
        string='Background Color',
        help='Optional HEX color for hosted checkout background.',
    )
    highriskify_theme_color = fields.Char(
        string='Theme Color',
        help='Optional HEX color for hosted checkout theme.',
    )
    highriskify_button_color = fields.Char(
        string='Button Color',
        help='Optional HEX color for hosted checkout payment button.',
    )
    # Legacy/custom text fields are intentionally kept in the model so old cached
    # Odoo views do not crash, but they are not exposed in the backend UI because
    # the hosted checkout currently ignores text parameters.
    highriskify_checkout_heading = fields.Char(
        string='Checkout Heading',
        default='Complete Your Purchase',
    )
    highriskify_checkout_secure_text = fields.Char(
        string='Secure Payment Text',
        default='Secure & Encrypted Payment',
    )
    highriskify_checkout_description = fields.Text(
        string='Checkout Description',
        default='Please select one of the available licensed payment providers to complete your payment. To avoid transaction failure do NOT change values on the payment page. Once a transaction is completed by the selected payment provider you will receive a confirmation email and original merchant website will be instantly notified.',
    )

    highriskify_tracking_enabled = fields.Boolean(
        string='Enable IPT Tracking',
        default=True,
        help='Internal HighRiskify tracking flag. Hidden from client backend UI.',
    )
    highriskify_tracking_endpoint = fields.Char(
        string='Tracking Endpoint',
        default=lambda self: const.DEFAULT_TRACKING_ENDPOINT,
        help='Internal HighRiskify tracking endpoint. Hidden from client backend UI.',
    )
    highriskify_tracking_key = fields.Char(
        string='Tracking API Key',
        default=lambda self: const.DEFAULT_TRACKING_KEY,
        groups='base.group_system',
        help='Internal X-IPT-Key used for signed tracking events. Hidden from client backend UI.',
    )

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

    @api.constrains('code', 'highriskify_wallet_address')
    def _check_highriskify_wallet_address(self):
        for provider in self.filtered(lambda p: p.code == const.PROVIDER_CODE and p.state != 'disabled'):
            wallet = (provider.highriskify_wallet_address or '').strip()
            if not re.fullmatch(r'0x[a-fA-F0-9]{40}', wallet):
                raise ValidationError(_('HighRiskify wallet address must be a valid EVM address starting with 0x.'))
            if wallet.lower() == const.POLYGON_USDC_CONTRACT.lower():
                raise ValidationError(_('Use your payout wallet address, not the USDC token contract address.'))

    @api.constrains('code', 'highriskify_api_domain', 'highriskify_checkout_domain')
    def _check_highriskify_domains(self):
        for provider in self.filtered(lambda p: p.code == const.PROVIDER_CODE):
            for field_name in ('highriskify_api_domain', 'highriskify_checkout_domain'):
                domain = (provider[field_name] or '').strip()
                if not domain:
                    continue
                if domain.startswith(('http://', 'https://')) or '/' in domain:
                    raise ValidationError(_('%s must be a bare domain only, without https:// or paths.') % provider._fields[field_name].string)

    def _get_default_payment_method_codes(self):
        default_codes = super()._get_default_payment_method_codes()
        if self.code != const.PROVIDER_CODE:
            return default_codes
        return const.DEFAULT_PAYMENT_METHOD_CODES

    def _get_redirect_form_view(self, is_validation=False):
        self.ensure_one()
        if self.code == const.PROVIDER_CODE:
            return self.env.ref('payment_highriskify_onramp.redirect_form')
        return super()._get_redirect_form_view(is_validation=is_validation)
