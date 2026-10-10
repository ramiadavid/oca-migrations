# Copyright 2026 ProcessControl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3).
{
    "name": "Base Res Bank (compatibility)",
    "summary": "Restores the res.bank directory removed in Odoo 20.0",
    "version": "20.0.1.0.0",
    "author": "ProcessControl",
    "website": "https://www.processcontrol.es",
    "category": "Hidden",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.access.csv",
        "views/res_bank_views.xml",
    ],
    "installable": True,
}
