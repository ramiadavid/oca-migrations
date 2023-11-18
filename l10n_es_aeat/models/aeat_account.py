# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl
import traceback

from odoo import fields, models, api


class AeatTax(models.Model):
    _name = "aeat.account"
    _description = "AEAT Account"
    _order = "name"

    name = fields.Char()
    xmlid = fields.Char()

    @api.model
    def update_accounts(self):
        try:
            chart_template = self.env["account.chart.template"].sudo()
            processed = []
            accounts = {}
            for company in self.env["res.company"].search([]).sudo():
                template = company.chart_template
                if template and template not in processed:
                    data = chart_template._get_chart_template_data(template)
                    processed.append(template)
                    for key in data["account.account"]:
                        accounts[key] = "%s - %s" % (data["account.account"][key]['code'], data["account.account"][key].get('name@es') or data["account.account"][key]['name'])
            self.create_or_remove_accounts(accounts)
        except:
            traceback.print_exc()
            raise

    def create_or_remove_accounts(self, data):
        accounts = self.env['aeat.account'].search([])
        accounts.filtered(lambda x: x.xmlid not in data).unlink()
        for key in data:
            account = accounts.filtered(lambda x: x.xmlid == key)
            if account:
                account.update({
                    "name": data[key]
                })
            else:
                account = account.create({
                    "xmlid": key,
                    "name": data[key]
                })
                self.env["ir.model.data"].create(
                    {
                        "name": key,
                        "module": "l10n_es_aeat",
                        "model": "aeat.account",
                        "res_id": account.id,
                        "noupdate": True
                    }
                )
