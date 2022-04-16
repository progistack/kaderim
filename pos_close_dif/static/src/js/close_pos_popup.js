odoo.define('pos_hide_refund.NumpadWidget', function(require) {
    'use strict';

    const NumpadWidget = require('point_of_sale.NumpadWidget');
    const Registries = require('point_of_sale.Registries');

    const PosHideRefundNumpadWidget = NumpadWidget => class extends NumpadWidget {
         mounted() {
                console.log("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                this.env.pos.on('change:cashier', () => {
                    const cashier = this.env.pos.get('cashier') || this.env.pos.get_cashier()
                    if (this.env.pos.config.hide_refund && cashier.role != 'manager') {
                        $("#refund_button" ).hide();
                        console.log("##############################################")
                    }else{
                        $("#refund_button" ).show();
                    }
                })
         }
         changeMode(mode) {
            const cashier = this.env.pos.get('cashier') || this.env.pos.get_cashier()
            if (this.env.pos.config.hide_refund && cashier.role != 'manager') {
                $("#refund_button" ).hide();
                console.log("##############################################")
            }
            if (!this.hasPriceControlRights && mode === 'price') {
                return;
            }
            if (!this.hasManualDiscount && mode === 'discount') {
                return;
            }
            this.trigger('set-numpad-mode', { mode });
        }

    };

    Registries.Component.extend(NumpadWidget, PosHideRefundNumpadWidget);

    return PosHideRefundNumpadWidget;
 });