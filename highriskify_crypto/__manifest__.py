{
    'name': 'HighRiskify Crypto',
    'version': '18.0.2.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Odoo 18 crypto payment gateway for eCommerce, website checkout, invoices, payment links, Bitcoin, Ethereum, USDT, USDC, stablecoins, QR code payments, hosted crypto checkout, multi-chain blockchain payments, webhook synchronization, and non-custodial wallet settlement.',
    'description': """
HighRiskify Crypto is a hosted non-custodial crypto payment gateway integration for Odoo 18. It connects Odoo Ecommerce, Odoo Website, Odoo Invoicing, and compatible payment workflows with HighRiskify hosted crypto checkout services.

This module allows merchants to configure payout wallets, redirect customers to a crypto checkout experience, display payment amount, receiving address, and QR code information, receive payment notifications, and synchronize Odoo transactions, orders, quotations, and invoices after confirmed payment updates.

Main Capabilities:
- Adds HighRiskify Crypto as an Odoo payment provider.
- Supports Odoo Website crypto payments and Odoo Ecommerce crypto checkout.
- Supports Odoo invoice payment workflows where applicable.
- Supports hosted crypto checkout, hosted payment pages, payment links, crypto invoice payments, and payment button workflows.
- Supports QR code crypto payments, wallet-address based checkout, and customer wallet payment flows.
- Supports webhook/callback synchronization for transaction monitoring and Odoo payment status updates.
- Supports non-custodial crypto transaction workflows where merchant payout wallets are configured in Odoo.
- Supports multi-currency crypto checkout and multi-chain payment workflows depending on configured network availability.
- Supports fast settlement and instant payout routing according to the configured checkout workflow.
- Supports backend configuration for API endpoint, hosted checkout domain, payout wallets, branding, display text, and operational settings.
- Only the main multicoin hosted method is attached to the provider by default; individual coin methods remain available for administrators to enable manually if needed.

Odoo Crypto Payment Coverage:
HighRiskify Crypto can be used for Odoo Crypto Payment Gateway, Odoo Ecommerce Crypto Payments, Odoo Website Crypto Payments, Odoo Online Store Crypto Payments, Odoo Cryptocurrency Payments, Odoo Bitcoin Payments, Odoo Ethereum Payments, Odoo Stablecoin Payments, Odoo USDC Payments, Odoo USDT Payments, Odoo Blockchain Payments, Odoo Crypto Checkout, Odoo Crypto Invoicing, Odoo Crypto Payment Integration, Odoo Alternative Payment Methods, Odoo Web3 Payments, Odoo Hosted Crypto Checkout, Odoo QR Code Crypto Payments, Odoo Wallet Payments, Odoo Wallet Connect Payments, Odoo Crypto Invoice Payments, Odoo Bitcoin Invoicing, Odoo USDC Invoice Payments, Odoo USDT Invoice Payments, Odoo Ecommerce Crypto Checkout, Odoo Website Crypto Checkout, Odoo Online Store Crypto Checkout, Odoo Crypto Payment Button, Odoo Crypto Payment Link, Odoo Payment Links, Odoo Subscription Billing, Odoo Recurring Payments, Odoo Invoice Payments, Odoo Ecommerce Payment Gateway, Odoo Merchant Gateway, and Odoo Crypto Merchant Account workflows.

Accepted Crypto and Network References:
Supported coin, token, and network references may include Bitcoin, BTC, Bitcoin Cash, BCH, Litecoin, LTC, Dogecoin, DOGE, Ethereum, ETH, Solana, SOL, Avalanche, AVAX, Tron, TRX, BNB Smart Chain, BNB, BEP-20, ERC-20, TRC-20, Arbitrum, Avalanche Network, Polygon Network, Solana Network, Bitcoin Network, Ethereum Network, 1INCH, Cardano, ADA, Bitcoin BEP20, BTCB, PancakeSwap, CAKE, DAI, PHPt, Shiba Inu, SHIB, USD Coin, USDC, Tether, USDT, XRP, ARB, Chainlink, LINK, Ondo Finance, ONDO, Pepe, PEPE, Polygon, POL, Coinbase Wrapped Bitcoin, cbBTC, PayPal USD, PYUSD, World Liberty Financial USD, USD1, TrueUSD, TUSD, EURC, Wrapped Bitcoin, WBTC, Wrapped Ethereum, WETH, and other configured cryptocurrencies, stablecoins, tokens, and digital assets where available.

Crypto Checkout and Payment Workflows:
The module supports crypto checkout for Odoo Ecommerce, cryptocurrency payments for online stores, Bitcoin payments for Odoo websites, Ethereum payments for Odoo websites, USDC payments for Odoo websites, USDT payments for Odoo websites, stablecoin checkout for Odoo websites, blockchain payments for Odoo websites, Odoo online store stablecoin payments, crypto merchant gateway workflows, crypto processing, crypto transactions, crypto settlement, digital currency payments, global payments, international payments, borderless payments, hosted crypto checkout, QR code crypto payments, wallet payments, crypto invoice payments, payment link generator workflows, invoice payment links, invoice payment buttons, automated invoice collection, crypto accounts receivable, digital invoice payments, and blockchain invoicing.

Stablecoin, Multi-Chain, and Blockchain Coverage:
This integration is suitable for multi-chain payments, blockchain payments, stablecoin payments, cryptocurrency payments, digital asset payments, multi-chain crypto gateway workflows, multi-chain stablecoin payments, self-custody payments, non-custodial crypto payments, crypto API integration, Odoo payment API workflows, crypto webhook integration, crypto transaction monitoring, secure crypto payments for ecommerce, secure blockchain payment gateway workflows, multi-currency crypto gateway use cases, low fee payment gateway workflows, reduced payment processing cost workflows, no-chargeback payment flows, instant payment settlement, fast settlement payments, global payment acceptance, international payments, borderless payments, alternative payment methods, crypto merchant processing, digital asset payments, blockchain payment gateway workflows, crypto ecommerce solution workflows, and Web3 ecommerce payments.

Invoice, Subscription, and Recurring Payment Coverage:
HighRiskify Crypto may be used with compatible Odoo flows for crypto invoice payments, Bitcoin invoice payment solution workflows, cryptocurrency invoice payments, crypto invoicing software, invoice automation with crypto, accepting Ethereum for invoices, accepting USDC for invoices, accepting USDT for invoices, stablecoin payments, blockchain payments, crypto subscription payments, recurring crypto payments, subscription crypto billing, stablecoin subscription payments, recurring USDC payments, recurring USDT payments, automated crypto billing, and automated invoice collection where supported by the configured Odoo workflow and checkout setup.

Customer Payment Flow:
When a customer selects HighRiskify Crypto during checkout, the module prepares the Odoo payment transaction and redirects the customer to the configured hosted crypto checkout experience. The customer may be shown the crypto amount, receiving address, and QR code. A unique payment session or receiving reference can be used for order-level tracking and payment detection. After payment confirmation, callback or webhook notifications synchronize the Odoo payment transaction and related order, quotation, or invoice records.

External Services and Data Handling:
This module connects to HighRiskify payment infrastructure and related operational tracking endpoints to create checkout/payment sessions, monitor transaction status, process callback notifications, and synchronize Odoo records. Limited transaction and order-related information may be exchanged, including order references, invoice references, transaction amounts, currency, selected crypto asset or network, customer information where available, wallet/session identifiers, callback notifications, transaction identifiers, merchant website information, and system-generated timestamps.

Availability Disclaimer:
Availability of cryptocurrencies, stablecoins, networks, hosted crypto checkout flows, QR code checkout, payment links, invoice payments, subscription billing, transaction monitoring, settlement routing, fees, limits, and customer eligibility depends on the configured HighRiskify crypto gateway settings, merchant wallet configuration, customer location, supported network availability, and provider-side requirements.
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
