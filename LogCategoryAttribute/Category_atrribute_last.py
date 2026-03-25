root_id = 5758
root_category = env['product.public.category'].browse(root_id)

if not root_category.exists():
    log("KLAIDA: Kategorija nerasta!", level='error')
else:
    # 1. Surandame visas kategorijas medyje
    all_categories = env['product.public.category'].search([('id', 'child_of', root_id)])
    sorted_categories = all_categories.sorted(key=lambda c: c.display_name)

    used_attributes = set()
    report_lines = []
    report_lines.append("=== UNIVERSALIŲ ATRIBUTŲ PASKIRSTYMAS (STRICT MODE) ===")

    for category in sorted_categories:
        # 2. Surandame visas "gyvas" sub-kategorijas po šia kategorija (įskaitant ją pačią)
        # Jos turi turėti bent 1 produktą su >1 atributu
        sub_tree_cats = env['product.public.category'].search([('id', 'child_of', category.id)])
        
        valid_sub_cats = []
        for sc in sub_tree_cats:
            prods = env['product.template'].search_count([
                ('public_categ_ids', 'in', sc.id),
                ('attribute_line_ids', '!=', False),
                #####
                ('sale_ok', '=', True),
                ('active', '=', True),
                ('is_published', '=', True)
            ])
            # Tikriname tik tas kategorijas, kurios turi realų turinį
            if prods > 0:
                valid_sub_cats.append(sc)

        if not valid_sub_cats:
            continue

        # 3. Surandame visus galimus naujus atributus šioje šakoje
        all_prods_in_branch = env['product.template'].search([
            ('public_categ_ids', 'child_of', category.id),
            ####
            ('sale_ok', '=', True),
            ('active', '=', True),
            ('is_published', '=', True)
        ])
        
        potential_attrs = {}
        for p in all_prods_in_branch:
            for line in p.attribute_line_ids:
                attr_name = line.attribute_id.name
                if attr_name not in used_attributes:
                    potential_attrs[attr_name] = potential_attrs.get(attr_name, 0) + 1

        # 4. TIKRINAME UNIVERSALUMĄ: Atributas turi egzistuoti KIEKVIENOJE valid_sub_cats
        universal_attrs = []
        for attr_name in potential_attrs:
            is_universal = True
            for vsc in valid_sub_cats:
                # Ar bent vienas produktas šioje konkrečioje kategorijoje turi šį atributą?
                exists_in_cat = env['product.template'].search_count([
                    ('public_categ_ids', 'in', vsc.id),
                    ('attribute_line_ids.attribute_id.name', '=', attr_name),
                    ####
                    ('sale_ok', '=', True),
                    ('active', '=', True),
                    ('is_published', '=', True)
                ])
                if exists_in_cat == 0:
                    is_universal = False
                    break
            
            if is_universal:
                universal_attrs.append((attr_name, potential_attrs[attr_name]))

        # 5. Rūšiuojame universalius pagal populiarumą ir paimame TOP 5
        universal_attrs.sort(key=lambda x: x[1], reverse=True)
        top_5 = universal_attrs[:5]

        if top_5:
            formatted_path = category.display_name.replace(' / ', ' > ')
            report_lines.append("\nKATEGORIJA: %s" % formatted_path)
            report_lines.append("Šios šakos 'gyvų' sub-kategorijų kiekis: %s" % len(valid_sub_cats))
            
            for attr_name, count in top_5:
                report_lines.append("  + [UNIVERSALUS] %s (%s prod.)" % (attr_name, count))
                used_attributes.add(attr_name)
            
            report_lines.append("-" * 30)

    log("\n".join(report_lines), level='info')