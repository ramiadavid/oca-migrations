# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import re

from odoo import api, models
from odoo.exceptions import ValidationError

BIC_REGEX = re.compile(r"[A-Z]{6}[A-Z2-9][A-NP-Z0-9]([A-Z0-9]{3})?$")


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    @api.constrains("bank_bic")
    def _check_bic(self):
        invalid = self.filtered(
            lambda r: r.bank_bic and not BIC_REGEX.match(r.bank_bic)
        )
        if invalid:
            raise ValidationError(
                self.env._(
                    "The following Bank Identifier Codes (BIC) do not respect "
                    "the SEPA pattern:\n%(bic_list)s\n\nSEPA pattern: %(sepa_pattern)s",
                    bic_list="\n".join(invalid.mapped("bank_bic")),
                    sepa_pattern=BIC_REGEX.pattern,
                )
            )
