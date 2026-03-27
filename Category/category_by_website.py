# 1. Surandame rmtools.eu svetainės įrašą
# Naudojame .search(), kad gautume ID pagal pavadinimą
target_website = env['website'].search([('name', '=', 'rmtools.eu')], limit=1)

# 2. Apibrėžiame domeną (filtrą):
# Mes norime kategorijų, kurių website_id NĖRA lygus rmtools.eu ID
# Taip pat įtraukiame tas, kurios neturi priskirtos svetainės (website_id = False)
category_domain = [('website_id', '=', target_website.id)]
# category_domain = [('website_id', '=', False)]

# 3. Ieškome kategorijų
other_categories = env['product.public.category'].search(category_domain)
count_category = 0
# 4. Paruošiame sąrašą išvedimui į Log'ą
if other_categories:
    log_entries = []
    for cat in other_categories:
        count_category += 1
        # Pasiimame kategorijos pilną pavadinimą (su tėvinėmis kategorijomis, jei yra)
        cat_name = cat.display_name
        # Patikriname, kokia svetainė priskirta (jei yra)
        web_name = cat.website_id.name if cat.website_id else "Visos svetainės"
        log_entries.append(f"Kategorija: {cat_name} | Svetainė: {web_name}")
    
    output = "\n".join(log_entries)
    log(f"RASTOS KATEGORIJOS (rmtools.eu svetaines {count_category}):\n{output}", level='info')
else:
    log("Kategorijų, nepriklausančių rmtools.eu, nerasta.", level='warn')