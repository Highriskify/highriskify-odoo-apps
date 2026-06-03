/** @odoo-module */

import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { PaymentHighriskifyPosCrypto } from "@highriskify_pos_crypto/app/payment_highriskify_pos_crypto";

register_payment_method("highriskify_pos_crypto", PaymentHighriskifyPosCrypto);
