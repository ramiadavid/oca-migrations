# Copyright 2026 ProcessControl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3).
"""Brings ``bank_id`` back to ``res.partner.bank``.

In 19.0 ``bank_name`` and ``bank_bic`` were related fields on ``bank_id``.
Odoo 20.0 turned them into plain Char fields that core code writes directly,
so they are left alone here: ``bank_id`` is kept as the directory link and its
values are copied over whenever it is set.
"""

from odoo import api, fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    bank_id = fields.Many2one("res.bank", string="Bank", index="btree_not_null")

    def _bank_vals_from_bank_id(self, bank):
        """Values mirrored from the directory onto the plain Char fields."""
        if not bank:
            return {}
        return {"bank_name": bank.name, "bank_bic": bank.bic}

    @api.onchange("bank_id")
    def _onchange_bank_id(self):
        vals = self._bank_vals_from_bank_id(self.bank_id)
        if vals:
            self.update(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("bank_id"):
                bank = self.env["res.bank"].browse(vals["bank_id"])
                vals.update(
                    {key: value for key, value in self._bank_vals_from_bank_id(bank).items() if not vals.get(key)}
                )
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("bank_id"):
            bank = self.env["res.bank"].browse(vals["bank_id"])
            vals.update({key: value for key, value in self._bank_vals_from_bank_id(bank).items() if not vals.get(key)})
        return super().write(vals)
