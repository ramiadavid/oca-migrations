# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_supplierinfo_discount2 = fields.Float(
        string='Default Supplier Discount 2 (%)',
        digits=(4, 2),
        help="This value will be used as the default one, for each new "
             "supplierinfo line depending on that supplier.",
    )
    default_supplierinfo_discount3 = fields.Float(
        string='Default Supplier Discount 3 (%)',
        digits=(4, 2),
        help="This value will be used as the default one, for each new "
             "supplierinfo line depending on that supplier.",
    )
