PROVIDER_CODE = 'highriskify_onramp'

# One Odoo payment provider, multiple payment methods under it.
# These names/slugs mirror the WooCommerce include files, but DO NOT create
# separate Odoo payment.provider cards.
PAYMENT_METHODS = [
    {'code': 'highriskify_onramp', 'name': 'Pay By Credit / Debit Card — Powered by On-Ramp Provider', 'slug': '', 'path': 'pay.php', 'force_currency': None, 'gateway_suffix': 'hostedinstaonrampdotto'},
    {'code': 'highriskify_banxa', 'name': 'Banxa Onramp (Credit Card)', 'slug': 'banxa', 'path': 'process-payment.php', 'force_currency': None, 'gateway_suffix': 'banxacom'},
    {'code': 'highriskify_binance', 'name': 'Binance Onramp (Credit Card)', 'slug': 'binance', 'path': 'process-payment.php', 'force_currency': None, 'gateway_suffix': 'binancecom'},
    {'code': 'highriskify_bitnovo', 'name': 'Bitnovo Onramp (Credit Card)', 'slug': 'bitnovo', 'path': 'process-payment.php', 'force_currency': 'USD', 'gateway_suffix': 'bitnovocom'},
    {'code': 'highriskify_customprovider', 'name': 'Custom Onramp (Credit Card)', 'slug': 'moonpay', 'path': 'process-payment.php', 'force_currency': None, 'gateway_suffix': 'customprovider'},
    {'code': 'highriskify_interac', 'name': 'Interac Onramp (Credit Card)', 'slug': 'interac', 'path': 'process-payment.php', 'force_currency': None, 'gateway_suffix': 'interaccad'},
    {'code': 'highriskify_moonpay', 'name': 'Moonpay Onramp (Credit Card)', 'slug': 'moonpay', 'path': 'process-payment.php', 'force_currency': None, 'gateway_suffix': 'moonpaycom'},
    {'code': 'highriskify_paypal', 'name': 'PayPal Onramp (Credit Card)', 'slug': 'paypal', 'path': 'process-payment.php', 'force_currency': 'USD', 'gateway_suffix': 'paypalcom'},
    {'code': 'highriskify_rampnetwork', 'name': 'Ramp Onramp (Credit Card)', 'slug': 'rampnetwork', 'path': 'process-payment.php', 'force_currency': 'USD', 'gateway_suffix': 'rampnetwork'},
    {'code': 'highriskify_revolut', 'name': 'Revolut Onramp (Credit Card)', 'slug': 'revolut', 'path': 'process-payment.php', 'force_currency': None, 'gateway_suffix': 'revolutcom'},
    {'code': 'highriskify_robinhood', 'name': 'Robinhood Onramp (Credit Card)', 'slug': 'robinhood', 'path': 'process-payment.php', 'force_currency': 'USD', 'gateway_suffix': 'robinhoodcom'},
    {'code': 'highriskify_sardine', 'name': 'Sardine Onramp (Credit Card)', 'slug': 'sardine', 'path': 'process-payment.php', 'force_currency': None, 'gateway_suffix': 'sardineai'},
    {'code': 'highriskify_simplex', 'name': 'Simplex Onramp (Credit Card)', 'slug': 'simplex', 'path': 'process-payment.php', 'force_currency': None, 'gateway_suffix': 'simplexcom'},
    {'code': 'highriskify_stripe', 'name': 'Stripe Onramp (Credit Card)', 'slug': 'stripe', 'path': 'process-payment.php', 'force_currency': 'USD', 'gateway_suffix': 'stripecom'},
    {'code': 'highriskify_topper', 'name': 'Topper Onramp (Credit Card)', 'slug': 'topper', 'path': 'process-payment.php', 'force_currency': None, 'gateway_suffix': 'topperpaycom'},
    {'code': 'highriskify_transak', 'name': 'Transak Onramp (Credit Card)', 'slug': 'transak', 'path': 'process-payment.php', 'force_currency': None, 'gateway_suffix': 'transakcom'},
    {'code': 'highriskify_transfi', 'name': 'TransFi Onramp (Credit Card)', 'slug': 'transfi', 'path': 'process-payment.php', 'force_currency': 'USD', 'gateway_suffix': 'transficom'},
    {'code': 'highriskify_upi', 'name': 'UPI Onramp (Credit Card)', 'slug': 'upi', 'path': 'process-payment.php', 'force_currency': None, 'gateway_suffix': 'upiimps'},
    {'code': 'highriskify_utorg', 'name': 'Utorg Onramp (Credit Card)', 'slug': 'utorg', 'path': 'process-payment.php', 'force_currency': None, 'gateway_suffix': 'utorgpro'},
]
PAYMENT_METHOD_MAP = {m['code']: m for m in PAYMENT_METHODS}
DEFAULT_PAYMENT_METHOD_CODES = set(PAYMENT_METHOD_MAP.keys())

POLYGON_USDC_CONTRACT = '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359'
CRYPTO_PRICE_COINS = {'polygon_pol', 'eth', 'bep20_bnb'}

DEFAULT_TRACKING_ENDPOINT = 'https://2530gateway.com/wp-json/ipt/v1/track'
DEFAULT_TRACKING_KEY = 'highriskify-1c07b45fd6542e20c2f82b3ee9e5d4cc'
TRACKING_PLUGIN_VERSION = 'odoo-19.0.1.0.0-onramp-callback-order-tracking'

BACKEND_LOGO_URL = 'https://record.highriskify.com/wp-content/uploads/2026/05/HighRiskify.jpg'
HOSTED_CHECKOUT_LOGO_URL = 'https://record.highriskify.com/wp-content/uploads/2026/05/ChatGPT-Image-May-24-2026-12_22_09-AM-e1779564292657.png'
FRONTEND_PAYMENT_LOGO_URL = 'https://record.highriskify.com/wp-content/uploads/2026/05/payment-1.png'
FRONTEND_PAYMENT_LOGO_WIDTH = 338
FRONTEND_PAYMENT_LOGO_HEIGHT = 22

DEFAULT_CHECKOUT_HEADING = 'Complete Your Purchase'
DEFAULT_CHECKOUT_SECURE_TEXT = 'Secure & Encrypted Payment'
DEFAULT_CHECKOUT_DESCRIPTION = 'Please follow the hosted checkout instructions carefully. To avoid transaction failure, do not change values on the payment page. Once the configured checkout workflow reports a completed transaction, the original merchant website will be notified automatically.'
