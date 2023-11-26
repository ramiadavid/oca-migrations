/** @odoo-module **/
import {patch} from "@web/core/utils/patch";
import {TreeEditor} from "@web/core/tree_editor/tree_editor";
import {Select} from "@web/core/tree_editor/tree_editor_components";
import {deserializeDate, deserializeDateTime, serializeDateTime, serializeDate} from "@web/core/l10n/dates";

function toDateTime(date, type, end) {
    if (type === "date") {
        return date
    }
    let jsDate = deserializeDate(date)
    if (end) {
        jsDate = luxon.DateTime.fromObject({
            ...jsDate.c,
            hour: 23,
            minute: 59,
            second: 59

        })
    } else {
        jsDate = luxon.DateTime.fromObject({
            ...jsDate.c,
            hour: 0,
            minute: 0,
            second: 0

        })
    }
    return serializeDateTime(jsDate)
}

function fromDateTime(date, type) {
    if (type === "date") {
        return date
    }
    return serializeDate(deserializeDateTime(date))
}

patch(TreeEditor.prototype, {
    setup() {
        super.setup()
    },
    getValueEditorInfo(node) {
        const fieldDef = this.getFieldDef(node.path);
        const info = super.getValueEditorInfo.apply(this, arguments)
        if (fieldDef && (fieldDef.type === "date" || fieldDef.type === "datetime") && node.operator === "daterange") {
            info.component = Select
        }
        const dateRanges = this.env.domain.dateRanges

        patch(info, {
            extractProps({value, update}) {
                const props = super.extractProps.apply(this, arguments)
                if (fieldDef && (fieldDef.type === "date" || fieldDef.type === "datetime") && node.operator === "daterange") {
                    let selected = dateRanges.find(range => range.date_start === fromDateTime(value[1], fieldDef.type) && range.date_end === fromDateTime(value[0], fieldDef.type))
                    if (!selected) {
                        selected = dateRanges[0]
                        update([toDateTime(selected.date_end, fieldDef.type,), toDateTime(selected.date_start, fieldDef.type, true)])
                    }

                    return {
                        options: dateRanges.map(dt => [dt.id, dt.name]),
                        update: (value) => {
                            const range = dateRanges.find(range => range.id === value)
                            update([toDateTime(range.date_end, fieldDef.type), toDateTime(range.date_start, fieldDef.type, true)])
                        },
                        value: selected.id
                    }

                }

                return props
            },
            isSupported(value) {
                if (node.operator === "daterange") {
                    return Array.isArray(value) && value.length === 2
                } else {
                    return super.isSupported.apply(this, arguments)
                }
            },
        })
        return info
    },

    updateLeafOperator(node, operator, negate) {
        super.updateLeafOperator.apply(this, arguments)
        const fieldDef = this.getFieldDef(node.path);
        const dateRanges = this.env.domain.dateRanges
        if (operator === "daterange" && dateRanges) {
            node.value = [toDateTime(dateRanges[0].date_end, fieldDef.type), toDateTime(dateRanges[0].date_start, fieldDef.type, true)]
            this.notifyChanges();
        }
    }
})
