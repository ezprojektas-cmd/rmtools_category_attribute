# === BATCH KONFIGŪRACIJA ===
batch_offset = 20  # Pakeisk į 5, 10 ir t.t., kad imtum kitas grupes
batch_limit = 10

# 1. Surandame svetainę
target_website = env['website'].search([('name', '=', 'rmtools.eu')], limit=1)

if not target_website:
    log("KLAIDA: Svetainė 'rmtools.eu' nerasta!", level='error')
else:
    # 2. Surandame šaknines kategorijas (tik tas, kurios neturi tėvų)
    root_categories_to_process = env['product.public.category'].search([
        ('parent_id', '=', False),
        # ('website_id', '=', target_website.id) nereikia nes nera skirtumo, jos vistiek eina atskirai
    ], order='id asc', offset=batch_offset, limit=batch_limit)

    report_lines = [f"=== APDOROJAMI ŠAKNINIAI RĖŽIAI: {batch_offset} iki {batch_offset + batch_limit} ==="]

    # 3. Ciklas per kiekvieną šakninę kategoriją atskirai
    for root_node in root_categories_to_process:
        root_id = root_node.id
        
        # --- TAVO ORIGINALUS KODAS (IZOLIUOTAS ŠAKOJE) ---
        all_categories = env['product.public.category'].search([('id', 'child_of', root_id)])

        # IŠVALOME SENUS DUOMENIS (SVARBU!)
        # (5, 0, 0) - Odoo komanda, kuri pašalina visus sąryšius M2M lauke
        all_categories.write({'x_studio_mandatory_attributes': [(5, 0, 0)]})

        sorted_categories = all_categories.sorted(key=lambda c: c.display_name)

        # Žodynas pavadinimų sekimui (išvalomas kiekvienai naujai šakniai!)
        category_assigned_names = {} 
        report_lines.append(f"\n>>> APDOROJAMA ŠAKA: {root_node.display_name} (ID: {root_id})")

        for category in sorted_categories:
            # Nustatome protėvius, kad išvengtume dubliavimo
            ancestor_ids = []
            curr = category.parent_id
            while curr and curr.id >= root_id:
                ancestor_ids.append(curr.id)
                curr = curr.parent_id
            
            already_used_above = set()
            for a_id in ancestor_ids:
                already_used_above.update(category_assigned_names.get(a_id, []))

            # Surandame aktyvias sub-kategorijas svorio skaičiavimui
            sub_tree_cats = env['product.public.category'].search([('id', 'child_of', category.id)])
            active_sub_cats = []
            
            for sc in sub_tree_cats:
                prods_count = env['product.template'].search_count([
                    ('public_categ_ids', 'in', sc.id),
                    ('attribute_line_ids', '!=', False),
                    ('sale_ok', '=', True),
                    ('active', '=', True),
                    ('is_published', '=', True)
                ])
                if prods_count > 0:
                    active_sub_cats.append({'cat': sc, 'weight': prods_count})

            if not active_sub_cats:
                continue

            # Surandame visus galimus atributus šioje šakoje
            all_prods_in_branch = env['product.template'].search([
                ('public_categ_ids', 'child_of', category.id),
                ('sale_ok', '=', True),
                ('active', '=', True),
                ('is_published', '=', True)
            ])
            
            potential_attrs = {} 
            attr_obj_map = {}

            for p in all_prods_in_branch:
                for line in p.attribute_line_ids:
                    attr = line.attribute_id
                    if attr.name not in already_used_above:
                        potential_attrs[attr.id] = potential_attrs.get(attr.id, 0) + 1
                        attr_obj_map[attr.id] = attr.name # Naudojam ID kaip raktą, kad išvengtume Index klaidos

            universal_attr_ids = []

            # Tikriname universalumą (Veto principas)
            for attr_id, count in potential_attrs.items():
                attr_name = attr_obj_map[attr_id]
                is_universal = True
                
                for item in active_sub_cats:
                    if item['weight'] >= 3:
                        exists = env['product.template'].search_count([
                            ('public_categ_ids', 'in', item['cat'].id),
                            ('attribute_line_ids.attribute_id', '=', attr_id),
                            ('sale_ok', '=', True),
                            ('active', '=', True),
                            ('is_published', '=', True)
                        ])
                        if exists == 0:
                            is_universal = False
                            break
                
                if is_universal:
                    universal_attr_ids.append((attr_id, attr_name, count))

            universal_attr_ids.sort(key=lambda x: x[2], reverse=True)
            top_5_data = universal_attr_ids[:5]

            if top_5_data:
                attr_to_write = [data[0] for data in top_5_data]
                category.write({
                    'x_studio_mandatory_attributes': [(6, 0, attr_to_write)]
                })
                
                category_assigned_names[category.id] = [data[1] for data in top_5_data]
                report_lines.append(f"  [+] {category.display_name}: {', '.join([d[1] for d in top_5_data])}")

    log("\n".join(report_lines), level='info')