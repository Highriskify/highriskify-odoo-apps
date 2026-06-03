# HighRiskify POS Crypto for Odoo 18

HighRiskify POS Crypto adds cryptocurrency payment support to **Odoo Point of Sale**.

It allows POS staff to select a HighRiskify crypto payment terminal from the POS payment screen, create a hosted crypto checkout or QR payment request, and synchronize confirmed payment status back into Odoo POS.

## Main flow

1. Cashier selects **HighRiskify POS Crypto** in Odoo POS.
2. The module creates a hosted multicoin crypto session or single-network QR payment request.
3. A customer payment page opens in a popup/new tab.
4. The customer sends the required crypto amount to the generated payment address or hosted checkout request.
5. HighRiskify sends a server-side callback to `/pos/highriskify_crypto/callback`.
6. Odoo polls transaction status and marks the POS payment line done only after a confirmed callback.

## Supported modes

- **Hosted multicoin checkout**: creates a hosted crypto checkout flow for supported assets and networks.
- **Single ticker QR checkout**: creates a network-specific payment request with a QR code and generated wallet address.

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

## External services and data handling

This module connects Odoo POS with HighRiskify integration services to create checkout sessions, generate payment requests, process callbacks, synchronize status, and support operational transaction tracking. Limited transaction/order-related information may be exchanged for these functions, including POS reference, amount, currency, customer email where available, wallet/session information, callback status, transaction identifiers, merchant website information, and timestamps.

Privacy Policy: https://highriskify.com/privacy-policy
