# -*- coding: utf-8 -*-

{
'name': 'HighRiskify POS Crypto',
'version': '19.0.1.0.0',
'category': 'Sales/Point of Sale',
'summary': 'Odoo POS crypto payment gateway for Bitcoin, Ethereum, USDT, USDC, stablecoins, QR code payments, retail checkout, restaurant checkout, mobile POS, hosted crypto checkout, multi-chain blockchain payments, webhook synchronization, and non-custodial wallet settlement.',
'description': """
HighRiskify POS Crypto adds cryptocurrency payment support to Odoo Point of Sale.

The module connects Odoo POS with HighRiskify hosted crypto checkout services, allowing POS cashiers to start a crypto payment request from the Odoo POS payment screen. Customers can complete payment using supported cryptocurrencies, stablecoins, digital assets, wallet payments, QR code payments, and blockchain payment workflows depending on the configured checkout setup and network availability.

Main Capabilities:

* Adds HighRiskify POS Crypto as an Odoo POS payment terminal option.
* Supports Odoo POS crypto payments and Odoo Point of Sale cryptocurrency checkout.
* Supports hosted crypto checkout and QR code payment request workflows from the POS payment screen.
* Supports retail crypto checkout, restaurant crypto checkout, store crypto checkout, mobile POS crypto payments, smartphone POS crypto payments, Android POS crypto payments, tablet POS crypto payments, touchscreen POS crypto payments, and self-checkout crypto payment workflows.
* Supports non-custodial wallet payout configuration where merchant payout wallets can be configured in Odoo.
* Supports multicoin, stablecoin, and multi-chain payment workflows depending on configured wallet and network support.
* Supports Bitcoin, BTC, Bitcoin Cash, BCH, Litecoin, LTC, Dogecoin, DOGE, Ethereum, ETH, Solana, SOL, Avalanche, AVAX, Tron, TRX, BNB Smart Chain, BEP-20, ERC-20, TRC-20, Arbitrum, Polygon, XRP wrapped assets, USDT, USDC, and other supported crypto assets, stablecoins, tokens, and digital assets where available.
* Creates unique POS transaction references and payment sessions from POS orders.
* Receives callback/status updates and synchronizes the Odoo POS payment line after confirmed payment.
* Supports webhook/status synchronization, crypto transaction monitoring, and operational transaction tracking.
* Includes backend configuration for API endpoint, hosted checkout domain, payout wallets, display settings, fallback QR mode, and operational tracking settings.

Odoo POS Payment Coverage:
HighRiskify POS Crypto can be used for Odoo POS Crypto Payments, Odoo POS Cryptocurrency Payments, Odoo POS Bitcoin Payments, Odoo POS Ethereum Payments, Odoo POS Stablecoin Payments, Odoo POS USDC Payments, Odoo POS USDT Payments, Odoo POS Blockchain Payments, Odoo POS Crypto Checkout, Odoo POS Crypto Payment Integration, Odoo POS Alternative Payment Methods, Odoo POS Web3 Payments, Odoo Point of Sale Crypto Payments, Odoo Retail Crypto Payments, Odoo Restaurant Crypto Payments, Odoo Store Crypto Payments, Odoo POS Stablecoin Gateway, Odoo POS Digital Asset Payments, Odoo POS Multi-Currency Payments, Odoo POS Merchant Payments, Odoo POS Crypto Merchant Gateway, Odoo POS Crypto Processing, Odoo POS Crypto Transactions, Odoo POS Crypto Settlement, Odoo POS Digital Currency Payments, Odoo POS Global Payments, Odoo POS International Payments, and Odoo POS Borderless Payments.

In-Person Checkout and POS Device Coverage:
The module is suitable for POS cryptocurrency gateway workflows, Bitcoin POS payment gateway workflows, USDC POS payment gateway workflows, USDT POS payment gateway workflows, Ethereum POS payment gateway workflows, QR code payment gateway flows, retail crypto checkout, restaurant crypto checkout, store crypto checkout, tap-to-pay crypto payment references, smart terminal crypto payment workflows, mobile POS crypto payments, Odoo POS crypto payment terminal workflows, Odoo POS crypto smart terminal setups, Odoo POS crypto card terminal workflows, Odoo POS crypto payment device workflows, Odoo POS iPhone crypto payments, Odoo POS smartphone crypto payments, Odoo POS Android crypto payments, Odoo POS tablet crypto payments, and Odoo POS touchscreen crypto payment workflows.

Crypto Asset and Network Coverage:
Supported crypto and network references may include Bitcoin, BTC, Bitcoin Cash, BCH, Litecoin, LTC, Dogecoin, DOGE, Ethereum, ETH, Solana, SOL, Avalanche, AVAX, Tron, TRX, BNB Smart Chain, BNB, BEP-20, ERC-20, TRC-20, Arbitrum, Avalanche Network, Polygon Network, Solana Network, Bitcoin Network, Ethereum Network, 1INCH, Cardano, ADA, Bitcoin BEP20, BTCB, PancakeSwap, CAKE, DAI, PHPt, Shiba Inu, SHIB, USD Coin, USDC, Tether, USDT, XRP, ARB, Chainlink, LINK, Ondo Finance, ONDO, Pepe, PEPE, Polygon, POL, Coinbase Wrapped Bitcoin, cbBTC, PayPal USD, PYUSD, World Liberty Financial USD, USD1, TrueUSD, TUSD, EURC, Wrapped Bitcoin, WBTC, Wrapped Ethereum, WETH, and other configured cryptocurrencies, stablecoins, tokens, and digital assets where available.

Stablecoin, Multi-Chain, and Blockchain Coverage:
The integration supports multi-chain payments, blockchain payments, stablecoin payments, cryptocurrency payments, digital asset payments, multi-chain crypto gateway workflows, multi-chain stablecoin payments, self-custody payments, non-custodial crypto payments, crypto API integration, Odoo payment API workflows, crypto webhook integration, crypto transaction monitoring, hosted crypto checkout, payment link generator workflows, low fee payment gateway workflows, reduced payment processing cost workflows, no-chargeback payment flows, instant payment settlement, fast settlement payments, global payment acceptance, international payments, borderless payments, alternative payment methods, crypto merchant processing, digital asset payments, blockchain payment gateway workflows, and secure crypto transaction workflows.

Extended Odoo Payment Flow Coverage:
Depending on the configured Odoo workflow, HighRiskify POS Crypto may also support Odoo POS crypto invoice payments, Odoo POS Bitcoin invoicing, Odoo POS USDC invoice payments, Odoo POS USDT invoice payments, generating crypto invoices in Odoo POS, paying Odoo POS invoices with crypto, cryptocurrency invoice settlement, blockchain invoicing, crypto accounts receivable workflows, Odoo crypto payment links, Odoo payment links, Odoo ecommerce crypto payments, Odoo website crypto checkout, Odoo online store crypto payments, Odoo crypto payment buttons, hosted crypto checkout routing, subscription-compatible crypto workflows, recurring crypto payment references, stablecoin billing references, and automated crypto billing flows where supported by the configured setup.

Customer Payment Flow:
When a cashier selects HighRiskify POS Crypto during the POS payment process, the module creates the required POS payment reference and starts the configured hosted crypto checkout or QR code payment request. The customer can scan the QR code or open the hosted payment page, send the required cryptocurrency amount using a supported network, and the module receives callback/status updates to synchronize the POS payment line and related transaction record after confirmed payment.

External Services and Data Handling:
This module connects Odoo POS with HighRiskify integration services to create checkout sessions, generate payment requests, process callbacks, synchronize payment status, and support operational transaction tracking. Limited transaction/order-related data may be exchanged for these functions, including POS reference, amount, currency, selected payment method or crypto asset, customer email where available, wallet/session information, callback status, transaction identifiers, merchant website information, and system-generated timestamps.

Availability Disclaimer:
Availability of cryptocurrencies, stablecoins, networks, QR code checkout, hosted crypto checkout, payment links, POS device flows, transaction monitoring, settlement routing, fees, limits, and customer eligibility depends on the configured HighRiskify crypto gateway settings, merchant wallet configuration, customer location, supported network availability, Odoo POS configuration, and provider-side requirements.
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
