(function () {
    'use strict';

    const PROVIDER_TEXT = 'highriskify onramp';
    const LOGO_SRC = 'https://record.highriskify.com/wp-content/uploads/2026/05/HighRiskify.jpg';
    const FALLBACK_SRC = '/highriskify_onramp/static/src/img/highriskify_backend_logo_150.png';

    function configureImg(img, size) {
        if (!img) return;
        img.src = LOGO_SRC;
        img.alt = 'HighRiskify';
        img.referrerPolicy = 'no-referrer';
        img.loading = 'lazy';
        img.classList.add('o_highriskify_backend_logo_img');
        img.classList.remove('o_highriskify_backend_logo_card', 'o_highriskify_backend_logo_form');
        if (size === 'card') img.classList.add('o_highriskify_backend_logo_card');
        if (size === 'form') img.classList.add('o_highriskify_backend_logo_form');
        img.onerror = function () {
            if (img.src !== FALLBACK_SRC) img.src = FALLBACK_SRC;
        };
    }

    function createImg(size) {
        const img = document.createElement('img');
        configureImg(img, size);
        return img;
    }

    function patchCard(card) {
        if (!card) return;
        const text = (card.textContent || '').toLowerCase();
        if (!text.includes(PROVIDER_TEXT)) return;

        let img = card.querySelector('img');
        if (img) {
            configureImg(img, 'card');
        } else {
            const left = card.querySelector('.o_kanban_image, .oe_kanban_global_click, .card-body, .o_kanban_record_body, .o_payment_provider') || card;
            img = createImg('card');
            left.insertBefore(img, left.firstChild);
        }
    }

    function patchForm() {
        const form = document.querySelector('.o_form_view');
        if (!form) return;
        const text = (form.textContent || '').toLowerCase();
        if (!text.includes(PROVIDER_TEXT)) return;

        let target = form.querySelector('.oe_avatar, .o_field_widget[name="image_128"], .o_field_widget[name="image_1920"], .o_field_image, .o_image_wrapper');
        if (!target) {
            const sheet = form.querySelector('.o_form_sheet');
            if (!sheet) return;
            target = document.createElement('div');
            target.className = 'o_highriskify_backend_logo_box';
            sheet.appendChild(target);
        }
        let img = target.querySelector('img');
        if (!img) {
            target.innerHTML = '';
            img = createImg('form');
            target.appendChild(img);
        } else {
            configureImg(img, 'form');
        }
        target.classList.add('o_highriskify_backend_logo_target');
    }

    function hideLegacyTrackingFields() {
        // Safety net for databases upgraded from older builds where a stale
        // inherited view still injected the internal tracking controls.
        const form = document.querySelector('.o_form_view');
        if (!form) return;
        const text = (form.textContent || '').toLowerCase();
        if (!text.includes('highriskify onramp')) return;

        document.querySelectorAll('.o_horizontal_separator, .o_group_header, h2, h3, h4').forEach((node) => {
            const nodeText = (node.textContent || '').toLowerCase();
            if (nodeText.includes('optional tracking')) {
                node.style.display = 'none';
            }
        });

        document.querySelectorAll('[name="highriskify_tracking_enabled"], [name="highriskify_tracking_endpoint"], [name="highriskify_tracking_key"]').forEach((field) => {
            const fieldWidget = field.closest('.o_field_widget') || field;
            const fieldCell = fieldWidget.closest('.o_cell') || fieldWidget.closest('.o_wrap_field') || fieldWidget.parentElement || fieldWidget;
            fieldCell.style.display = 'none';

            const previous = fieldCell.previousElementSibling;
            if (previous && /tracking|ipt/i.test(previous.textContent || '')) {
                previous.style.display = 'none';
            }

            const row = fieldCell.closest('.row, .o_row');
            if (row && /tracking|ipt/i.test(row.textContent || '')) {
                row.style.display = 'none';
            }
        });
    }

    function run() {
        document.querySelectorAll('.o_kanban_record, .oe_kanban_card, .o_kanban_renderer .card').forEach(patchCard);
        patchForm();
        hideLegacyTrackingFields();
    }

    function start() {
        run();
        const observer = new MutationObserver(() => run());
        observer.observe(document.documentElement, { childList: true, subtree: true });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
})();
