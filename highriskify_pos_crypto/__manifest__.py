# -*- coding: utf-8 -*-
{
    'name': 'HighRiskify POS Crypto',
    'version': '17.0.1.1.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Accept cryptocurrency payments in Odoo Point of Sale with hosted crypto checkout and status synchronization.',
    'description': """
HighRiskify POS Crypto adds cryptocurrency payment support to Odoo Point of Sale.

The module lets POS cashiers start a hosted crypto checkout or QR payment request from the Odoo POS payment screen. Customers can complete payment using supported cryptocurrencies and networks, while Odoo receives payment status updates and synchronizes the POS payment line after confirmation.

Main features:
- Adds HighRiskify POS Crypto as an Odoo POS payment terminal option.
- Supports hosted crypto checkout and QR-code payment request workflows.
- Supports non-custodial wallet payout configuration where crypto can be forwarded to merchant wallets after confirmation.
- Supports multicoin and multi-chain payment workflows depending on configured wallet/network support.
- Supports Bitcoin, Ethereum, USDT, USDC, Solana, Litecoin, Dogecoin, Bitcoin Cash and other supported crypto assets/tokens through the configured checkout service.
- Creates unique transaction references and payment sessions from POS orders.
- Receives callback/status updates and marks the POS payment line only after confirmed payment.
- Includes backend configuration for API endpoint, hosted checkout domain, payout wallets, display settings, fallback QR mode and operational tracking settings.

External services and data handling:
This module connects Odoo POS with HighRiskify integration services to create checkout sessions, generate payment requests, process callbacks, synchronize payment status, and support operational transaction tracking. Limited transaction/order-related data may be exchanged for these functions, including POS reference, amount, currency, selected payment method, customer email where available, wallet/session information, callback status, transaction identifiers, merchant website information, and timestamps.
    """,
    'author': 'HighRiskify',
    'website': 'https://highriskify.com',
    'support': 'support@highriskify.com',
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_payment_method_views.xml',
        'views/highriskify_pos_crypto_transaction_views.xml',
        'data/default_pos_payment_method.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'highriskify_pos_crypto/static/src/app/payment_highriskify_pos_crypto.js',
            'highriskify_pos_crypto/static/src/overrides/models/models.js',
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
