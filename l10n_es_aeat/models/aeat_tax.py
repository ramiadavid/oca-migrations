# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl
import traceback

from odoo import fields, models, api


class AeatTax(models.Model):
    _name = "aeat.tax"
    _description = "AEAT Tax"
    _order = "name"

    name = fields.Char()
    xmlid = fields.Char()

    @api.model
    def update_taxes(self):
        try:
            chart_template = self.env["account.chart.template"].sudo()
            taxes = {}
            data = chart_template._parse_csv("es_common", "account.tax", "l10n_es")
            for key in data:
                taxes[key] = data[key].get('description@es') or data[key].get('description') or data[key].get('name')
            self.create_or_remove_taxes(taxes)
        except:
            traceback.print_exc()
            raise

    def create_or_remove_taxes(self, data):
        taxes = self.env['aeat.tax'].search([])
        taxes.filtered(lambda x: x.xmlid not in data).unlink()
        taxes = taxes.exists()
        for key in data:
            tax = taxes.filtered(lambda x: x.xmlid == key)
            if tax:
                tax.update({
                    "name": data[key]
                })
            else:
                tax = tax.create({
                    "xmlid": key,
                    "name": data[key]
                })
                self.env["ir.model.data"].create(
                    {
                        "name": key,
                        "module": "l10n_es_aeat",
                        "model": "aeat.tax",
                        "res_id": tax.id,
                        "noupdate": True
                    }
                )
