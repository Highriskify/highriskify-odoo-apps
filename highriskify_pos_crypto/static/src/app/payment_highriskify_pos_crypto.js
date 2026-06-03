/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

const POLL_INTERVAL_MS = 5000;
const MAX_POLL_ATTEMPTS = 180; // 15 minutes

export class PaymentHighriskifyPosCrypto extends PaymentInterface {
    setup() {
        super.setup(...arguments);
    }

    _getLine(cid) {
        const order = this.pos.get_order();
        return order.paymentlines.find((line) => line.cid === cid) || order.selected_paymentline;
    }

    _showError(message, title) {
        const props = {
            title: title || _t("HighRiskify POS Crypto"),
            body: message,
        };
        if (this.env.services.dialog) {
            this.env.services.dialog.add(AlertDialog, props);
        } else if (this.env.services.popup) {
            this.env.services.popup.add(AlertDialog, props);
        } else {
            window.alert(`${props.title}

${props.body}`);
        }
    }

    async _ormCall(model, method, args = [], kwargs = {}) {
        const orm = this.env.services.orm?.silent || this.env.services.orm;
        return await orm.call(model, method, args, kwargs);
    }

    async send_payment_request(cid) {
        await super.send_payment_request(...arguments);
        const order = this.pos.get_order();
        const line = this._getLine(cid);
        if (!line) {
            this._showError(_t("No payment line was selected."));
            return false;
        }
        if (line.amount <= 0) {
            this._showError(_t("HighRiskify POS Crypto cannot process a zero or negative amount."));
            line.set_payment_status("retry");
            return false;
        }

        // Open immediately from the cashier click to avoid browser popup blockers.
        const checkoutWindow = window.open("", "_blank");
        if (checkoutWindow) {
            checkoutWindow.opener = null;
        }
        line.set_payment_status("waiting");

        try {
            const partner = order.get_partner();
            const payload = {
                order_uid: order.uid,
                order_name: order.name,
                amount: line.amount,
                currency: this.pos.currency.name,
                partner_email: partner?.email || "",
                pos_config_id: this.pos.config.id,
                pos_session_id: this.pos.pos_session.id,
            };
            const data = await this._ormCall(
                "pos.payment.method",
                "highriskify_crypto_create_pos_payment",
                [[this.payment_method.id], payload]
            );

            if (!data || !data.tx_id || !data.checkout_url) {
                throw new Error(_t("HighRiskify did not return a POS crypto checkout URL."));
            }

            line.highriskify_pos_crypto_tx_id = data.tx_id;
            line.highriskify_pos_crypto_reference = data.reference;
            line.transaction_id = data.reference;
            line.set_payment_status("waitingCard");

            if (checkoutWindow) {
                checkoutWindow.location = data.checkout_url;
            } else {
                this._showError(
                    _t("Your browser blocked the crypto checkout popup. Allow popups for this site, then click Send again."),
                    _t("Popup blocked")
                );
                line.set_payment_status("retry");
                return false;
            }

            return await this._waitForConfirmation(line, data.tx_id, data.reference);
        } catch (error) {
            if (checkoutWindow && !checkoutWindow.closed) {
                checkoutWindow.close();
            }
            const message = error?.data?.message || error?.message || _t("Could not start HighRiskify POS Crypto checkout.");
            this._showError(message);
            line.set_payment_status("retry");
            return false;
        }
    }

    async _waitForConfirmation(line, txId, reference) {
        for (let attempt = 0; attempt < MAX_POLL_ATTEMPTS; attempt++) {
            await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
            let status;
            try {
                status = await this._ormCall(
                    "highriskify.pos.crypto.transaction",
                    "highriskify_crypto_check_status",
                    [txId]
                );
            } catch (error) {
                // Keep polling on temporary network problems.
                continue;
            }

            if (status?.state === "done") {
                line.transaction_id = status.txid_out || status.txid_in || reference;
                line.card_type = "HighRiskify Crypto";
                line.set_receipt_info(
                    `HighRiskify POS Crypto\nReference: ${reference}\nTXID: ${status.txid_out || status.txid_in || "-"}`
                );
                line.set_payment_status("done");
                return true;
            }
            if (["error", "cancel"].includes(status?.state)) {
                this._showError(status.message || _t("HighRiskify POS Crypto payment was not completed."));
                line.set_payment_status("retry");
                return false;
            }
        }

        this._showError(_t("HighRiskify POS Crypto is still pending. Please check the blockchain payment before validating the order."));
        line.set_payment_status("retry");
        return false;
    }

    async send_payment_cancel(order, cid) {
        await super.send_payment_cancel(...arguments);
        const line = this._getLine(cid);
        if (line?.highriskify_pos_crypto_tx_id) {
            try {
                await this._ormCall(
                    "highriskify.pos.crypto.transaction",
                    "highriskify_crypto_cancel_payment",
                    [line.highriskify_pos_crypto_tx_id]
                );
            } catch (error) {
                // The payment line will still be removed by Odoo if this resolves.
            }
        }
        return true;
    }
}
