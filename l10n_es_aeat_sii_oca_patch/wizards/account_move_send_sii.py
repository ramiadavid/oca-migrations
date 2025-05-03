from odoo import fields, models


class SendSIIWizard(models.TransientModel):
    _inherit = "wizard.send.sii"
    _description = "Send SII Wizard"

    def default_get(self, fields):
        res = super().default_get(fields)
        active_ids = self.env.context.get("active_ids", [])
        res.update(
            {
                "account_move_ids": [(6, 0, active_ids)],
            }
        )
        return res
