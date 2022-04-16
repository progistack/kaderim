odoo.define('pos_hide_refund.NumpadWidget', function(require) {
    'use strict';

    const NumpadWidget = require('point_of_sale.NumpadWidget');
    const Registries = require('point_of_sale.Registries');

    const PosHideRefundNumpadWidget = NumpadWidget => class extends NumpadWidget {
         mounted() {
                this.env.pos.on('change:cashier', () => {
                    const cashier = this.env.pos.get('cashier') || this.env.pos.get_cashier()
                    if (this.env.pos.config.hide_refund && cashier.role != 'manager') {
                        $("#refund_button" ).hide();
                    }else{
                        $("#refund_button" ).show();
                    }
                })
         }

        willUnmount() {
            this.env.pos.on('change:cashier', null, this);
             const cashier = this.env.pos.get('cashier') || this.env.pos.get_cashier()
            if (this.env.pos.config.hide_refund && cashier.role != 'manager') {
                $("#refund_button" ).hide();
            }
        }
        get hasPriceControlRights() {
            const cashier = this.env.pos.get('cashier') || this.env.pos.get_cashier();
            if (this.env.pos.config.hide_refund && cashier.role != 'manager') {
                $("#refund_button" ).hide();
            };
            return (
                (!this.env.pos.config.restrict_price_control || cashier.role == 'manager') &&
                !this.props.disabledModes.includes('price')
            );
        }
         changeMode(mode) {
            const cashier = this.env.pos.get('cashier') || this.env.pos.get_cashier()
            if (this.env.pos.config.hide_refund && cashier.role != 'manager') {
                $("#refund_button" ).hide();
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