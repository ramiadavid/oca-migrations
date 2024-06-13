import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    _logger.info("Initializing column discount1 on table purchase_order_line")
    env.cr.execute(
        """
            UPDATE purchase_order_line
            SET discount1 = discount
            WHERE discount != 0
        """
    )
    _logger.info("Initializing column discount1 on table product_supplierinfo")
    env.cr.execute(
        """
            UPDATE product_supplierinfo
            SET discount1 = discount
            WHERE discount != 0
        """
    )
