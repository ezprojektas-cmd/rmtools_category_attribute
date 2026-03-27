# 1. Surandame svetainę pagal pavadinimą
target_website = env['website'].search([('name', '=', 'rmtools.eu')], limit=1)

if not target_website:
    log("KLAIDA: Svetainė 'rmtools.eu' nerasta!", level='error')
else:
    # 2. Filtras: Šakninės kategorijos (parent_id = False) ir konkreti svetainė
    root_category_domain = [
        ('parent_id', '=', False),
        ('website_id', '=', target_website.id)
    ]

    # 3. Vykdome paiešką
    root_categories = env['product.public.category'].search(root_category_domain, order='id asc')

    # 4. Suskaičiuojame, kiek įrašų grąžino paieška
    total_count = len(root_categories)

    # 5. Rezultatų išvedimas į Log'ą
    if total_count > 0:
        log_header = f"--- SUVESTINĖ (Svetainė: {target_website.name}) ---"
        count_info = f"Iš viso rasta šakninių kategorijų: {total_count}"
        
        # Sukuriame sąrašą su pavadinimais
        cat_list = "\n".join([f"- {cat.name} (ID: {cat.id})" for cat in root_categories])
        
        # Sujungiame viską į vieną žinutę
        final_message = f"{log_header}\n{count_info}\n\nSĄRAŠAS:\n{cat_list}"
        log(final_message, level='info')
    else:
        log(f"Svetainė '{target_website.name}' neturi jokių šakninių kategorijų.", level='warn')