from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    keep_partner_bank_without_payment_mode = fields.Boolean(
        string="Keep Partner Bank Without Payment Mode",
        default=True,
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    keep_partner_bank_without_payment_mode = fields.Boolean(
        related="company_id.keep_partner_bank_without_payment_mode",
        readonly=False,
    )
