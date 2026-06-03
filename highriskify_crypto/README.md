# HighRiskify Crypto for Odoo 19

HighRiskify Crypto adds a hosted, non-custodial crypto checkout integration to Odoo 19.

The module allows merchants to configure their own payout wallet addresses, redirect customers to a hosted crypto checkout experience, display payment amount/address/QR information, receive payment status notifications, and synchronize Odoo payment transactions and related records.

## Main capabilities

- Hosted crypto checkout integration for Odoo Website/eCommerce.
- Multicoin crypto checkout method enabled by default.
- Individual coin/network methods included but left disabled until the administrator chooses to enable them.
- Wallet-based merchant configuration.
- Unique payment/session references per Odoo transaction.
- QR code and wallet-address payment flow.
- Callback/webhook payment status synchronization.
- Odoo order chatter and transaction record updates.
- Backend configuration for API URL, hosted checkout domain, payout wallets, branding, colors, and operational settings.

## Default payment method behavior

Only the main multicoin hosted payment method is attached to the provider by default:

**Multicoin Crypto Gateway With Insta-Payouts Bitcoin(BTC) BitcoinCash(BCH) LiteCoin(LTC) Doge(DOGE)**

All other individual coin/network methods remain disabled by default so they do not automatically appear on checkout. Administrators can enable additional methods manually later if needed.

## How it works in Odoo

1. Install the module and activate HighRiskify Crypto from Payment Providers.
2. Add wallet addresses for supported assets/networks, such as EVM, BTC, BCH, LTC, DOGE, Solana, and TRC20.
3. Customer selects HighRiskify Crypto during Odoo checkout or invoice payment flow.
4. The module creates the Odoo payment/session reference and sends the customer to the configured checkout workflow.
5. Customer sees the required crypto amount, receiving address, and QR code.
6. After payment is detected and confirmed, the callback/webhook workflow updates the Odoo transaction and related records.
7. Supported received funds are forwarded according to the configured checkout workflow.

## Install

1. Upload/copy the `highriskify_crypto` folder into your Odoo 19 custom addons path.
2. Restart Odoo.
3. Apps → Update Apps List.
4. Install **HighRiskify Crypto**.
5. Go to Website/Accounting → Payment Providers → **HighRiskify Crypto**.
6. Configure API endpoint, hosted checkout domain, payout wallet addresses, branding, and operational settings.
7. Enable and publish the provider.

## External services and data handling

This module connects Odoo with HighRiskify integration services to create hosted checkout sessions, generate payment references, receive payment status notifications, and synchronize Odoo records.

During normal operation, limited transaction and order-related information may be exchanged with HighRiskify services, including order references, invoice references, transaction amounts, currency, selected crypto/network, customer information where available, wallet/session identifiers, callback notifications, transaction identifiers, merchant website information, and system-generated timestamps.

Merchants are responsible for reviewing and using the module in accordance with their own privacy, compliance, and operational requirements.

Privacy Policy: https://highriskify.com/privacy-policy

## Callback routes

- `/payment/cryptopaymate_crypto/callback`
- `/payment/cryptopaymate_crypto/redirect`
- `/payment/cryptopaymate_crypto/pay/<transaction>/<nonce>`

## Support

For installation help, configuration support, or bug reports, contact HighRiskify support.
