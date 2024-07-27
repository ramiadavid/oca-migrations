# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        string="Payment mode",
        readonly=True,
    )

    def _select(self):
        return SQL("%s, move.payment_mode_id AS payment_mode_id", super()._select())
