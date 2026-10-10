# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestBank(BaseCommon):
    _test_user_groups = None  # Run as admin for Odoo 20 compatibility

    def test_bank(self):
        bank_account = self.env["res.partner.bank"].create(
            {
                "account_number": "BE32121212121212",
                "bank_name": "Test Bank",
                "bank_bic": "FIDCFR21XXX",
                "partner_id": self.env.ref("base.main_partner").id,
            }
        )
        with self.assertRaises(ValidationError):
            bank_account.bank_bic = "TEST"
