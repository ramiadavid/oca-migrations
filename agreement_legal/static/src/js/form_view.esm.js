/** @odoo-module **/

import {usePlugin} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {FormController} from "@web/views/form/form_controller";
import {formView} from "@web/views/form/form_view";
import {ActionPlugin} from "@web/webclient/actions/action_plugin";

export class AgreementFormController extends FormController {
    setup() {
        super.setup();
        this.action = usePlugin(ActionPlugin);
        this.canCreateTemplate = this.props.context.default_is_template || false;
    }
    onClickCreateFromTemplate() {
        this.action.doAction("agreement_legal.create_agreement_from_template_action");
    }
}

export const AgreementFormView = {
    ...formView,
    Controller: AgreementFormController,
    // Los botones salen de una plantilla propia, como en las vistas kanban y lista:
    // asi el t-if de "Nuevo" solo afecta a esta vista y no a todos los formularios.
    buttonTemplate: "agreement_legal.FormViewButtons",
};

registry.category("views").add("agreement_template_form", AgreementFormView);
