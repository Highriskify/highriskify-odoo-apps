{
    'name': 'HighRiskify Crypto',
    'version': '17.0.2.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Hosted non-custodial crypto checkout integration for Odoo eCommerce and invoices.',
    'description': """
HighRiskify Crypto payment provider for Odoo 17.

This module connects Odoo with HighRiskify hosted crypto checkout services. It allows merchants to configure payout wallets, redirect customers to a crypto checkout experience, display payment amount/address/QR information, receive payment notifications, and synchronize Odoo transactions, orders, quotations, and invoices after confirmed payment updates.

Key capabilities:
- Hosted crypto checkout integration for Odoo Website/eCommerce.
- Supports Bitcoin, Ethereum, USDC, USDT, Solana, Litecoin, Dogecoin, Bitcoin Cash and many other major cryptocurrencies/tokens depending on configured network support.
- Non-custodial workflow where merchant payout wallets are configured in Odoo and supported received funds are forwarded according to the configured checkout workflow.
- Unique receiving/payment session references for order-level tracking and payment detection.
- QR code and wallet-address based customer payment flow.
- Callback/webhook status synchronization with Odoo payment transactions and related records.
- Backend configuration for API endpoint, hosted checkout domain, payout wallets, branding, and operational settings.
- Only the main multicoin hosted method is attached to the provider by default; individual coin methods remain available for administrators to enable manually if needed.

External services and data handling:
This module connects to HighRiskify payment infrastructure and related operational tracking endpoints to create checkout/payment sessions, monitor transaction status, process callback notifications, and synchronize Odoo records. Limited transaction and order-related information may be exchanged, including order references, invoice references, transaction amounts, currency, selected crypto/network, customer information where available, wallet/session identifiers, callback notifications, transaction identifiers, merchant website information, and system-generated timestamps.
    """,
    'author': 'HighRiskify',
    'website': 'https://highriskify.com',
    'support': 'support@highriskify.com',
    'license': 'LGPL-3',
    'depends': ['payment', 'website_sale'],
    'data': [
        'data/payment_method_data.xml',
        'views/payment_cryptopaymate_templates.xml',
        'views/payment_provider_views.xml',
        'data/payment_provider_data.xml',
        'data/cryptopaymate_seed_data.xml',
    ],
    'images': [
        'static/description/main_screenshot.png',
        'static/description/backend_settings.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
