(function () {
    'use strict';

    const LOGO_SRC = 'https://record.highriskify.com/wp-content/uploads/2026/05/payment-1.png';
    const FALLBACK_SRC = '/highriskify_onramp/static/src/img/paymentlogo_338x22.png';
    const PROVIDER_TEXT = 'highriskify';
    const PROVIDER_CODE = 'highriskify_onramp';

    function makeLogo() {
        const img = document.createElement('img');
        img.className = 'o_highriskify_gateway_logo_inline';
        img.src = LOGO_SRC;
        img.alt = 'Accepted payment methods';
        img.width = 338;
        img.height = 22;
        img.loading = 'lazy';
        img.referrerPolicy = 'no-referrer';
        img.onerror = function () {
            if (img.src !== FALLBACK_SRC) {
                img.src = FALLBACK_SRC;
            }
        };
        return img;
    }

    function closestPaymentContainer(node) {
        if (!node || !node.closest) return null;
        return node.closest('.o_payment_option, .o_payment_method, .list-group-item, .card, .form-check, li, label') || node.parentElement;
    }

    function findHighRiskifyContainers() {
        const containers = new Set();
        document.querySelectorAll(`[data-provider-code="${PROVIDER_CODE}"], [data-payment-option-code="${PROVIDER_CODE}"], input[value="${PROVIDER_CODE}"]`).forEach((node) => {
            const container = closestPaymentContainer(node);
            if (container) containers.add(container);
        });
        document.querySelectorAll('label, .o_payment_option, .o_payment_method, .list-group-item, .card, .form-check').forEach((node) => {
            const text = (node.textContent || '').toLowerCase();
            if (text.includes(PROVIDER_TEXT)) {
                const container = closestPaymentContainer(node);
                if (container) containers.add(container);
            }
        });
        const result = Array.from(containers);
        return result.filter((container) => !result.some((other) => other !== container && container.contains(other)));
    }

    function applyLogoToContainer(container) {
        if (!container) return;

        // Remove legacy appended strips/messages if present.
        container.querySelectorAll('.o_highriskify_gateway_logos, .o_highriskify_payment_message').forEach((el) => el.remove());

        let img = container.querySelector('img.o_highriskify_gateway_logo_inline');
        if (!img) {
            // Prefer replacing an existing payment option image instead of appending a second logo.
            const existingImg = Array.from(container.querySelectorAll('img')).find((el) => !el.classList.contains('o_highriskify_gateway_logo_inline'));
            if (existingImg) {
                img = existingImg;
                img.classList.add('o_highriskify_gateway_logo_inline');
            } else {
                img = makeLogo();
                const titleLikeNode = Array.from(container.querySelectorAll('label, span, strong, div')).find((el) => (el.textContent || '').toLowerCase().includes(PROVIDER_TEXT));
                if (titleLikeNode && titleLikeNode.parentElement) {
                    titleLikeNode.parentElement.insertBefore(img, titleLikeNode.parentElement.firstChild);
                } else {
                    container.insertBefore(img, container.firstChild);
                }
            }
        }

        img.src = LOGO_SRC;
        img.alt = 'Accepted payment methods';
        img.width = 338;
        img.height = 22;
        img.loading = 'lazy';
        img.referrerPolicy = 'no-referrer';
        img.onerror = function () {
            if (img.src !== FALLBACK_SRC) {
                img.src = FALLBACK_SRC;
            }
        };
    }

    function injectHighRiskifyLogos() {
        findHighRiskifyContainers().forEach(applyLogoToContainer);
    }

    function start() {
        injectHighRiskifyLogos();
        const observer = new MutationObserver(() => injectHighRiskifyLogos());
        observer.observe(document.documentElement, { childList: true, subtree: true });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
})();
