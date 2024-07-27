# Copyright 2018 QubiQ (http://www.qubiq.es)
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Invoice Triple Discount",
    "version": "18.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "QubiQ, Tecnativa, GRAP, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "summary": "Manage triple discount on invoice lines",
    "depends": ["account"],
    "excludes": [
        "account_global_discount",
    ],
    "post_init_hook": "post_init_hook",
    "data": ["report/invoice.xml", "views/account_move.xml"],
    "installable": True,
}
