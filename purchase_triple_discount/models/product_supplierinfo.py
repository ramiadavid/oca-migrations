# Copyright 2019 Tecnativa - David Vidal
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    discount2 = fields.Float(
        string="Discount 2 (%)",
        digits="Discount",
    )
    discount3 = fields.Float(
        string="Discount 3 (%)",
        digits="Discount",
    )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        """Apply the default supplier discounts of the selected supplier"""
        for supplierinfo in self.filtered("partner_id"):
            supplierinfo.discount2 = (
                supplierinfo.partner_id.default_supplierinfo_discount2
            )
            supplierinfo.discount3 = (
                supplierinfo.partner_id.default_supplierinfo_discount3
            )
        return super().onchange_partner_id()

    @api.model
    def _get_po_to_supplierinfo_synced_fields(self):
        res = super()._get_po_to_supplierinfo_synced_fields()
        res += ["discount2", "discount3"]
        return res
