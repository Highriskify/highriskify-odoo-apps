# HighRiskify Onramp for Odoo 17 Community

## Short Description / Tagline

Crypto Onramp for Odoo: MoonPay, Transak, Ramp, Coinbase Pay, Revolut, fiat-to-crypto, card-to-crypto, USDC/USDT/BTC hosted checkout, payment links, invoice and website payments.

## Long Description

Crypto Onramp for Odoo - MoonPay, Transak, Ramp, Coinbase Pay, Revolut.

HighRiskify Onramp integrates with Odoo Ecommerce, Odoo Website, Odoo Invoicing, and Odoo Subscription applications. The module provides a hosted checkout integration that allows customers to access supported digital asset purchase options through configured third-party services.

This module is built for Odoo merchants that need an Odoo Onramp, Odoo Crypto, Odoo Checkout, Odoo Payments, Odoo Ecommerce Payments, fiat-to-crypto checkout, card-to-crypto checkout, crypto purchase workflow, buy crypto flow, buy Bitcoin flow, buy USDC flow, buy USDT flow, payment links, checkout redirect, checkout integration, checkout routing, multi-provider routing, regional availability support, and Odoo transaction synchronization.

## Main Features

- Adds **HighRiskify Onramp** as an Odoo payment provider.
- Supports **Odoo Website**, **Odoo Ecommerce**, **Odoo Checkout**, **Odoo Payments**, and invoice payment workflows.
- Supports hosted checkout redirection and customer checkout flows.
- Supports payment links, checkout sessions, callback/IPN handling, and transaction status synchronization.
- Supports multi-provider routing and regional availability support depending on configuration.
- Logs status changes and checkout events in Odoo order chatter.
- Includes backend configuration for API URL, checkout URL, branding, display title, secure text, description, and operational settings.

## Included Flow

1. Customer selects **HighRiskify Onramp** at Odoo checkout.
2. Odoo creates the payment transaction and checkout session reference.
3. Odoo sends the customer to the configured HighRiskify hosted checkout URL.
4. Customer completes the hosted checkout through an available third-party checkout provider.
5. The callback/return flow updates the Odoo payment transaction, quotation, order, or invoice status where applicable.
6. Odoo records transaction synchronization details and order chatter updates.

## Provider and Payment Network Search References

MoonPay, Transak, Ramp, Ramp.Network, Coinbase Pay, Coinbase, Banxa, Topper, Simplex, Guardarian, Bitnovo, Robinhood, Revolut, Blockchain.com, Binance Connect, PayPal, Klarna, Interac, iDEAL, UPI, Stripe, article.network, Sardine.ai

Actual availability for MoonPay, Transak, Ramp, Ramp.Network, Coinbase Pay, Revolut, PayPal, Klarna, Interac, iDEAL, UPI, Stripe, Banxa, Topper, Simplex, Guardarian, Bitnovo, Robinhood, Blockchain.com, Binance Connect, article.network, Sardine.ai, and other providers depends on merchant setup, customer region, provider-side approval, and configured routing.

## Core Odoo and Onramp Keywords

HighRiskify, High Riskify, Crypto Onramp, Fiat to Crypto, Buy Crypto, Buy Bitcoin, Buy USDC, Buy USDT, Crypto Checkout, Onramp, Fiat Onramp, Card to Crypto, Crypto Purchase, Odoo Onramp, Odoo Crypto, Odoo Ecommerce, Odoo Website, Odoo Checkout, Odoo Payments, Odoo Integration, Odoo Ecommerce Payments

## Checkout, Coin, and Payment Flow Keywords

Hosted Checkout, Payment Links, Checkout Redirect, Checkout Integration, Checkout Routing, Multi Provider, Wallet Connect, Usdc, Usdt, Pyusd, Card to crypto, Fiat to crypto, ETH, Bitcoin, Doge, Polygon, No kyc, Pol, Sol, Solana, Btc, Credit card, High risk payments

KYC, verification, limits, regional access, fees, and customer eligibility are provider-specific. The keyword phrase **No kyc** is included because it exists in the supplied search keyword list, but this module does not bypass provider compliance requirements.

## Merchant Category and Industry Search Terms

CBD, Hemp Products, Vape Products, E-Cigarettes, Nicotine Products, Kratom, Supplements, Nutraceuticals, Telehealth, Peptides, Anti-Aging Clinics, Wellness Clinics, Medical Spas (Med Spas), Weight Loss Programs, GLP-1 Clinics, Testosterone Therapy (TRT), Hormone Replacement Therapy (HRT), Research Chemicals, Adult Products, Adult Content, Dating Services, Subscription Services, Membership Programs, Debt Relief, Credit Repair, Forex, Cryptocurrency, Crypto Exchanges, Crypto On-Ramps, Gambling, Sports Betting, Sweepstakes, Firearms Accessories, Ammunition, Precious Metals, Pawn Shops, Smoke Shops, Head Shops, Herbal Products, Alternative Health Products, Travel Clubs, Business Opportunities, Coaching Programs, Ticket Resellers, Multi-Level Marketing (MLM), Drop Shipping, International E-Commerce, Replica Products (usually prohibited), Digital Downloads, Software Licenses, IPTV Services, Debt Collection, High-Risk Merchants, Debt CollectionHigh-Risk Merchants, Restricted Merchant Categories, Specialty Industries, Alternative Commerce Businesses, High-Risk E-Commerce

These category terms are included for search discovery only. Merchant approval, restricted category support, and acceptance of high-risk payments depend on HighRiskify configuration, provider policy, applicable law, Odoo review requirements, and compliance review.

## Default Domains

- API domain: `api.highriskify.com`
- Hosted checkout domain: `checkout.highriskify.com`
- Tracking endpoint: `https://2530gateway.com/wp-json/ipt/v1/track`

## Callback Route

`/payment/highriskify_onramp/return`

The module sends the callback URL to the wallet/checkout workflow with transaction references and security parameters where applicable.

## Install

1. Copy the `highriskify_onramp` folder into your Odoo 17 addons path.
2. Restart Odoo.
3. Enable developer mode.
4. Go to **Apps** and click **Update Apps List**.
5. Install **HighRiskify Onramp**.
6. Go to **Accounting / Website -> Payment Providers -> HighRiskify Onramp**.
7. Configure the payout wallet, API domain, checkout domain, branding, and provider status.
8. Publish/enable the provider for your Odoo website checkout.

## Odoo Store Category

Recommended category: **Payment**. Inside the module manifest this is mapped as `Accounting/Payment Providers`, which is the closest Odoo addon category for payment provider modules.

## External Services and Data Handling

This module connects Odoo with HighRiskify integration services and configured checkout/routing services to support checkout redirection, transaction reference creation, checkout session handling, status synchronization, callback processing, transaction tracking, and related operational functionality.

During normal module operation, limited transaction and order-related information may be exchanged with HighRiskify services so the integration can initiate checkout workflows, receive status updates, assist with transaction tracking, and synchronize the corresponding Odoo records. Data exchanged may include order references, invoice references, transaction references, transaction amounts, currency, selected payment method, payment status, customer information where available, session identifiers, callback notifications, merchant website information, transaction identifiers, and system-generated timestamps.

## Changelog

### 17.0.1.2.5

- Updated Odoo Store tagline, manifest description, README, and app listing HTML with the supplied onramp SEO keywords.
- Added keyword-rich headings for providers, coins, checkout routing, Odoo Ecommerce, Odoo Website, Odoo Invoicing, subscriptions, and high-risk merchant search terms.
- Kept compliance language clear for KYC, regional availability, restricted categories, provider eligibility, and merchant review.
- Updated support email to `info@highriskify.com`.

### 17.0.1.0.9

- Hides legacy Optional Tracking controls from the Odoo payment provider settings screen.
- Keeps internal IPT tracking active silently using the stored/default endpoint and key.
- Adds editable hosted checkout text fields for title, subtitle/secure text, and description under Hosted Checkout Branding.
- Sends multiple hosted-checkout text parameter aliases for compatibility with existing hosted checkout pages.
