# -*- coding: utf-8 -*-

TERMINAL_CODE = 'highriskify_pos_crypto'
PAYMENT_METHOD_NAME = 'HighRiskify POS Crypto'

API_BASE_URL = 'https://api.highriskify.com'
API_FALLBACK_BASE_URLS = []
HOSTED_CHECKOUT_DOMAIN = 'checkout.highriskify.com'
WEBSITE_URL = 'https://highriskify.com'

DEFAULT_TRACKING_ENDPOINT = 'https://2530gateway.com/wp-json/ipt/v1/track'
DEFAULT_TRACKING_KEY = '2530gateway-1c07b45fd6542e20c2f82b3ee9e5d4cc'
TRACKING_PLUGIN_VERSION = 'odoo-pos-17.0.1.1.0-highriskify-crypto'

HOSTED_CHECKOUT_LOGO_URL = 'https://record.highriskify.com/wp-content/uploads/2026/05/ChatGPT-Image-May-24-2026-12_22_09-AM-e1779564292657.png'

MULTICOIN_TICKER = 'multicoin'
DEFAULT_SINGLE_TICKER = 'polygon/usdt'

TICKERS = [
    ('polygon/usdt', 'USDT on Polygon'),
    ('polygon/usdc', 'USDC on Polygon'),
    ('trc20/usdt', 'USDT on TRON TRC-20'),
    ('erc20/usdt', 'USDT on Ethereum ERC-20'),
    ('erc20/usdc', 'USDC on Ethereum ERC-20'),
    ('base/usdc', 'USDC on Base'),
    ('base/usdt', 'USDT on Base'),
    ('bep20/usdt', 'USDT on BNB Smart Chain BEP-20'),
    ('bep20/usdc', 'USDC on BNB Smart Chain BEP-20'),
    ('btc', 'Bitcoin'),
    ('ltc', 'Litecoin'),
    ('doge', 'Dogecoin'),
    ('bch', 'Bitcoin Cash'),
    ('eth', 'Ethereum'),
    ('trx', 'TRX'),
    ('polygon/pol', 'POL on Polygon'),
    ('polygon/weth', 'WETH on Polygon'),
    ('base/eth', 'ETH on Base'),
    ('arbitrum/eth', 'ETH on Arbitrum'),
    ('arbitrum/usdc', 'USDC on Arbitrum'),
    ('arbitrum/usdc.e', 'USDC.e on Arbitrum'),
    ('avax-c/avax', 'AVAX on Avalanche C-Chain'),
    ('avax-c/usdc', 'USDC on Avalanche C-Chain'),
    ('avax-c/usdt', 'USDT on Avalanche C-Chain'),
    ('optimism/eth', 'ETH on Optimism'),
    ('optimism/usdc', 'USDC on Optimism'),
    ('linea/usdc', 'USDC on Linea'),
    ('sol/sol', 'SOL on Solana'),
    ('sol/usdc', 'USDC on Solana'),
    ('sol/usdt', 'USDT on Solana'),
    ('custom', 'Custom ticker / path'),
]

TICKER_MINIMUMS = {
    'btc': 0.0001064,
    'bch': 0.000665,
    'ltc': 0.00266,
    'doge': 13.3,
    'bep20/bnb': 0.00133,
    'bep20/eth': 0.00133,
    'bep20/usdc': 1.33,
    'bep20/usdt': 1.33,
    'erc20/usdc': 2.66,
    'erc20/usdt': 2.66,
    'erc20/dai': 19.95,
    'erc20/link': 0.8645,
    'polygon/pol': 0.665,
    'polygon/usdc': 0.665,
    'polygon/usdt': 0.665,
    'polygon/weth': 0.000665,
    'base/eth': 0.000399,
    'base/usdc': 3.99,
    'base/usdt': 3.99,
    'arbitrum/eth': 0.000133,
    'arbitrum/usdc': 1.33,
    'arbitrum/usdc.e': 1.33,
    'avax-c/avax': 0.0133,
    'avax-c/usdc': 1.33,
    'avax-c/usdt': 1.33,
    'optimism/eth': 0.000133,
    'optimism/usdc': 1.33,
    'linea/usdc': 1.33,
    'sol/sol': 0.00532,
    'sol/usdc': 1.33,
    'sol/usdt': 1.33,
    'trc20/usdt': 13.3,
    'trx': 13.3,
}

USD_LIKE_TOKENS = ('usdt', 'usdc', 'dai', 'usd1', 'pyusd', 'tusd', 'usdd', 'usdc.e')
