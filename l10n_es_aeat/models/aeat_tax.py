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
            processed = []
            taxes = {}
            for company in self.env["res.company"].search([]).sudo():
                template = company.chart_template
                if template and template not in processed:
                    data = chart_template._get_chart_template_data(template)
                    processed.append(template)
                    for key in data["account.tax"]:

                        taxes[key] = data["account.tax"][key].get('description@es') or data["account.tax"][key]['description']
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
