{
'name': 'HighRiskify Onramp',
'version': '17.0.1.2.5',
'category': 'Accounting/Payment Providers',
'summary': 'Crypto Onramp for Odoo: MoonPay, Transak, Ramp, Coinbase Pay, Revolut, fiat-to-crypto, card-to-crypto, USDC/USDT/BTC hosted checkout, payment links, invoice and website payments.',
'description': """
Crypto Onramp for Odoo - MoonPay, Transak, Ramp, Coinbase Pay, Revolut

HighRiskify Onramp is a hosted checkout and payment redirection integration for Odoo 17. It connects Odoo Ecommerce, Odoo Website, Odoo Invoicing, quotation payment flows, and compatible subscription billing workflows with configured fiat-to-crypto, card-to-crypto, bank transfer, and digital asset purchase checkout services.

The module helps Odoo merchants add a crypto onramp checkout experience for customer payment flows such as buy crypto, buy Bitcoin, buy USDC, buy USDT, crypto checkout, fiat onramp, card to crypto, crypto purchase, hosted checkout, payment links, checkout redirect, checkout routing, and transaction status synchronization.

Main Features:

* Adds HighRiskify Onramp as an Odoo payment provider.
* Supports Odoo Website, Odoo Ecommerce, Odoo Checkout, Odoo Payments, and Odoo Ecommerce Payments workflows.
* Supports Odoo invoice, quotation, customer payment link, and subscription billing flows where applicable.
* Redirects customers to a configured hosted checkout destination.
* Supports hosted checkout, checkout redirection, checkout integration, checkout routing, and customer checkout flows.
* Creates Odoo payment transactions and checkout session references.
* Supports transaction status synchronization, callback/IPN handling, and Odoo transaction synchronization.
* Logs transaction events, checkout updates, and status changes in Odoo order chatter.
* Supports multi-provider routing and regional availability support depending on merchant configuration and provider coverage.
* Includes backend configuration fields for API URL, checkout URL, branding, display text, and operational settings.

Provider and Network Search References:

HighRiskify Onramp can be discovered by merchants searching for Odoo crypto onramp integrations and third-party onramp provider routing terms including MoonPay, Transak, Ramp, Ramp.Network, Coinbase Pay, Coinbase, Banxa, Topper, Simplex, Guardarian, Bitnovo, Robinhood, Revolut, Blockchain.com, Binance Connect, PayPal, Klarna, Interac, iDEAL, UPI, Stripe, article.network, and Sardine.ai. Actual provider availability depends on the configured checkout routing, customer region, merchant setup, and provider-side eligibility.

Coins, Digital Asset, and Checkout Search Terms:

Search keywords covered by this listing include Hosted Checkout, Payment Links, Checkout Redirect, Checkout Integration, Checkout Routing, Multi Provider, Wallet Connect, Usdc, Usdt, Pyusd, ETH, Bitcoin, Btc, Doge, Polygon, Pol, Sol, Solana, Credit card, Card to crypto, Fiat to crypto, Fiat Onramp, Crypto Onramp, Crypto Checkout, Buy Crypto, Buy Bitcoin, Buy USDC, Buy USDT, Crypto Purchase, High risk payments, and No kyc. KYC, verification, limits, fees, regional support, and customer eligibility are controlled by the configured checkout providers; this module does not bypass provider compliance requirements.

Merchant Category Search Terms:

The module listing also includes search terminology used by specialty and high-risk ecommerce merchants, including CBD, Hemp Products, Vape Products, E-Cigarettes, Nicotine Products, Kratom, Supplements, Nutraceuticals, Telehealth, Peptides, Anti-Aging Clinics, Wellness Clinics, Medical Spas (Med Spas), Weight Loss Programs, GLP-1 Clinics, Testosterone Therapy (TRT), Hormone Replacement Therapy (HRT), Research Chemicals, Adult Products, Adult Content, Dating Services, Subscription Services, Membership Programs, Debt Relief, Credit Repair, Forex, Cryptocurrency, Crypto Exchanges, Crypto On-Ramps, Gambling, Sports Betting, Sweepstakes, Firearms Accessories, Ammunition, Precious Metals, Pawn Shops, Smoke Shops, Head Shops, Herbal Products, Alternative Health Products, Travel Clubs, Business Opportunities, Coaching Programs, Ticket Resellers, Multi-Level Marketing (MLM), Drop Shipping, International E-Commerce, Replica Products (usually prohibited), Digital Downloads, Software Licenses, IPTV Services, Debt Collection, High-Risk Merchants, Debt CollectionHigh-Risk Merchants, Restricted Merchant Categories, Specialty Industries, Alternative Commerce Businesses, and High-Risk E-Commerce. Merchant eligibility remains subject to HighRiskify configuration, provider terms, applicable law, Odoo store policies, and compliance review.

Odoo Search References:

HighRiskify, High Riskify, Odoo Onramp, Odoo Crypto, Odoo Ecommerce, Odoo Website, Odoo Checkout, Odoo Payments, Odoo Integration, Odoo Ecommerce Payments, Odoo Crypto Onramp, Odoo Fiat to Crypto, Odoo Buy Crypto, Odoo Digital Asset Checkout, Odoo Hosted Checkout, Odoo Ecommerce Onramp, Odoo Website Onramp, Odoo Checkout Integration, Odoo Checkout Routing, Odoo Transaction Synchronization, Odoo Website Checkout, Odoo Ecommerce Checkout, Odoo Digital Asset Integration, Odoo Checkout Module, Odoo Ecommerce Extension, Odoo Website Extension, Odoo Subscription Integration, Odoo Invoice Integration, Odoo Web3 Integration, Odoo Digital Asset Access, Odoo Crypto Access, and Odoo Buy Crypto Integration.

External Services and Data Handling:

This module connects Odoo with HighRiskify integration services and configured checkout/routing services to support checkout redirection, transaction reference creation, checkout session handling, status synchronization, callback processing, transaction tracking, and related operational functionality.

During normal module operation, limited transaction and order-related information may be exchanged with HighRiskify services so the integration can initiate checkout workflows, receive status updates, assist with transaction tracking, and synchronize the corresponding Odoo records. Data exchanged may include order references, invoice references, transaction references, transaction amounts, currency, selected payment method, payment status, customer information where available, session identifiers, callback notifications, merchant website information, transaction identifiers, and system-generated timestamps.

Availability and Compliance Disclaimer:

Provider availability, regional coverage, payment methods, transaction limits, checkout routing, fees, digital asset purchase options, KYC requirements, merchant category eligibility, restricted category support, and customer eligibility depend on the configured checkout setup, customer location, provider coverage, merchant configuration, and provider-side requirements. This module provides the Odoo integration layer for checkout redirection, hosted checkout workflow, and transaction synchronization.
""",
'author': 'HighRiskify',
'website': 'https://highriskify.com',
'support': 'info@highriskify.com',
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
