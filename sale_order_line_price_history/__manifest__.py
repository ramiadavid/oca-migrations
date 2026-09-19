# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale order line price history",
    "version": "20.0.1.0.0",
    "category": "Sales Management",
    "author": "Tecnativa,Odoo Community Association (OCA)",
    "website": "https://www.processcontrol.es",
    "license": "AGPL-3",
    "depends": ["sale"],
    "development_status": "Production/Stable",
    "data": [
        "wizards/sale_order_line_price_history.xml",
        "views/sale_views.xml",
        "security/ir.access.csv",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_order_line_price_history/static/src/js/*.js",
            "sale_order_line_price_history/static/src/xml/*.xml",
        ],
    },
    "maintainers": ["CarlosRoca13", "Shide"],
    "installable": True,
}
