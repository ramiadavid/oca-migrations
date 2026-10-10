# Copyright 2021-2022 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    """20.0 cambio _select_additional_fields() (cadenas SQL) por
    _select_dict(table) ({campo: SQL} sobre una TableSQL de sale.order.line)."""

    _inherit = "sale.report"

    payment_mode_id = fields.Many2one(
        "account.payment.mode",
        string="Payment Mode",
        readonly=True,
    )

    def _select_dict(self, table):
        return super()._select_dict(table) | {
            "payment_mode_id": table.order_id.payment_mode_id,
        }
