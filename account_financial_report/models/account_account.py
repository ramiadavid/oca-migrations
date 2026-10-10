# © 2018 Forest and Biomass Romania SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
"""Odoo 20.0 removed ``account.group``: the chart of accounts is now a tree of
``account.account`` records linked by ``parent_id``. The helpers the reports
used to read from the group model are rebuilt here on top of that hierarchy,
where a "group" is simply an account that has children.
"""

from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    group_child_ids = fields.One2many(
        comodel_name="account.account",
        inverse_name="parent_id",
        string="Child Accounts",
    )
    is_account_group = fields.Boolean(
        compute="_compute_is_account_group",
        search="_search_is_account_group",
        string="Is a group",
    )
    level = fields.Integer(compute="_compute_level", recursive=True)
    account_ids = fields.Many2many(
        comodel_name="account.account",
        compute="_compute_account_ids",
        string="Accounts",
        store=False,
    )
    compute_account_ids = fields.Many2many(
        "account.account",
        recursive=True,
        compute="_compute_group_accounts",
        string="Compute accounts",
        store=False,
    )
    complete_name = fields.Char("Full Name", compute="_compute_complete_name", recursive=True)
    complete_code = fields.Char("Full Code", compute="_compute_complete_code", recursive=True)

    @api.depends("group_child_ids")
    def _compute_is_account_group(self):
        for account in self:
            account.is_account_group = bool(account.group_child_ids)

    @api.model
    def _search_is_account_group(self, operator, value):
        if operator not in ("in", "not in"):
            raise NotImplementedError(self.env._("Unsupported operator"))
        parents = self.with_context(active_test=False).search([("parent_id", "!=", False)])
        domain = [("id", "in", parents.parent_id.ids)]
        if (operator == "in") != bool(value):
            domain = ["!", *domain]
        return domain

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        """Forms complete name of location from parent location to child location."""
        for account in self:
            if account.parent_id.complete_name:
                account.complete_name = f"{account.parent_id.complete_name}/{account.name}"
            else:
                account.complete_name = account.name

    @api.depends("group_child_ids")
    def _compute_account_ids(self):
        """Direct leaf children of the account, i.e. the accounts it totals."""
        for account in self:
            account.account_ids = account.group_child_ids.filtered(lambda child: not child.group_child_ids)

    @api.depends("code", "parent_id.complete_code")
    def _compute_complete_code(self):
        """Forms complete code of location from parent location to child location."""
        for account in self:
            if account.parent_id.complete_code:
                account.complete_code = f"{account.parent_id.complete_code}/{account.code}"
            else:
                account.complete_code = account.code

    @api.depends("parent_id", "parent_id.level")
    def _compute_level(self):
        for account in self:
            if not account.parent_id:
                account.level = 0
            else:
                account.level = account.parent_id.level + 1

    @api.depends(
        "group_child_ids.compute_account_ids",
    )
    def _compute_group_accounts(self):
        for one in self:
            one.compute_account_ids = one.account_ids | one.group_child_ids.compute_account_ids
