# RMtoos category and atribute: search category tree 1-2(regular)
# tik reguliarus

# Puiku, dabar apjungsime kategorijų hierarchiją su atributų analitika. Kadangi viena kategorija gali turėti daug produktų, o tie produktai – skirtingus atributus, mes turime kiekvienai kategorijai „pereiti“ per jos produktus ir susumuoti, kiek kartų kiekvienas atributas pasirodo.

# Štai atnaujintas skriptas jūsų Scheduled Action (Python Code) sekcijai:

# 1. Surandame pagrindinę Web kategoriją pagal ID (5758)
root_category = env['product.public.category'].browse(5758)

if not root_category.exists():
    log("KLAIDA: Kategorija su ID 5758 nerasta!", level='error')
else:
    # Surandame visas vaikines kategorijas
    all_categories = env['product.public.category'].search([
        ('id', 'child_of', root_category.id)
    ])
    
    # Rūšiuojame Python lygmenyje (išvengiame SQL klaidos)
    sorted_categories = all_categories.sorted(key=lambda c: c.display_name)
    
    report_lines = []
    report_lines.append("=== ATRIBUTŲ POPULIARUMO ATASKAITA PAGAL KATEGORIJAS ===")
    report_lines.append("Sugeneruota: %s" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    report_lines.append("-" * 50)

    for category in sorted_categories:
        # 2. Surandame visus produktus (product.template), priskirtus šiai Web kategorijai
        products = env['product.template'].search([
            ('public_categ_ids', 'in', category.id),
            ('sale_ok', '=', True),
            ('active', '=', True),
            ('is_published', '=', True)
        ])
        
        # Žodynas atributams skaičiuoti: { 'Atributo Pavadinimas': kiekis }
        attr_stats = {}
        
        for product in products:
            # Pasiimame unikalius atributus iš produkto eilučių (attribute_line_ids)
            for line in product.attribute_line_ids:
                attr_name = line.attribute_id.name
                # Skaičiuojame, kiek produktų turi šį atributą
                attr_stats[attr_name] = attr_stats.get(attr_name, 0) + 1
        
        # Rūšiuojame atributus pagal populiarumą (mažėjimo tvarka)
        # sorted_items bus sąrašas tūpų: [('Spalva', 10), ('Dydis', 5)...]
        sorted_attrs = sorted(attr_stats.items(), key=lambda item: item[1], reverse=True)
        
        # Formuojame kategorijos antraštę
        formatted_path = category.display_name.replace(' / ', ' > ')
        report_lines.append("\nKATEGORIJA: %s" % formatted_path)
        report_lines.append("Iš viso produktų kategorijoje: %s" % len(products))
        
        # 3. Išvedame atributus
        if not sorted_attrs:
            report_lines.append("  [!] Šioje kategorijoje produktai atributų neturi.")
        else:
            for attr_name, count in sorted_attrs:
                report_lines.append("  - %s: %s prod." % (attr_name, count))
        
        report_lines.append("-" * 30)

    # 4. Visą sukauptą tekstą išvedame į vieną log įrašą
    log("\n".join(report_lines), level='info')