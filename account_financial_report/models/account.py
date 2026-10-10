# © 2011 Guewen Baconnier (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).-
from odoo import api, fields, models
from odoo.tools import SQL


class AccountAccount(models.Model):
    _inherit = "account.account"

    centralized = fields.Boolean(
        help="If flagged, no details will be displayed in "
        "the General Ledger report (the webkit one only), "
        "only centralized amounts per period.",
    )
    # Restored from Odoo 19.0 core (removed in Odoo 20.0) so that
    # financial reports can keep grouping accounts by code prefix.
    group_id = fields.Many2one(
        "account.group",
        compute="_compute_account_group",
        help="Account prefixes can determine account groups.",
    )

    @api.depends_context("company")
    @api.depends("code")
    def _compute_account_group(self):
        accounts_with_code = self.filtered(lambda a: a.code)

        (self - accounts_with_code).group_id = False

        if not accounts_with_code:
            return

        codes = accounts_with_code.mapped("code")
        account_code_values = SQL(",".join(["(%s)"] * len(codes)), *codes)
        results = self.env.execute_query(
            SQL(
                """
                     SELECT DISTINCT ON (account_code.code)
                            account_code.code,
                            agroup.id AS group_id
                       FROM (VALUES %(account_code_values)s)
                            AS account_code (code)
                  LEFT JOIN account_group agroup
                         ON agroup.code_prefix_start
                            <= LEFT(account_code.code,
                                    char_length(agroup.code_prefix_start))
                            AND agroup.code_prefix_end
                            >= LEFT(account_code.code,
                                    char_length(agroup.code_prefix_end))
                            AND agroup.company_id = %(root_company_id)s
                   ORDER BY account_code.code,
                            char_length(agroup.code_prefix_start) DESC,
                            agroup.id
                """,
                account_code_values=account_code_values,
                root_company_id=self.env.company.root_id.id,
            )
        )
        group_by_code = dict(results)

        for account in accounts_with_code:
            account.group_id = group_by_code[account.code]
