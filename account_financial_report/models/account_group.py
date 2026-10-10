# © 2018 Forest and Biomass Romania SA
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# This file recreates the ``account.group`` model removed from Odoo core
# in version 20.0. The implementation is copied from Odoo 19.0
# (odoo/addons/account/models/account_account.py, class AccountGroup)
# with the extra reporting helpers historically provided by this module.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain
from odoo.tools import SQL


class AccountGroup(models.Model):
    _name = "account.group"
    _description = "Account Group"
    _order = "code_prefix_start"
    _check_company_auto = True
    _check_company_domain = models.check_company_domain_parent_of

    parent_id = fields.Many2one(
        "account.group",
        index=True,
        ondelete="cascade",
        readonly=True,
        check_company=True,
    )
    name = fields.Char(required=True, translate=True)
    code_prefix_start = fields.Char(
        compute="_compute_code_prefix_start",
        readonly=False,
        store=True,
        precompute=True,
    )
    code_prefix_end = fields.Char(
        compute="_compute_code_prefix_end",
        readonly=False,
        store=True,
        precompute=True,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company.root_id,
    )

    _check_length_prefix = models.Constraint(
        "CHECK(char_length(COALESCE(code_prefix_start, '')) "
        "= char_length(COALESCE(code_prefix_end, '')))",
        "The length of the starting and the ending code prefix must be the same",
    )

    group_child_ids = fields.One2many(
        comodel_name="account.group", inverse_name="parent_id", string="Child Groups"
    )
    level = fields.Integer(compute="_compute_level", recursive=True)
    account_ids = fields.One2many(
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
    complete_name = fields.Char(
        "Full Name", compute="_compute_complete_name", recursive=True
    )
    complete_code = fields.Char(
        "Full Code", compute="_compute_complete_code", recursive=True
    )

    @api.depends("code_prefix_start")
    def _compute_code_prefix_end(self):
        for group in self:
            if not group.code_prefix_end or (
                group.code_prefix_start
                and group.code_prefix_end < group.code_prefix_start
            ):
                group.code_prefix_end = group.code_prefix_start

    @api.depends("code_prefix_end")
    def _compute_code_prefix_start(self):
        for group in self:
            if not group.code_prefix_start or (
                group.code_prefix_end
                and group.code_prefix_start > group.code_prefix_end
            ):
                group.code_prefix_start = group.code_prefix_end

    @api.depends("code_prefix_start", "code_prefix_end")
    def _compute_display_name(self):
        for group in self:
            prefix = group.code_prefix_start and str(group.code_prefix_start)
            if prefix and group.code_prefix_end != group.code_prefix_start:
                prefix += "-" + str(group.code_prefix_end)
            group.display_name = " ".join(filter(None, [prefix, group.name]))

    @api.model
    def _search_display_name(self, operator, value):
        if operator in Domain.NEGATIVE_OPERATORS:
            return NotImplemented
        if operator == "in":
            return [
                "|",
                ("code", "in", [(name or "").split(" ")[0] for name in value]),
                ("name", "in", value),
            ]
        if operator == "ilike" and isinstance(value, str):
            return [
                "|",
                ("code_prefix_start", "=like", value + "%"),
                ("name", operator, value),
            ]
        return [("name", operator, value)]

    @api.constrains("code_prefix_start", "code_prefix_end")
    def _constraint_prefix_overlap(self):
        self.flush_model()
        query = """
            SELECT other.id FROM account_group this
            JOIN account_group other
              ON char_length(other.code_prefix_start)
                = char_length(this.code_prefix_start)
             AND other.id != this.id
             AND other.company_id = this.company_id
             AND (
                other.code_prefix_start <= this.code_prefix_start
                AND this.code_prefix_start <= other.code_prefix_end
                OR
                other.code_prefix_start >= this.code_prefix_start
                AND this.code_prefix_end >= other.code_prefix_start
            )
            WHERE this.id IN %(ids)s
        """
        self.env.cr.execute(query, {"ids": tuple(self.ids)})
        res = self.env.cr.fetchall()
        if res:
            raise ValidationError(
                _("Account Groups with the same granularity can't overlap")
            )

    def _sanitize_vals(self, vals):
        if (
            vals.get("code_prefix_start")
            and "code_prefix_end" in vals
            and not vals["code_prefix_end"]
        ):
            del vals["code_prefix_end"]
        if (
            vals.get("code_prefix_end")
            and "code_prefix_start" in vals
            and not vals["code_prefix_start"]
        ):
            del vals["code_prefix_start"]
        return vals

    @api.constrains("parent_id")
    def _check_parent_not_circular(self):
        if self._has_cycle():
            raise ValidationError(_("You cannot create recursive groups."))

    @api.model_create_multi
    def create(self, vals_list):
        groups = super().create([self._sanitize_vals(vals) for vals in vals_list])
        groups._adapt_parent_account_group()
        return groups

    def write(self, vals):
        res = super().write(self._sanitize_vals(vals))
        if "code_prefix_start" in vals or "code_prefix_end" in vals:
            self._adapt_parent_account_group()
        return res

    def unlink(self):
        for record in self:
            children_ids = self.env["account.group"].search(
                [("parent_id", "=", record.id)]
            )
            children_ids.write({"parent_id": record.parent_id.id})
        return super().unlink()

    def _adapt_parent_account_group(self, company=None):
        """Ensure consistency of the hierarchy of account groups.

        Find and set the most specific parent for each group.
        The most specific is the one with the longest prefixes and with
        the starting prefix being smaller than the child prefixes and
        the ending prefix being greater.
        """
        if self.env.context.get("delay_account_group_sync"):
            return

        company_ids = company.ids if company else self.company_id.ids
        if not company_ids:
            return

        self.flush_model()
        query = SQL(
            """
            WITH relation AS (
                SELECT DISTINCT ON (child.id)
                       child.id AS child_id,
                       parent.id AS parent_id
                  FROM account_group parent
            RIGHT JOIN account_group child
                    ON char_length(parent.code_prefix_start)
                        < char_length(child.code_prefix_start)
                   AND parent.code_prefix_start
                        <= LEFT(child.code_prefix_start,
                                char_length(parent.code_prefix_start))
                   AND parent.code_prefix_end
                        >= LEFT(child.code_prefix_end,
                                char_length(parent.code_prefix_end))
                   AND parent.id != child.id
                   AND parent.company_id = child.company_id
                 WHERE child.company_id IN %s
              ORDER BY child.id, char_length(parent.code_prefix_start) DESC
            )
            UPDATE account_group child
               SET parent_id = relation.parent_id
              FROM relation
             WHERE child.id = relation.child_id
               AND child.parent_id IS DISTINCT FROM relation.parent_id
         RETURNING child.id
        """,
            tuple(company_ids),
        )
        self.env.cr.execute(query)

        updated_rows = self.env.cr.fetchall()
        if updated_rows:
            self.invalidate_model(["parent_id"])

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        """Forms complete name of location from parent location
        to child location."""
        for group in self:
            if group.parent_id.complete_name:
                group.complete_name = f"{group.parent_id.complete_name}/{group.name}"
            else:
                group.complete_name = group.name

    @api.depends("code_prefix_start", "code_prefix_end")
    def _compute_account_ids(self):
        """Retrieves every account from `self`.
        In Odoo 18 the group_id on account is not stored so it raises
        an error the one2many account_ids with inverse name group_id."""
        group_ids = self.ids
        self.account_ids = self.env["account.account"]
        if not group_ids:
            return
        group_ids = SQL(",".join(map(str, group_ids)))
        results = self.env.execute_query(
            SQL(
                """
        SELECT
        agroup.id AS group_id,
        STRING_AGG(DISTINCT account.id::text, ', ') as account_ids
        FROM  account_group agroup
        inner join account_account account
        ON agroup.code_prefix_start <= LEFT(%(code_store)s->>agroup.company_id::text,
        char_length(agroup.code_prefix_start))
        AND agroup.code_prefix_end >= LEFT(%(code_store)s->>agroup.company_id::text,
        char_length(agroup.code_prefix_end))
        WHERE agroup.id IN (%(group_ids)s)
        GROUP BY agroup.id
            """,
                code_store=SQL.identifier("account", "code_store"),
                group_ids=group_ids,
            )
        )
        group_by_code = dict(results)
        if not group_by_code:
            return
        for record in self:
            if group_by_code.get(record.id, ""):
                record.account_ids = list(
                    map(int, group_by_code.get(record.id, "").split(", "))
                )

    @api.depends("code_prefix_start", "parent_id.complete_code")
    def _compute_complete_code(self):
        """Forms complete code of location from parent location
        to child location."""
        for group in self:
            if group.parent_id.complete_code:
                group.complete_code = (
                    f"{group.parent_id.complete_code}/{group.code_prefix_start}"
                )
            else:
                group.complete_code = group.code_prefix_start

    @api.depends("parent_id", "parent_id.level")
    def _compute_level(self):
        for group in self:
            if not group.parent_id:
                group.level = 0
            else:
                group.level = group.parent_id.level + 1

    @api.depends(
        "group_child_ids.compute_account_ids",
    )
    def _compute_group_accounts(self):
        for one in self:
            one.compute_account_ids = (
                one.account_ids | one.group_child_ids.compute_account_ids
            )
