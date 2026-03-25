# prideta kad vaikinė tikrintų tik tevus ir senelius ir tik jei juose yra panaidota atributas tampa used, t.y. tikrinam kinkrečiai toje šakoje
# root_id = 5758 #Drilling, screwing tools
# root_id = 5770 #Fasteners 
root_id = 5766 #Gas, torches, heaters, soldering irons
root_category = env['product.public.category'].browse(root_id)

if not root_category.exists():
    log("KLAIDA: Kategorija nerasta!", level='error')
else:
    # 1. Pasiimame visas kategorijas, surūšiuotas pagal pavadinimą (Top-Down)
    all_categories = env['product.public.category'].search([('id', 'child_of', root_id)])
    sorted_categories = all_categories.sorted(key=lambda c: c.display_name)

    # 2. Vietoj set(), naudosime žodyną, kur saugosime, kokie atributai priskirti konkrečiai kategorijai
    # Tai padės mums patikrinti tik protėvius (ancestors)
    category_assigned_attrs = {} 
    report_lines = ["=== TOP-DOWN LOGIKA (Patobulinta šakų izoliacija) ==="]

    for category in sorted_categories:
        # Nustatome visus protėvius (tėvus, senelius) iki pat root_idgit 
        # Tai svarbu, kad nesidubliuotų filtrai el. parduotuvės navigacijoje
        ancestor_ids = []
        curr = category.parent_id
        while curr and curr.id >= root_id:
            ancestor_ids.append(curr.id)
            curr = curr.parent_id
        
        # Sukuriame rinkinį atributų, kurie JAU panaudoti aukštesniuose lygmenyse
        already_used_above = set()
        for a_id in ancestor_ids:
            already_used_above.update(category_assigned_attrs.get(a_id, []))

        # --- Toliau jūsų logika dėl sub_tree_cats ir active_sub_cats ---
        sub_tree_cats = env['product.public.category'].search([('id', 'child_of', category.id)])
        active_sub_cats = []
        for sc in sub_tree_cats:
            prods_with_any_attrs = env['product.template'].search_count([
                ('public_categ_ids', 'in', sc.id),
                ('attribute_line_ids', '!=', False),
                ('sale_ok', '=', True),
                ('active', '=', True),
                ('is_published', '=', True)
            ])
            if prods_with_any_attrs > 0:
                active_sub_cats.append({'cat': sc, 'weight': prods_with_any_attrs})

        if not active_sub_cats:
            continue

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
                # SVARBU: Tikriname tik ar nebuvo panaudota AUKŠČIAU šioje šakoje
                if attr_name not in already_used_above:
                    potential_attrs[attr_name] = potential_attrs.get(attr_name, 0) + 1

        universal_attrs = []
        rejected_attrs = []

        for attr_name, count in potential_attrs.items():
            is_universal = True
            rejection_reason = ""
            
            for item in active_sub_cats:
                vsc = item['cat']
                weight = item['weight']
                
                exists_in_cat = env['product.template'].search_count([
                    ('public_categ_ids', 'in', vsc.id),
                    ('attribute_line_ids.attribute_id.name', '=', attr_name),
                    ('sale_ok', '=', True),
                    ('active', '=', True),
                    ('is_published', '=', True)
                ])
                
                if exists_in_cat == 0 and weight >= 3:
                    is_universal = False
                    rejection_reason = "Veto: %s (w:%s)" % (vsc.name, weight)
                    break
            
            if is_universal:
                universal_attrs.append((attr_name, count))
            else:
                rejected_attrs.append((attr_name, rejection_reason))

        universal_attrs.sort(key=lambda x: x[1], reverse=True)
        top_5 = universal_attrs[:5]

        if top_5:
            # Įrašome šiai kategorijai priskirtus atributus į atmintį (vaikams)
            category_assigned_attrs[category.id] = [a[0] for a in top_5]
            
            formatted_path = category.display_name.replace(' / ', ' > ')
            report_lines.append("\nKATEGORIJA: %s" % formatted_path)
            
            for attr_name, count in top_5:
                report_lines.append("  [+] UNIVERSALUS: %s (%s prod.)" % (attr_name, count))
            
            for attr_name, reason in rejected_attrs:
                report_lines.append("  [-] ATMESTAS: %s -> %s" % (attr_name, reason))
            
            report_lines.append("-" * 40)

    log("\n".join(report_lines), level='info')