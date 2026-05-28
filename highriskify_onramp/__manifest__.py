{
    'name': 'HighRiskify Onramp',
    'version': '17.0.1.2.2',
    'category': 'Accounting/Payment Providers',
    'summary': 'Accept onramp/card payments through HighRiskify hosted checkout with callback order tracking.',
    'description': """
HighRiskify Onramp payment provider for Odoo 17 Community and Odoo Online-compatible deployments.

Flow:
- Converts non-USD order totals through the gateway conversion endpoint.
- Creates a temporary onramp wallet for the Odoo payment transaction.
- Redirects the customer to the hosted HighRiskify checkout page.
- Processes gateway callbacks/IPNs, logs order chatter, and confirms sale orders only after confirmed payment.
    """,
    'author': 'HighRiskify',
    'website': 'https://highriskify.com',
    'license': 'LGPL-3',
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
            'payment_highriskify_onramp/static/src/css/highriskify_payment_logos.css',
            'payment_highriskify_onramp/static/src/js/highriskify_payment_logos.js',
        ],
        'web.assets_backend': [
            'payment_highriskify_onramp/static/src/css/highriskify_backend_logo.css',
            'payment_highriskify_onramp/static/src/js/highriskify_backend_logo.js',
        ],
    },
    'installable': True,
    'application': False,
}
