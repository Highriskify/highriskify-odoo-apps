{
    'name': 'HighRiskify Onramp',
    'version': '17.0.1.2.3',
    'category': 'Accounting/Payment Providers',
    'summary': 'Accept onramp/card payments through HighRiskify hosted checkout with callback order tracking.',
    'description': """
HighRiskify Onramp payment provider for Odoo 17 Community.

HighRiskify Onramp allows Odoo website customers to pay through a secure hosted HighRiskify checkout flow. The module creates the payment transaction in Odoo, redirects the customer to the HighRiskify hosted checkout page, and processes payment callbacks to update the related Odoo order.

Main Features:
- Adds HighRiskify Onramp as an Odoo payment provider.
- Supports Odoo Website/eCommerce checkout.
- Redirects customers to hosted HighRiskify checkout.
- Converts non-USD order totals through the configured gateway conversion endpoint.
- Creates a temporary onramp wallet/payment session for each Odoo transaction.
- Handles gateway callbacks/IPNs.
- Logs payment updates in the order chatter.
- Confirms sale orders only after confirmed payment.
- Includes backend configuration fields for API URL, checkout URL, branding, and tracking settings.

External Services:
This module connects to HighRiskify payment infrastructure and related tracking endpoints to create payment sessions, redirect customers, process payment callbacks, and update payment/order status.
    """,
    'author': 'HighRiskify',
    'website': 'https://highriskify.com',
    'support': 'support@highriskify.com',
    'license': 'OPL-1',
    'depends': ['payment', 'website_sale'],
    'data': [
        'data/payment_method_data.xml',
        'views/payment_highriskify_templates.xml',
        'views/payment_provider_views.xml',
        'data/payment_provider_data.xml',
        'data/highriskify_methods_branding_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'highriskify_onramp/static/src/css/highriskify_payment_logos.css',
            'highriskify_onramp/static/src/js/highriskify_payment_logos.js',
        ],
        'web.assets_backend': [
            'highriskify_onramp/static/src/css/highriskify_backend_logo.css',
            'highriskify_onramp/static/src/js/highriskify_backend_logo.js',
        ],
    },
    'images': [
        'static/description/main_screenshot.png',
        'static/description/backend_settings.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
