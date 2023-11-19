# Copyright 2013-2016 Camptocamp SA (Yannick Vaucher)
# Copyright 2004-2016 Odoo S.A. (www.odoo.com)
# Copyright 2015-2016 Akretion
# (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import calendar

from dateutil.relativedelta import relativedelta

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round


class AccountPaymentTermHoliday(models.Model):
    _name = "account.payment.term.holiday"
    _description = "Payment Term Holidays"

    payment_id = fields.Many2one(comodel_name="account.payment.term")
    holiday = fields.Date(required=True)
    date_postponed = fields.Date(string="Postponed date", required=True)

    @api.constrains("holiday", "date_postponed")
    def check_holiday(self):
        for record in self:
            if fields.Date.from_string(
                record.date_postponed
            ) <= fields.Date.from_string(record.holiday):
                raise ValidationError(
                    _("Holiday %s can only be postponed into the future")
                    % record.holiday
                )
            if (
                record.search_count(
                    [
                        ("payment_id", "=", record.payment_id.id),
                        ("holiday", "=", record.holiday),
                    ]
                )
                > 1
            ):
                raise ValidationError(
                    _("Holiday %s is duplicated in current payment term")
                    % record.holiday
                )
            if (
                record.search_count(
                    [
                        ("payment_id", "=", record.payment_id.id),
                        "|",
                        ("date_postponed", "=", record.holiday),
                        ("holiday", "=", record.date_postponed),
                    ]
                )
                >= 1
            ):
                raise ValidationError(
                    _("Date %s cannot is both a holiday and a Postponed date")
                    % record.holiday
                )


class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    amount_round = fields.Float(
        string="Amount Rounding",
        digits="Account",
        help="Sets the amount so that it is a multiple of this value.",
    )
    weeks = fields.Integer()
    nb_months = fields.Integer(string="Months")
    value = fields.Selection(
        selection_add=[
            ("percent_amount_untaxed", "Percent (Untaxed amount)"),
            ("fixed",),
        ],
        ondelete={"percent_amount_untaxed": lambda r: r.write({"value": "percent"})},
    )

    def _get_due_date(self, date_ref):
        """override to support weeks, months, apply holidays and payment days"""
        self.ensure_one()
        due_date = super()._get_due_date(date_ref) - relativedelta(days=self.nb_days)
        due_date = due_date + relativedelta(weeks=self.weeks)
        due_date = due_date + relativedelta(months=self.nb_months)
        due_date = due_date + relativedelta(days=self.nb_days)
        due_date = self.payment_id.apply_holidays(due_date)
        return self.payment_id.apply_payment_days(self, due_date)

    @api.constrains("value", "value_amount")
    def _check_value_amount_untaxed(self):
        for term_line in self:
            if (
                term_line.value == "percent_amount_untaxed"
                and not 0 <= term_line.value_amount <= 100
            ):
                raise ValidationError(
                    _(
                        "Percentages on the Payment Terms lines "
                        "must be between 0 and 100."
                    )
                )

    def compute_line_amount(self, total_amount, remaining_amount, precision_digits):
        """Compute the amount for a payment term line.
        In case of procent computation, use the payment
        term line rounding if defined

            :param total_amount: total balance to pay
            :param remaining_amount: total amount minus sum of previous lines
                computed amount
            :returns: computed amount for this line
        """
        self.ensure_one()
        if self.value == "fixed":
            return float_round(self.value_amount, precision_digits=precision_digits)
        elif self.value in ("percent", "percent_amount_untaxed"):
            amt = total_amount * self.value_amount / 100.0

            if abs(amt) > abs(remaining_amount):
                amt = remaining_amount

            if self == self.payment_id.line_ids[-1]:
                amt = remaining_amount

            if self.amount_round:
                amt = float_round(amt, precision_rounding=self.amount_round)
            return float_round(amt, precision_digits=precision_digits)
        return None

    def _decode_payment_days(self, days_char):
        # Admit space, dash and comma as separators
        days_char = days_char.replace(" ", "-").replace(",", "-")
        days_char = [x.strip() for x in days_char.split("-") if x]
        days = [int(x) for x in days_char]
        days.sort()
        return days

    @api.constrains("payment_days")
    def _check_payment_days(self):
        for record in self:
            if not record.payment_days:
                continue
            try:
                payment_days = record._decode_payment_days(record.payment_days)
                error = any(day <= 0 or day > 31 for day in payment_days)
            except Exception:
                error = True
            if error:
                raise exceptions.Warning(_("Payment days field format is not valid."))

    payment_days = fields.Char(
        string="Payment day(s)",
        help="Put here the day or days when the partner makes the payment. "
        "Separate each possible payment day with dashes (-), commas (,) "
        "or spaces ( ).",
    )


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    sequential_lines = fields.Boolean(
        default=False,
        help="Allows to apply a chronological order on lines.",
    )
    holiday_ids = fields.One2many(
        string="Holidays",
        comodel_name="account.payment.term.holiday",
        inverse_name="payment_id",
    )

    def apply_holidays(self, date):
        holiday = self.holiday_ids.search(
            [("payment_id", "=", self.id), ("holiday", "=", date)]
        )
        if holiday:
            return holiday.date_postponed
        return date

    def apply_payment_days(self, line, date):
        """Calculate the new date with days of payments"""
        if line.payment_days:
            payment_days = line._decode_payment_days(line.payment_days)
            if payment_days:
                new_date = None
                payment_days.sort()
                days_in_month = calendar.monthrange(date.year, date.month)[1]
                for day in payment_days:
                    if date.day <= day:
                        if day > days_in_month:
                            day = days_in_month
                        new_date = date + relativedelta(day=day)
                        break
                if not new_date:
                    day = payment_days[0]
                    if day > days_in_month:
                        day = days_in_month
                    new_date = date + relativedelta(day=day, months=1)
                return new_date
        return date

    @api.depends(
        "currency_id",
        "example_amount",
        "example_date",
        "line_ids.value",
        "line_ids.value_amount",
        "line_ids.nb_days",
        "line_ids.nb_months",
        "line_ids.weeks",
        "early_discount",
        "sequential_lines",
        "discount_percentage",
        "discount_days",
        "holiday_ids",
    )
    def _compute_example_preview(self):
        """adding depends for new customized fields"""
        return super()._compute_example_preview()

    def _compute_terms(
        self,
        date_ref,
        currency,
        company,
        tax_amount,
        tax_amount_currency,
        sign,
        untaxed_amount,
        untaxed_amount_currency,
    ):
        self.ensure_one()
        res = super()._compute_terms(
            date_ref,
            currency,
            company,
            tax_amount,
            tax_amount_currency,
            sign,
            untaxed_amount,
            untaxed_amount_currency,
        )
        company_currency = company.currency_id
        untaxed_amount_left = untaxed_amount
        untaxed_amount_currency_left = untaxed_amount_currency

        total_amount = remaining_amount = tax_amount + untaxed_amount
        total_amount_currency = remaining_amount_currency = (
            tax_amount_currency + untaxed_amount_currency
        )

        precision_digits = currency.decimal_places
        company_precision_digits = company_currency.decimal_places
        next_date = date_ref

        lines = {line: res["line_ids"][i] for i, line in enumerate(self.line_ids)}
        for line, term_vals in lines.items():
            if self.sequential_lines:
                next_date = line._get_due_date(next_date)
                term_vals["date"] = next_date

            if line.value == "fixed":
                line_amount = line.compute_line_amount(
                    total_amount, remaining_amount, precision_digits
                )
                company_line_amount = line.compute_line_amount(
                    total_amount, remaining_amount, company_precision_digits
                )
                term_vals["company_amount"] = sign * company_line_amount
                term_vals["foreign_amount"] = sign * line_amount
                remaining_amount -= line_amount
                remaining_amount_currency -= company_line_amount
            elif line.value == "percent":
                line_amount = line.compute_line_amount(
                    total_amount, remaining_amount, precision_digits
                )
                company_line_amount = line.compute_line_amount(
                    total_amount_currency,
                    remaining_amount_currency,
                    company_precision_digits,
                )
                term_vals["company_amount"] = company_line_amount
                term_vals["foreign_amount"] = line_amount
                remaining_amount -= line_amount
                remaining_amount_currency -= company_line_amount
            elif line.value == "percent_amount_untaxed":
                if company_currency != currency:
                    raise UserError(
                        _(
                            "Percentage of amount untaxed can't be used with foreign "
                            "currencies"
                        )
                    )

                line_amount = line.compute_line_amount(
                    untaxed_amount, untaxed_amount_left, precision_digits
                )
                company_line_amount = line.compute_line_amount(
                    untaxed_amount_currency,
                    untaxed_amount_currency_left,
                    company_precision_digits,
                )
                term_vals["company_amount"] = company_line_amount
                term_vals["foreign_amount"] = line_amount
                remaining_amount -= line_amount
                remaining_amount_currency -= company_line_amount
                untaxed_amount_left -= line_amount
                untaxed_amount_currency_left -= company_line_amount

        return res
