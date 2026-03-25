root_id = 5758
root_category = env['product.public.category'].browse(root_id)

if not root_category.exists():
    log("KLAIDA: Kategorija nerasta!", level='error')
else:
    # 1. Rūšiuojame iš viršaus į apačią (nuo šaknies)
    all_categories = env['product.public.category'].search([('id', 'child_of', root_id)])
    sorted_categories = all_categories.sorted(key=lambda c: c.display_name)

    used_attributes = set()
    report_lines = []
    report_lines.append("=== TOP-DOWN (NEUTRAL SMALL CATEGORIES LOGIC) ===")

    for category in sorted_categories:
        # 2. Surandame visas sub-kategorijas, kurios turi bent kokio turinio
        sub_tree_cats = env['product.public.category'].search([('id', 'child_of', category.id)])
        
        active_sub_cats = []
        for sc in sub_tree_cats:
            # Kiek produktų šioje kategorijoje apskritai turi bent vieną atributą?
            prods_with_any_attrs = env['product.template'].search_count([
                ('public_categ_ids', 'in', sc.id),
                ('attribute_line_ids', '!=', False),
                ('sale_ok', '=', True),
                ('active', '=', True),
                ('is_published', '=', True)
            ])
            if prods_with_any_attrs > 0:
                # Saugome kategoriją ir jos "svorį" (produktų kiekį)
                active_sub_cats.append({'cat': sc, 'weight': prods_with_any_attrs})

        if not active_sub_cats:
            continue

        # 3. Potencialūs atributai (dar nepanaudoti aukščiau esančių tėvų)
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

        # 4. UNIVERSALUMO TIKRINIMAS
        universal_attrs = []
        for attr_name in potential_attrs:
            is_universal = True
            
            for item in active_sub_cats:
                vsc = item['cat']
                weight = item['weight']
                
                # Tikriname, ar šis konkretus atributas egzistuoja šioje kategorijoje
                exists_in_cat = env['product.template'].search_count([
                    ('public_categ_ids', 'in', vsc.id),
                    ('attribute_line_ids.attribute_id.name', '=', attr_name),
                    ('sale_ok', '=', True),
                    ('active', '=', True),
                    ('is_published', '=', True)
                ])
                
                # Taisyklė: Veto teisę turi tik tos, kurios turi >= 3 produktus su atributais.
                # Jei atributo nėra IR kategorija yra reikšminga (weight >= 3) -> blokuojame.
                # Jei weight < 3, exists_in_cat == 0 ignoruojamas (neutralumas).
                if exists_in_cat == 0 and weight >= 3:
                    is_universal = False
                    break
            
            if is_universal:
                universal_attrs.append((attr_name, potential_attrs[attr_name]))

        # 5. Atrinkimas (TOP 5)
        universal_attrs.sort(key=lambda x: x[1], reverse=True)
        top_5 = universal_attrs[:5]

        if top_5:
            formatted_path = category.display_name.replace(' / ', ' > ')
            report_lines.append("\nKATEGORIJA: %s" % formatted_path)
            
            for attr_name, count in top_5:
                report_lines.append("  + [UNIVERSALUS] %s (%s prod.)" % (attr_name, count))
                used_attributes.add(attr_name)
            
            report_lines.append("-" * 30)

    log("\n".join(report_lines), level='info')