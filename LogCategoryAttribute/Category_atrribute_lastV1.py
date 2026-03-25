root_id = 5758
root_category = env['product.public.category'].browse(root_id)

if not root_category.exists():
    log("KLAIDA: Kategorija nerasta!", level='error')
else:
    # 1. Surandame visas kategorijas medyje
    all_categories = env['product.public.category'].search([('id', 'child_of', root_id)])
    # Rūšiuojame nuo giliausių (ilgiausias display_name arba reverse), kad vaikinės būtų pirmos
    sorted_categories = all_categories.sorted(key=lambda c: c.display_name, reverse=True)

    used_attributes = set()
    report_lines = []
    report_lines.append("=== UNIVERSALIŲ ATRIBUTŲ PASKIRSTYMAS (NON-BLOCKING EMPTY CATS) ===")

    for category in sorted_categories:
        # 2. Identifikuojame kategorijas, kurios TURI produktų su atributais (tik jos gali blokuoti universalumą)
        sub_tree_cats = env['product.public.category'].search([('id', 'child_of', category.id)])
        
        # Filtruojame tik tas, kurios turi bent vieną "gyvą" produktą su atributais
        active_sub_cats = []
        for sc in sub_tree_cats:
            has_content = env['product.template'].search_count([
                ('public_categ_ids', 'in', sc.id),
                ('attribute_line_ids', '!=', False),
                ('sale_ok', '=', True),
                ('active', '=', True),
                ('is_published', '=', True)
            ])
            if has_content > 0:
                active_sub_cats.append(sc)

        # Jei visoje šakoje nėra nei vieno produkto su atributais - šaką praleidžiame
        if not active_sub_cats:
            continue

        # 3. Surandame visus potencialius atributus šioje šakoje (kurie dar nebuvo panaudoti žemiau)
        all_prods_in_branch = env['product.template'].search([
            ('public_categ_ids', 'child_of', category.id),
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

        # 4. TIKRINAME UNIVERSALUMĄ:
        # Atributas yra universalus, jei jis egzistuoja VISOSE 'active_sub_cats'
        universal_attrs = []
        for attr_name in potential_attrs:
            is_universal = True
            for vsc in active_sub_cats:
                exists_in_cat = env['product.template'].search_count([
                    ('public_categ_ids', 'in', vsc.id),
                    ('attribute_line_ids.attribute_id.name', '=', attr_name),
                    ('sale_ok', '=', True),
                    ('active', '=', True),
                    ('is_published', '=', True)
                ])
                # Jei nors vienoje kategorijoje, kurioje YRA produktų, šio atributo trūksta -> neuniversalus
                if exists_in_cat == 0:
                    is_universal = False
                    break
            
            if is_universal:
                universal_attrs.append((attr_name, potential_attrs[attr_name]))

        # 5. Rezultatų fiksavimas (TOP 5)
        universal_attrs.sort(key=lambda x: x[1], reverse=True)
        top_5 = universal_attrs[:5]

        if top_5:
            formatted_path = category.display_name.replace(' / ', ' > ')
            report_lines.append("\nKATEGORIJA: %s" % formatted_path)
            report_lines.append("Aktyvių (turinio turinčių) sub-kategorijų kiekis: %s" % len(active_sub_cats))
            
            for attr_name, count in top_5:
                report_lines.append("  + [UNIVERSALUS] %s (%s prod.)" % (attr_name, count))
                used_attributes.add(attr_name)
            
            report_lines.append("-" * 30)

    log("\n".join(report_lines), level='info')