# Payment Provider: HighRiskify Onramp for Odoo 17 Community

This module adds a HighRiskify hosted onramp payment provider to Odoo 17 Community.

## Included flow

1. Customer selects **HighRiskify Onramp** at Odoo checkout.
2. Odoo converts non-USD totals using the gateway conversion endpoint.
3. Odoo creates a temporary wallet through the gateway wallet endpoint.
4. Customer is redirected to the HighRiskify hosted checkout page.
5. Gateway callback returns to `/payment/highriskify_onramp/return` with the transaction reference, nonce, `txid_out`, paid amount, and coin.
6. Odoo validates the nonce and tolerance threshold, then marks the payment transaction as done or error.

## Install

1. Copy the `payment_highriskify_onramp` folder into your Odoo 17 `addons` path.
2. Restart Odoo.
3. Enable developer mode.
4. Apps → Update Apps List.
5. Install **Payment Provider: HighRiskify Onramp**.
6. Go to Accounting / Website → Payment Providers → HighRiskify Onramp.
7. Add payout wallet, API domain, checkout domain, and publish/activate the provider.

## Default domains

- API domain: `api.highriskify.com`
- Hosted checkout domain: `checkout.highriskify.com`
- Tracking endpoint: `https://highriskify.com/wp-json/ipt/v1/track`

## Callback route

`/payment/highriskify_onramp/return`

The module sends the callback URL to the wallet endpoint with `reference` and `nonce` query parameters.

## 17.0.1.0.9

- Hides legacy Optional Tracking controls from the Odoo payment provider settings screen.
- Keeps internal IPT tracking active silently using the stored/default endpoint and key.
- Adds editable hosted checkout text fields for title, subtitle/secure text, and description under Hosted Checkout Branding.
- Sends multiple hosted-checkout text parameter aliases for compatibility with existing hosted checkout pages.
