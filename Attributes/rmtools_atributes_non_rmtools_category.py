# 1. Gauname svetainės ID, kurios kategorijų norime VENGTI
# Pakeiskite 'rmtools.eu' į tikslų pavadinimą, jei jis skiriasi sistemoje
excluded_website = env['website'].search([('name', '=', 'rmtools.eu')], limit=1)

# 2. Filtruojame kategorijas, kurios NĖRA priskirtos šiai svetainei
# Jei website_id yra False, tai kategorija yra bendra visoms svetainėms
category_domain = [('website_id', '!=', excluded_website.id)]
valid_categories = env['product.public.category'].search(category_domain)

# 3. Ieškome produktų pagal tavo kriterijus
product_domain = [
    ('active', '=', True),
    ('sale_ok', '=', True),
    ('is_published', '=', True),
    ('public_categ_ids', 'in', valid_categories.ids)
]
active_products = env['product.template'].search(product_domain)

# 4. Kaupiame unikalius atributus ir skaičiuojame jų panaudojimą
# Naudosime žodyną (dictionary): { 'Atributo Pavadinimas': produktų_kiekis }
attr_summary = {}

for product in active_products:
    # Odoo 18 produkto atributai pasiekiami per attribute_line_ids
    for line in product.attribute_line_ids:
        attr_name = line.attribute_id.name
        if attr_name in attr_summary:
            attr_summary[attr_name] += 1
        else:
            attr_summary[attr_name] = 1

# 5. Išvedame rezultatą į Odoo Log (Technical > Logging > Messages)
log_header = "--- UNIKALIŲ ATRIBUTŲ ATASKAITA ---"
log_body = "\n".join([f"Atributas: {k} | Kiekis: {v}" for k, v in attr_summary.items()])

log(f"{log_header}\n{log_body}", level='info')