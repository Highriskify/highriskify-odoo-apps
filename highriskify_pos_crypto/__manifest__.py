# -*- coding: utf-8 -*-

{
'name': 'HighRiskify POS Crypto',
'version': '17.0.1.1.2',
'category': 'Sales/Point of Sale',
'summary': 'Accept Bitcoin, USDC, USDT, BTC, BCH, LTC, DOGE, ETH, SOL and stablecoin crypto payments in Odoo POS with QR payments, payment links, Wallet Connect, hosted checkout, non-custodial/self-custody settlement, webhook status sync, and POS crypto gateway support.',
'description': 'Odoo POS Crypto Payments | Bitcoin, USDC & USDT Gateway\n\nHighRiskify POS Crypto is a cryptocurrency non-custodial payment provider integration for Odoo POS. The module lets merchants add a Crypto Payment Gateway to Odoo Point of Sale so cashiers can start POS Crypto, POS Bitcoin, POS USDC, POS USDT, POS Stablecoin, Crypto POS, Bitcoin POS, and Stablecoin POS checkout flows from the Odoo POS payment screen.\n\nCustomers can complete payment using hosted crypto checkout, QR Payments, Payment Links, Wallet Connect-style wallet payments, and supported blockchain payment workflows depending on merchant configuration, customer location, and network availability. Supported search and network references include BTC, ETH, USDT, LTC, DASH, DOGE, ERC-20, (BNB)BEP-20, (TRON)TRC-20, Arbitrum, Solana, Avalanche, Polygon, and XRP wrapped versions on EVM chains.\n\nMain Capabilities:\n\n* Adds HighRiskify POS Crypto as an Odoo POS payment terminal option.\n* Supports Odoo POS Crypto Payments, POS Bitcoin, POS USDC, POS USDT, POS Stablecoin, POS Payments, Crypto POS, Bitcoin POS, and Stablecoin POS workflows.\n* Supports hosted crypto checkout, QR Payments, Payment Links, wallet payments, and crypto payment request workflows from the POS payment screen.\n* Supports retail POS, restaurant POS, store checkout, mobile POS, tablet POS, touchscreen POS, pos application, pos machine, pos gateway, and in-person point-of-sale payment workflows.\n* Supports non-custodial, Non Custodial, Self Custody, merchant wallet, and wallet settlement configuration where supported.\n* Supports callback/status synchronization and updates Odoo POS payment lines after confirmed crypto payment.\n* Supports blockchain payments, stablecoin payments, Crypto Payment Gateway workflows, Bitcoin Gateway references, USDC Gateway references, and Payment Gateway search coverage.\n\nBrand and POS Search Keywords:\nHighriskify, High riskify, pos application, pos machine, pos gateway, pos, POS Crypto, POS Bitcoin, POS USDC, POS USDT, POS Stablecoin, POS Payments, Crypto POS, Bitcoin POS, Stablecoin POS.\n\nCrypto Asset, Token, and Stablecoin Search Keywords:\nBitcoin, BTC, Bitcoin Cash, BCH, Litecoin, LTC, Dogecoin, DOGE, Ethereum, ETH, Solana, SOL, Avalanche, AVAX, Tron, TRX, BNB Smart Chain, BEP-20, 1INCH, Cardano, ADA, BNB, Bitcoin BEP20, BTCB, PancakeSwap, CAKE, DAI, PHPt, Shiba Inu, SHIB, USD Coin, USDC, Tether, USDT, XRP, ERC-20, Arbitrum, ARB, Chainlink, LINK, Ondo Finance, ONDO, Pepe, PEPE, Polygon, POL, Coinbase Wrapped Bitcoin, cbBTC, PayPal USD, PYUSD, World Liberty Financial USD, USD1, TrueUSD, TUSD, EURC, Wrapped Bitcoin, WBTC, Wrapped Ethereum, WETH.\n\nBlockchain Network Search Keywords:\nBitcoin Network, Ethereum Network, BNB Smart Chain, BEP-20, ERC-20, TRC-20, Solana Network, Arbitrum Network, Avalanche Network, Polygon Network.\n\nCheckout, Gateway, Wallet, and Payment Flow Keywords:\nCrypto, Crypto Payment, Crypto Payments, Bitcoin Payments, Stablecoin, Stablecoin Payments, Blockchain Payments, Odoo Crypto, Crypto Checkout, Crypto Gateway, Bitcoin Gateway, USDC Gateway, No KYC, Payment Gateway, Crypto Payment Gateway, Non Custodial, Self Custody, Wallet Connect, QR Payments, Payment Links.\n\nMerchant Category and Industry Search Terms:\nCBD, Hemp Products, Vape Products, E-Cigarettes, Nicotine Products, Kratom, Supplements, Nutraceuticals, Telehealth, Peptides, Anti-Aging Clinics, Wellness Clinics, Medical Spas (Med Spas), Weight Loss Programs, GLP-1 Clinics, Testosterone Therapy (TRT), Hormone Replacement Therapy (HRT), Research Chemicals, Adult Products, Adult Content, Dating Services, Subscription Services, Membership Programs, Debt Relief, Credit Repair, Forex, Cryptocurrency, Crypto Exchanges, Crypto On-Ramps, Gambling, Sports Betting, Sweepstakes, Firearms Accessories, Ammunition, Precious Metals, Pawn Shops, Smoke Shops, Head Shops, Herbal Products, Alternative Health Products, Travel Clubs, Business Opportunities, Coaching Programs, Ticket Resellers, Multi-Level Marketing (MLM), Drop Shipping, International E-Commerce, Replica Products (usually prohibited), Digital Downloads, Software Licenses, IPTV Services, Debt Collection.\n\nExternal Services and Data Handling:\nThis module connects Odoo POS with HighRiskify integration services to create checkout sessions, generate payment requests, process callbacks, synchronize payment status, and support operational transaction tracking. Limited transaction/order-related data may be exchanged for these functions, including POS reference, amount, currency, selected payment method or crypto asset, customer email where available, wallet/session information, callback status, transaction identifiers, merchant website information, and system-generated timestamps.\n\nAvailability Disclaimer:\nAvailability of cryptocurrencies, stablecoins, networks, QR code checkout, hosted crypto checkout, payment links, POS device flows, transaction monitoring, settlement routing, fees, limits, and customer eligibility depends on the configured HighRiskify crypto gateway settings, merchant wallet configuration, customer location, supported network availability, Odoo POS configuration, and provider-side requirements.',
'author': 'HighRiskify',
'website': 'https://highriskify.com',
'support': 'info@highriskify.com',
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
