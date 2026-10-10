# Copyright 2019 Tecnativa - David Vidal
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductSupplierInfo(models.Model):
    _name = "product.supplierinfo"
    _inherit = ["purchase.triple.discount.mixin", "product.supplierinfo"]

    def _get_seller_info(self):
        """20.0: `_select_seller` ya no devuelve la tarifa del proveedor sino el
        diccionario que arma este metodo, asi que los descuentos multiples tienen
        que viajar dentro. Quien lo lea debe usar `.get()`: el respaldo del ultimo
        pedido (`_get_last_po_seller_info`) arma el diccionario sin pasar por aqui."""
        res = super()._get_seller_info()
        if res:
            res.update({fname: self[fname] for fname in self._get_multiple_discount_field_names()})
        return res
