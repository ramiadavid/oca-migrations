from openupgradelib import openupgrade


@openupgrade.logging()
def compute_purchase_discount(env):
    purchase_lines_to_compute = env["purchase.order.line"].search(
        [
            "|",
            "|",
            ("discount1", "!=", 0),
            ("discount2", "!=", 0),
            ("discount3", "!=", 0),
        ]
    )
    for line in purchase_lines_to_compute:
        discount = line._get_aggregated_multiple_discounts(
            [line[x] for x in ["discount1", "discount2", "discount3"]]
        )
        rounded_discount = line._fields["discount"].convert_to_column(discount, line)
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE purchase_order_line
            SET discount = %s
            WHERE id = %s;
        """,
            tuple(
                [
                    rounded_discount,
                    line.id,
                ]
            ),
        )


@openupgrade.logging()
def compute_supplierinfo_discount(env):
    purchase_lines_to_compute = env["product.supplierinfo"].search(
        [
            "|",
            "|",
            ("discount1", "!=", 0),
            ("discount2", "!=", 0),
            ("discount3", "!=", 0),
        ]
    )
    for line in purchase_lines_to_compute:
        discount = line._get_aggregated_multiple_discounts(
            [line[x] for x in ["discount1", "discount2", "discount3"]]
        )
        rounded_discount = line._fields["discount"].convert_to_column(discount, line)
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE product_supplierinfo
            SET discount = %s
            WHERE id = %s;
        """,
            tuple(
                [
                    rounded_discount,
                    line.id,
                ]
            ),
        )


@openupgrade.migrate()
def migrate(env, version):
    compute_purchase_discount(env)
    compute_supplierinfo_discount(env)
