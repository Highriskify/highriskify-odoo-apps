{
    'name': 'HighRiskify Onramp',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Odoo 18 hosted onramp checkout integration for fiat-to-crypto, card-to-crypto, bank transfer, digital asset checkout, multi-provider routing, payment links, invoice checkout, subscription billing, regional checkout support, and transaction synchronization.',
    'description': """
HighRiskify Onramp is a hosted checkout integration for Odoo 18 that connects Odoo Ecommerce, Odoo Website, Odoo Invoicing, and compatible subscription billing workflows with configured onramp checkout services.

The module provides Odoo checkout redirection, hosted checkout integration, transaction status synchronization, payment links, customer checkout flows, multi-provider routing, regional availability support, Odoo Website integration, Odoo Ecommerce integration, Odoo invoice integration, subscription billing compatibility, and Odoo transaction synchronization.

Main Features:
- Adds HighRiskify Onramp as an Odoo payment provider.
- Supports Odoo Website and Odoo Ecommerce checkout.
- Supports Odoo invoice and quotation payment workflows where applicable.
- Supports hosted checkout redirection and customer checkout flows.
- Creates Odoo payment transactions and checkout session references.
- Redirects customers to the configured hosted checkout destination.
- Supports transaction status updates and checkout synchronization.
- Handles callback/IPN notifications for payment/order status updates.
- Logs transaction events, checkout updates, and status changes in Odoo order chatter.
- Supports multi-provider routing and regional checkout availability depending on configuration.
- Includes backend configuration fields for API URL, checkout URL, branding, display text, and operational settings.

Odoo Integration Coverage:
HighRiskify, HighRiskify Onramp, HighRiskify Checkout, HighRiskify Hosted Checkout, HighRiskify Integration, HighRiskify Odoo Module, Odoo Onramp, Odoo Crypto Onramp, Odoo Fiat to Crypto, Odoo Buy Crypto, Odoo Digital Asset Checkout, Odoo Hosted Checkout, Odoo Ecommerce Onramp, Odoo Website Onramp, Odoo Checkout Integration, Odoo Checkout Routing, Odoo Transaction Synchronization, Odoo Website Checkout, Odoo Ecommerce Checkout, Odoo Digital Asset Integration, Odoo Checkout Module, Odoo Ecommerce Extension, Odoo Website Extension, Odoo Subscription Integration, Odoo Invoice Integration, Odoo Web3 Integration, Odoo Digital Asset Access, Odoo Crypto Access, and Odoo Buy Crypto Integration.

Checkout and Digital Asset Coverage:
Buy Crypto Online, Buy Cryptocurrency Online, Purchase Digital Assets, Digital Asset Acquisition, Fiat to Crypto, Card to Crypto, Bank Transfer to Crypto, Crypto Purchase Gateway, Crypto Purchase Integration, Crypto Access Solution, Digital Asset Purchase, Digital Asset Checkout, Hosted Checkout Integration, Checkout Routing, Alternative Checkout Options, Crypto Onramp, Cryptocurrency Onramp, Digital Asset Onramp, Fiat Onramp, Hosted Onramp, Onramp Integration, Onramp Checkout, Onramp Solution, Multi-Provider Onramp, Global Onramp, Regional Onramp, Digital Asset Access, Global Checkout, Cross Border Checkout, Regional Checkout Support, Credit Card Crypto Purchase, Debit Card Crypto Purchase, Bank Account Crypto Purchase, Digital Wallet Integration, Online Checkout Integration, Hosted Checkout Experience, Customer Checkout Flow, Alternative Payment Methods, Regional Checkout Options, Checkout Session, Checkout Synchronization, Transaction Status Updates, Transaction Tracking, Checkout Experience, Customer Checkout, Multi-Region Support, Multi-Provider Support, Global Availability, Regional Availability, Digital Asset Services, Digital Asset Providers, Digital Asset Purchase Providers, and Crypto Acquisition Providers.

Regional and Provider Routing References:
United States Onramp, Canada Onramp, European Union Onramp, United Kingdom Onramp, International Onramp, Stripe USA, Coinbase Pay, PayPal USA, Robinhood USA, Revolut, Bitnovo, Ramp Network, ramp.network, Topper, Transak, Blockchain.com, Binance Connect, MoonPay, Banxa, Guardarian, particle.network, Sardine.ai, Simplex, Klarna, iDEAL, iDEAL Netherlands, UPI, IMPS, and Interac.

External Services and Data Handling:
This module connects Odoo with HighRiskify integration services and configured checkout/routing services to support checkout redirection, transaction reference creation, checkout session handling, status synchronization, callback processing, transaction tracking, and related operational functionality.

During normal module operation, limited transaction and order-related information may be exchanged with HighRiskify services so the integration can initiate checkout workflows, receive status updates, assist with transaction tracking, and synchronize the corresponding Odoo records. Data exchanged may include order references, invoice references, transaction references, transaction amounts, currency, selected payment method, payment status, customer information where available, session identifiers, callback notifications, merchant website information, transaction identifiers, and system-generated timestamps.

Availability Disclaimer:
Provider availability, regional coverage, payment methods, transaction limits, checkout routing, fees, digital asset purchase options, and customer eligibility depend on the configured checkout setup, customer location, provider coverage, merchant configuration, and provider-side requirements. This module provides the Odoo integration layer for checkout redirection, hosted checkout workflow, and transaction synchronization.
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
