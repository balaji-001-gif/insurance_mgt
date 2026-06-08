frappe.ui.form.on('Insurance Policy', {
    refresh(frm) {
        if (!frm.is_new()) {
            // Add "Recommend Policies" button
            frm.add_custom_button(__('Recommend Policies'), () => {
                frm.call('get_recommendations').then(r => {
                    if (r.message) {
                        const recommendations = Array.isArray(r.message)
                            ? r.message
                            : [r.message];
                        frappe.msgprint({
                            title: __('Policy Recommendations'),
                            indicator: 'green',
                            message: recommendations.join('<br><br>'),
                        });
                    }
                });
            });

            // Add "Send Quote" button
            frm.add_custom_button(__('Send Quote'), () => {
                frm.call('send_quote').then(r => {
                    if (r.message) {
                        frappe.msgprint(__('Quote sent successfully!'));
                    }
                });
            });
        }
    },

    // Auto-refresh risk score display when fields change
    policy_type(frm) {
        if (!frm.is_new()) {
            frm.refresh_field('risk_score');
        }
    },

    premium(frm) {
        if (!frm.is_new()) {
            frm.refresh_field('risk_score');
        }
    },
});
