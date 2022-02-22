# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountMove(models.Model):
    _inherit = "account.move"

    def get_taxes_values(self):
        vals = {}
        for line in self.invoice_line_ids:
            vals[line] = {
                'price_unit': line.price_unit,
                'discount': line.discount,
            }
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_unit *= (1 - (line.discount2 or 0.0) / 100.0)
            price_unit *= (1 - (line.discount3 or 0.0) / 100.0)
            line.update({
                'price_unit': price_unit,
                'discount': 0.0,
            })
        tax_grouped = super(AccountMove, self).get_taxes_values()
        for line in self.invoice_line_ids:
            line.update(vals[line])
        return tax_grouped




    def _get_computed_price_unit(self):
        for line in self:
            prev_price_unit = line.price_unit
            prev_discount = line.discount
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_unit *= (1 - (line.discount2 or 0.0) / 100.0)
            price_unit *= (1 - (line.discount3 or 0.0) / 100.0)
            line.update({
                'price_unit': price_unit,
                'discount': 0.0,
            })
            super(AccountMoveLine, line)._get_computed_price_unit()
            line.update({
                'price_unit': prev_price_unit,
                'discount': prev_discount,
            })


