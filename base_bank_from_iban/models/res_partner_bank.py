# Copyright 2017 Tecnativa - Carlos Dauden
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3).

import schwifty

from odoo import api, models
from odoo.tools.bank_account_number import _map_iban_template, format_account_number, normalize_account_number


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._add_bank_vals(vals) for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        self._add_bank_vals(vals)
        return super().write(vals)

    def _add_bank_vals(self, vals):
        if vals.get("account_number") and not vals.get("bank_id"):
            vals["bank_id"] = self._get_bank_from_iban(vals["account_number"]).id
        return vals

    @api.model
    def _get_bank_from_iban(self, account_number):
        try:
            iban = schwifty.IBAN(account_number)
            country_code = iban.country_code
            country = self.env["res.country"].search([("code", "=", country_code)])
            if iban.bank:
                vals = {
                    "name": iban.bank["name"],
                    "bic": iban.bank["bic"],
                    "code": iban.bank["bank_code"],
                    "country": country.id,
                }
                domain = [
                    ("code", "=", iban.bank["bank_code"]),
                    ("country", "=", country.id),
                ]
                bank = self.env["res.bank"].search(domain, limit=1)
                if bank:
                    for field in vals:
                        if not bank[field]:
                            bank[field] = vals[field]
                else:
                    bank = self.env["res.bank"].create(vals)
            else:
                bank = self.env["res.bank"]
        except (
            schwifty.exceptions.InvalidStructure,
            schwifty.exceptions.InvalidChecksumDigits,
        ):
            bank = self.env["res.bank"]
        return bank

    @api.onchange("account_number", "account_type")
    def _onchange_acc_number_base_bank_from_iban(self):
        if self.account_type != "iban":
            return
        account_number = format_account_number(self.env, normalize_account_number(self.account_number)).upper()
        country_code = self.account_number[:2].lower()
        iban_template = _map_iban_template[country_code]
        first_match = iban_template[2:].find("B") + 2
        last_match = iban_template.rfind("B") + 1
        bank_code = account_number[first_match:last_match].replace(" ", "")
        bank = self.env["res.bank"].search(
            [("code", "=", bank_code), ("country.code", "=", country_code.upper())],
            limit=1,
        )
        self.update({"bank_id": bank.id, "account_number": account_number})
