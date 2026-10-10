import {Component, useProps} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class PriceHistoryWidget extends Component {
    // Owl 3: Component ya no trae `props`; sin esta linea `this.props` es undefined.
    props = useProps();

    setup() {
        super.setup();
        this.actionService = useService("action");
    }

    viewPriceHistory() {
        this.actionService.doAction("sale_order_line_price_history.sale_order_line_price_history_action", {
            additionalContext: {
                default_product_id: this.props.record.data.product_id.id,
                default_partner_id: this.props.record.data.order_partner_id.id,
                default_active_id: this.props.value,
                default_sale_order_line_id: this.props.value,
            },
            onClose: (value) => {
                if (value && "price_unit" in value) {
                    this.props.record.update(value);
                }
            },
        });
    }
}

PriceHistoryWidget.template = "sale_order_line_price_history.price_history_widget";
registry.category("view_widgets").add("sale_line_price_history_widget", {component: PriceHistoryWidget});
