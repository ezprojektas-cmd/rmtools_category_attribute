# Kaip veikia ši logika (pavyzdys):
# Top lygis ("Drilling, screwing tools"): Skriptas randa visus produktus. Pamato, kad populiariausi yra "Manufacturer1", "Diameter", "Stem type", "Overall length", "Stone". Jis juos "pasisavina" ir įdeda į used_attributes.

# Vidinis lygis ("SDS plus Premium"): Jis vėl žiūri savo produktus. Jis mato "Manufacturer1", bet kadangi jis jau used_attributes sąraše, jį ignoruoja. Jis randa kitus, pvz., "Concrete", "Marble", "Brick" ir t.t. Jei jie nebuvo panaudoti viršuje, jis paima savo 5.

# Žemiausias lygis ("SDS plus IRWIN Speedhammer"): Jis matys tik tuos atributus, kurie liko "laisvi" po to, kai tėvai ir seneliai išsirinko savo populiariausius.

# 1. Pradiniai nustatymai
root_id = 5758
root_category = env['product.public.category'].browse(root_id)

if not root_category.exists():
    log("KLAIDA: Kategorija %s nerasta!" % root_id, level='error')
else:
    # Surandame visas kategorijas ir jas surūšiuojame pagal gylį (hierarchiją)
    # Svarbu: Einame nuo tėvų link vaikų
    all_categories = env['product.public.category'].search([('id', 'child_of', root_id)])
    sorted_categories = all_categories.sorted(key=lambda c: c.display_name)

    # Čia saugosime atributų pavadinimus, kurie jau buvo priskirti aukščiau
    used_attributes = set()
    
    report_lines = []
    report_lines.append("=== UNIKALIŲ ATRIBUTŲ PASKIRSTYMAS PER HIERARCHIJĄ ===")

    for category in sorted_categories:
        # 2. Randame visus produktus šioje kategorijoje IR visose jos vaikėse kategorijose
        # Tai svarbu, nes tėvinė kategorija turi matyti visą savo "turinį"
        sub_tree_products = env['product.template'].search([('public_categ_ids', 'child_of', category.id)])
        
        attr_counts = {}
        for product in sub_tree_products:
            for line in product.attribute_line_ids:
                name = line.attribute_id.name
                # SKAIČIUOJAME TIK JEI DAR NEBUVO PANAUDOTA AUKŠČIAU
                if name not in used_attributes:
                    attr_counts[name] = attr_counts.get(name, 0) + 1
        
        # Rūšiuojame pagal populiarumą
        sorted_available = sorted(attr_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Paimame iki 5 populiariausių
        top_5_for_this_cat = sorted_available[:5]
        
        # Suformuojame ataskaitos eilutę
        formatted_path = category.display_name.replace(' / ', ' > ')
        report_lines.append("\nKATEGORIJA: %s" % formatted_path)
        
        if not top_5_for_this_cat:
            report_lines.append("  [!] Naujų unikalių atributų nepriklausė.")
        else:
            report_lines.append("  Priskirti TOP atributai:")
            for attr_name, count in top_5_for_this_cat:
                report_lines.append("  + %s (%s prod.)" % (attr_name, count))
                # Įtraukiame į panaudotų sąrašą, kad vaikinės kategorijos nebegautų
                used_attributes.add(attr_name)
        
        report_lines.append("-" * 30)

    # 3. Išvedame viską į logą
    log("\n".join(report_lines), level='info')