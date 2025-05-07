from odoo import http
from odoo.addons.base_user_role_company.controllers.main import HomeExtended
from odoo.addons.base_user_role_company.controllers.main import Home


@http.route()
def web_load_menus(self, *args, **kwargs):
    response = Home.web_load_menus(self, *args, **kwargs)
    response.headers.remove("Cache-Control")
    return response


HomeExtended.web_load_menus = web_load_menus
