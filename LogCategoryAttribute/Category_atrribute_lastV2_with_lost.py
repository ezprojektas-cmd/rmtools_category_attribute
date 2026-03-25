# root_id = 5758 #Drilling, screwing tools
# root_id = 5770 #Fasteners 
root_id = 5766 #Gas, torches, heaters, soldering irons

root_category = env['product.public.category'].browse(root_id)

if not root_category.exists():
    log("KLAIDA: Kategorija nerasta!", level='error')
else:
    all_categories = env['product.public.category'].search([('id', 'child_of', root_id)])
    sorted_categories = all_categories.sorted(key=lambda c: c.display_name)

    used_attributes = set()
    report_lines = []
    report_lines.append("=== TOP-DOWN LOGIKA (Odoo 18) ===")

    for category in sorted_categories:
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
                if attr_name not in used_attributes:
                    potential_attrs[attr_name] = potential_attrs.get(attr_name, 0) + 1

        universal_attrs = []
        rejected_attrs = [] # Naujas sąrašas „atmestiems“ atributams

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
                
                # VETO taisyklė
                if exists_in_cat == 0 and weight >= 3:
                    is_universal = False
                    rejection_reason = "Trūksta kategorijoje: %s (svoris: %s)" % (vsc.name, weight)
                    break
            
            if is_universal:
                universal_attrs.append((attr_name, count))
            else:
                rejected_attrs.append((attr_name, rejection_reason))

        # Rūšiuojame ir atrenkame TOP 5
        universal_attrs.sort(key=lambda x: x[1], reverse=True)
        top_5 = universal_attrs[:5]
        # Atributai, kurie buvo universalūs, bet netilpo į TOP 5
        others_universal = universal_attrs[5:] 

        if top_5 or rejected_attrs:
            formatted_path = category.display_name.replace(' / ', ' > ')
            report_lines.append("\nKATEGORIJA: %s" % formatted_path)
            
            # Išvedame sėkmingus
            for attr_name, count in top_5:
                report_lines.append("  [+] UNIVERSALUS: %s (%s prod.)" % (attr_name, count))
                used_attributes.add(attr_name)
            
            # Išvedame atmestus dėl VETO taisyklės
            for attr_name, reason in rejected_attrs:
                report_lines.append("  [-] ATMESTAS (Veto): %s -> %s" % (attr_name, reason))
            
            # Išvedame tuos, kurie buvo universalūs, bet netilpo į limitą
            for attr_name, count in others_universal:
                report_lines.append("  [!] NETILPO Į TOP 5: %s (%s prod.)" % (attr_name, count))
            
            report_lines.append("-" * 40)

    log("\n".join(report_lines), level='info')