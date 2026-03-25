# 1. Randame visas šaknines e-komercijos kategorijas
root_categories = env['product.public.category'].search([('parent_id', '=', False)])

report_lines = []
report_lines.append("=== ŠAKNINIŲ KATEGORIJŲ PRODUKTŲ APŽVALGA (Odoo 18) ===")
report_lines.append("{:<40} | {:<15} | {:<15}".format("Kategorija", "Visi prod.", "Paskelbti (Online)"))
report_lines.append("-" * 75)

total_published = 0

for root in root_categories:
    # Bendrai visi aktyvūs produktai šakoje
    all_count = env['product.template'].search_count([
        ('public_categ_ids', 'child_of', root.id),
        ('sale_ok', '=', True),
        ('active', '=', True)
    ])
    
    # Tik tie, kurie pažymėti "Is Published"
    published_count = env['product.template'].search_count([
        ('public_categ_ids', 'child_of', root.id),
        ('sale_ok', '=', True),
        ('active', '=', True),
        ('is_published', '=', True)  # Tavo pastebėtas filtras
    ])
    
    report_lines.append("{:<40} | {:<15} | {:<15}".format(root.name, all_count, published_count))
    total_published += published_count

report_lines.append("-" * 75)
report_lines.append("Iš viso paskelbtų produktų per visas šaknis: %s" % total_published)

# Išvedame į Technical > Logging
log("\n".join(report_lines), level='info')