# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Agreements Legal",
    "summary": "Manage Agreements, LOI and Contracts",
    "author": "Pavlov Media, "
    "Open Source Integrators, "
    "Yves Goldberg (Ygol Internetwork), "
    "Odoo Community Association (OCA)",
    "website": "https://www.processcontrol.es",
    "category": "Partner",
    "license": "AGPL-3",
    "version": "20.0.1.0.1",
    "depends": ["contacts", "agreement", "product", "web"],
    "data": [
        "data/cron.xml",
        "data/ir_sequence.xml",
        "data/agreement_stage.xml",
        "data/agreement_type.xml",
        "security/res_groups.xml",
        "report/agreement.xml",
        "views/res_config_settings.xml",
        "views/agreement_appendix.xml",
        "views/agreement_clause.xml",
        "views/agreement_recital.xml",
        "views/agreement_section.xml",
        "views/agreement_stages.xml",
        "views/agreement_type.xml",
        "views/agreement_subtype.xml",
        "views/agreement.xml",
        "views/menu.xml",
        "wizards/create_agreement_wizard.xml",
        "security/ir.access.csv",
    ],
    "demo": ["demo/demo.xml"],
    "assets": {
        "web.assets_backend": [
            "agreement_legal/static/src/js/**/*",
            "agreement_legal/static/src/xml/**/*",
        ],
    },
    "application": True,
    "development_status": "Beta",
    "maintainers": ["max3903", "ygol"],
}
