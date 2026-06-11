# HighRiskify POS Crypto for Odoo 17

## Short Description / Tagline

Accept Bitcoin, USDC, USDT, BTC, BCH, LTC, DOGE, ETH, SOL and stablecoin crypto payments in Odoo POS with QR payments, payment links, Wallet Connect, hosted checkout, non-custodial/self-custody settlement, webhook status sync, and POS crypto gateway support.

## Long Description

Odoo POS Crypto Payments | Bitcoin, USDC & USDT Gateway

HighRiskify POS Crypto adds cryptocurrency payment support to **Odoo Point of Sale**. It is built for merchants that want a POS Crypto, POS Bitcoin, POS USDC, POS USDT, POS Stablecoin, POS Payments, Crypto POS, Bitcoin POS, or Stablecoin POS payment option inside Odoo POS.

The module allows POS staff to select a HighRiskify crypto payment terminal from the POS payment screen, create a hosted crypto checkout or QR payment request, and synchronize confirmed payment status back into Odoo POS. It supports secure non-custodial crypto transaction workflows for point-of-sale checkout, including pos application, pos machine, pos gateway, and in-person POS payment flows.

## Main Flow

1. Cashier selects **HighRiskify POS Crypto** in Odoo POS.
2. The module creates a hosted multicoin crypto session or single-network QR payment request.
3. A customer payment page opens in a popup/new tab.
4. The customer sends the required crypto amount to the generated payment address or hosted checkout request.
5. HighRiskify sends a server-side callback to `/pos/highriskify_crypto/callback`.
6. Odoo polls transaction status and marks the POS payment line done only after a confirmed callback.

## Supported Modes

- **Hosted multicoin checkout**: creates a hosted crypto checkout flow for supported assets and networks.
- **Single ticker QR checkout**: creates a network-specific payment request with a QR code and generated wallet address.
- **Wallet and QR payments**: supports QR Payments, wallet payments, Wallet Connect-style flows, Payment Links, and hosted checkout routing where configured.
- **Non-custodial settlement**: supports Non Custodial, Self Custody, and merchant wallet payout workflows according to the configured gateway setup.

## Configuration

Go to **Point of Sale > Configuration > Payment Methods**, open **HighRiskify POS Crypto**, then configure:

- HighRiskify API base URL
- Hosted checkout domain
- Crypto checkout mode
- Merchant payout wallet addresses
- QR fallback mode
- Confirmation and underpayment tolerance settings
- Hosted checkout logo/theme settings
- Operational tracking settings where required

Then add the payment method to your POS configuration and close/reopen the POS session.

## Brand and POS Search Keywords

Highriskify, High riskify, pos application, pos machine, pos gateway, pos, POS Crypto, POS Bitcoin, POS USDC, POS USDT, POS Stablecoin, POS Payments, Crypto POS, Bitcoin POS, Stablecoin POS.

## Accepted Crypto, Token, and Stablecoin Keywords

Bitcoin, BTC, Bitcoin Cash, BCH, Litecoin, LTC, Dogecoin, DOGE, Ethereum, ETH, Solana, SOL, Avalanche, AVAX, Tron, TRX, BNB Smart Chain, BEP-20, 1INCH, Cardano, ADA, BNB, Bitcoin BEP20, BTCB, PancakeSwap, CAKE, DAI, PHPt, Shiba Inu, SHIB, USD Coin, USDC, Tether, USDT, XRP, ERC-20, Arbitrum, ARB, Chainlink, LINK, Ondo Finance, ONDO, Pepe, PEPE, Polygon, POL, Coinbase Wrapped Bitcoin, cbBTC, PayPal USD, PYUSD, World Liberty Financial USD, USD1, TrueUSD, TUSD, EURC, Wrapped Bitcoin, WBTC, Wrapped Ethereum, WETH.

## Blockchain Network Keywords

Bitcoin Network, Ethereum Network, BNB Smart Chain, BEP-20, ERC-20, TRC-20, Solana Network, Arbitrum Network, Avalanche Network, Polygon Network.

## Checkout, Gateway, Wallet, and Payment Flow Keywords

Crypto, Crypto Payment, Crypto Payments, Bitcoin Payments, Stablecoin, Stablecoin Payments, Blockchain Payments, Odoo Crypto, Crypto Checkout, Crypto Gateway, Bitcoin Gateway, USDC Gateway, No KYC, Payment Gateway, Crypto Payment Gateway, Non Custodial, Self Custody, Wallet Connect, QR Payments, Payment Links.

## Merchant Category and Industry Search Terms

CBD, Hemp Products, Vape Products, E-Cigarettes, Nicotine Products, Kratom, Supplements, Nutraceuticals, Telehealth, Peptides, Anti-Aging Clinics, Wellness Clinics, Medical Spas (Med Spas), Weight Loss Programs, GLP-1 Clinics, Testosterone Therapy (TRT), Hormone Replacement Therapy (HRT), Research Chemicals, Adult Products, Adult Content, Dating Services, Subscription Services, Membership Programs, Debt Relief, Credit Repair, Forex, Cryptocurrency, Crypto Exchanges, Crypto On-Ramps, Gambling, Sports Betting, Sweepstakes, Firearms Accessories, Ammunition, Precious Metals, Pawn Shops, Smoke Shops, Head Shops, Herbal Products, Alternative Health Products, Travel Clubs, Business Opportunities, Coaching Programs, Ticket Resellers, Multi-Level Marketing (MLM), Drop Shipping, International E-Commerce, Replica Products (usually prohibited), Digital Downloads, Software Licenses, IPTV Services, Debt Collection.

## Odoo Store Category

Recommended Odoo Store category: **Point of Sale**.

Secondary related categories: **Payment**, **eCommerce**, **Website**, and **Accounting**.

The module manifest uses the Odoo internal category path **Sales/Point of Sale** because this is a POS-specific crypto payment gateway.

## External Services and Data Handling

This module connects Odoo POS with HighRiskify integration services to create checkout sessions, generate payment requests, process callbacks, synchronize status, and support operational transaction tracking. Limited transaction/order-related information may be exchanged for these functions, including POS reference, amount, currency, selected payment method or crypto asset, customer email where available, wallet/session information, callback status, transaction identifiers, merchant website information, and timestamps.

Privacy Policy: https://highriskify.com/privacy-policy

## Availability Disclaimer

Availability of Crypto, Crypto Payment, Crypto Payments, Bitcoin Payments, Stablecoin, Stablecoin Payments, Blockchain Payments, Odoo Crypto, Crypto Checkout, Crypto Gateway, Bitcoin Gateway, USDC Gateway, No KYC, Payment Gateway, Crypto Payment Gateway, Non Custodial, Self Custody, Wallet Connect, QR Payments, Payment Links, cryptocurrencies, stablecoins, networks, settlement routing, and payment status synchronization depends on merchant configuration, customer location, supported network availability, provider-side requirements, and Odoo POS setup.
