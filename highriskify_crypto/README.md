# HighRiskify Crypto for Odoo 17

## Short Description / Tagline

Accept Bitcoin, USDC, USDT, BTC, BCH, LTC, DOGE, ETH and stablecoin crypto payments in Odoo Website, Ecommerce, invoices and hosted checkout with QR payments, wallet payments, payment links, webhook sync and non-custodial settlement.

## Long Description

HighRiskify Crypto is a **Cryptocurrency Non-Custodial Crypto Payment Gateway** for Odoo Website, Odoo Ecommerce, Odoo Invoicing, and compatible Odoo Subscription payment flows. It allows merchants to add crypto checkout to Odoo so customers can pay through hosted checkout, QR payments, wallet payments, payment links, crypto invoices, invoice emails, and webhook-synchronized payment flows.

The module is built for Odoo online payments and can support Bitcoin, USDC, USDT, BTC, ETH, LTC, DASH, DOGE, ERC-20, BNB Smart Chain BEP-20, TRON TRC-20, Arbitrum, Solana, Avalanche, Polygon, XRP wrapped versions on EVM chains, and other configured assets or networks where available.

## Main Capabilities

- Hosted crypto checkout integration for Odoo Website and Odoo Ecommerce.
- Multicoin crypto checkout method enabled by default.
- Individual coin/network methods included but left disabled until the administrator chooses to enable them.
- Wallet-based merchant configuration for non-custodial and self-custody payment workflows.
- Unique payment/session references per Odoo transaction.
- QR payments and wallet-address payment flow.
- Payment links, crypto payment link workflows, invoice payment links, and invoice email payment flows.
- Callback/webhook payment status synchronization.
- Odoo order chatter and transaction record updates.
- Backend configuration for API URL, hosted checkout domain, payout wallets, branding, colors, and operational settings.

## Default Payment Method Behavior

Only the main multicoin hosted payment method is attached to the provider by default:

**Multicoin Crypto Gateway With Insta-Payouts Bitcoin(BTC) BitcoinCash(BCH) LiteCoin(LTC) Doge(DOGE)**

All individual coin methods remain present in the module but are not automatically attached to the provider. Administrators can enable additional methods manually if needed.

## Core Odoo and Crypto Payment Keywords

Odoo Crypto, Crypto Payments, Crypto Gateway, Crypto Checkout, Bitcoin Payments, Bitcoin Gateway, USDC Payments, USDT Payments, Stablecoin Payments, Stablecoin Gateway, Odoo Website, Odoo Ecommerce, Odoo Checkout, Odoo Payments, Odoo Payment Gateway, Odoo Website Payments, Odoo Ecommerce Payments, Odoo Online Store, Ecommerce Crypto, Website Crypto, Online Crypto Payments, Crypto Shopping Cart, Crypto Processor, Crypto Merchant, Payment Links, Hosted Checkout, QR Payments, Non Custodial, Self Custody, Wallet Connect, Wallet Payments, Crypto API, Payment API, Webhook, Crypto Invoices, Invoice Payments, Subscription Payments, Recurring Payments, Crypto Billing, Stablecoin Billing, Crypto payment link, Invoice email, Crypto, Payment Gateway, Website Payments, Ecommerce Payments.

## Brand and General Search Keywords

High riskify, Highriskify, HighRiskify, High Riskify, check out, online payments.

## Accepted Crypto, Token, and Stablecoin Keywords

Bitcoin, BTC, Bitcoin Cash, BCH, Litecoin, LTC, Dogecoin, DOGE, Ethereum, ETH, Solana, SOL, Avalanche, AVAX, Tron, TRX, BNB Smart Chain, BEP-20, 1INCH, Cardano, ADA, BNB, Bitcoin BEP20, BTCB, PancakeSwap, CAKE, DAI, PHPt, Shiba Inu, SHIB, USD Coin, USDC, Tether, USDT, XRP, ERC-20, Arbitrum, ARB, Chainlink, LINK, Ondo Finance, ONDO, PEPE, Polygon, POL, Coinbase Wrapped Bitcoin, cbBTC, PayPal USD, PYUSD, World Liberty Financial USD, USD1, TrueUSD, TUSD, EURC, Wrapped Bitcoin, WBTC, Wrapped Ethereum, WETH, DASH.

## Blockchain Network Keywords

Bitcoin Network, Ethereum Network, BNB Smart Chain, BEP-20, ERC-20, TRC-20, Solana Network, Arbitrum Network, Avalanche Network, Polygon Network.

## Checkout, API, Webhook, and Payment Flow Keywords

This module is relevant for Odoo crypto checkout, Odoo payment gateway, Bitcoin payments, Bitcoin gateway, USDC payments, USDT payments, stablecoin payments, stablecoin gateway, ecommerce crypto, website crypto, online crypto payments, crypto shopping cart, crypto processor, crypto merchant, payment links, hosted checkout, QR payments, non custodial payments, self custody payments, wallet connect, wallet payments, crypto API, payment API, webhook payment notifications, crypto invoices, invoice payments, subscription payments, recurring payments, crypto billing, stablecoin billing, crypto payment link, invoice email, crypto, payment gateway, website payments, ecommerce payments, subscription payments, and invoice payments.

## Merchant Category and Industry Search Terms

HighRiskify Crypto can be discovered by merchants looking for alternative payment methods, crypto payments, stablecoin payments, ecommerce payments, website payments, subscription payments, invoice payments, high-risk ecommerce, restricted merchant category payment options, and specialty industry payment workflows.

Merchant category search terms include: CBD, Hemp Products, Vape Products, E-Cigarettes, Nicotine Products, Kratom, Supplements, Nutraceuticals, Telehealth, Peptides, Anti-Aging Clinics, Wellness Clinics, Medical Spas (Med Spas), Weight Loss Programs, GLP-1 Clinics, Testosterone Therapy (TRT), Hormone Replacement Therapy (HRT), Research Chemicals, Adult Products, Adult Content, Dating Services, Subscription Services, Membership Programs, Debt Relief, Credit Repair, Forex, Cryptocurrency, Crypto Exchanges, Crypto On-Ramps, Gambling, Sports Betting, Sweepstakes, Firearms Accessories, Ammunition, Precious Metals, Pawn Shops, Smoke Shops, Head Shops, Herbal Products, Alternative Health Products, Travel Clubs, Business Opportunities, Coaching Programs, Ticket Resellers, Multi-Level Marketing (MLM), Drop Shipping, International E-Commerce, Replica Products (usually prohibited), Digital Downloads, Software Licenses, IPTV Services, Debt Collection.

These category references are included for search discovery and merchant research. Availability, approval, and suitability depend on applicable law, merchant compliance, HighRiskify operational settings, network support, and checkout configuration.

## External Services and Data Handling

This module connects Odoo with HighRiskify integration services to create hosted crypto checkout sessions, generate payment references, receive status notifications, and synchronize related Odoo records.

During normal operation, limited transaction and order-related information may be exchanged with HighRiskify services so the integration can initiate checkout, monitor payment status, process callback notifications, and update the corresponding Odoo records. Data may include order references, invoice references, transaction amounts, currency, selected crypto/network, customer information where available, wallet/session identifiers, callback notifications, transaction identifiers, merchant website information, and system-generated timestamps.

## Odoo Store Category

Recommended Odoo Store category: **Payment**.

Closest related categories: **eCommerce**, **Website**, and **Accounting**.

Do not use **Point of Sale** for this Website Crypto module unless a separate POS crypto module is being published.

## Installation

1. Copy the `highriskify_crypto` directory into your custom Odoo addons path.
2. Restart Odoo and update the Apps list.
3. Install **HighRiskify Crypto**.
4. Open Payment Providers and configure HighRiskify Crypto.
5. Add the required wallet addresses and hosted checkout settings.
6. Enable the provider for the required Odoo website/payment flow.

## Support

For setup help, configuration support, or bug reports, contact HighRiskify at info@highriskify.com.
