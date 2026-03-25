# Tai yra esminis logikos klausimas kuriant filtrų sistemą. Jūsų pastebėjimas labai teisingas: jei tėvinė kategorija „pasisavina“ atributą, jis tampa bendru vardikliu visoms žemiau esančioms vaikėms kategorijoms.

# Štai kaip veikia ši logika Odoo 18 „Web“ kategorijų kontekste ir atsakymai į jūsų klausimus:

# 1. Ar tai reiškia, kad jie tinka visoms vaikinėms kategorijoms?
# Taip, statistiškai. Kadangi tėvinė kategorija skaičiuoja visus savo vaikus (child_of), jei „Diameter, mm“ surinko 2088 produktus, tai reiškia, kad didžioji dauguma tų produktų (išbarstytų po sub-kategorijas) turi šį atributą.

# Privalumas: Vartotojas, būdamas pagrindiniame „Drilling, screwing tools“ puslapyje, iškart matys svarbiausią filtrą (Skersmenį), kuris veiks visame prekių medyje.

# Rizika: Jei turite kokią nors specifinę sub-kategoriją (pvz., „Cleaning sprays“ po įrankiais), kuriai skersmuo neaktualus, tas filtras ten tiesiog nerodys jokių reikšmių arba bus tuščias.

# 2. Produktai be atributų arba su vienu atributu
# Jūsų pageidavimas „nežiūrėti į tas kategorijas“ yra labai logiškas, kad neužterštume logų ir nepriskirtume filtrų ten, kur nėra prasmės.

# Sprendimas – į skriptą įtraukti filtrus/saugiklius:

# Skip Empty Categories: Praleidžiame kategorijas, kurios neturi produktų.

# Minimum Attributes: Praleidžiame produktus, kurie neturi bent 2 atributų (nes filtruoti vieną atributą nėra prasmės).

# Minimum Popularity: Galime nustatyti, kad atributas būtų laikomas „reikšmingu“, tik jei jis dengia bent tam tikrą procentą kategorijos produktų.

# Patobulinta logika (su saugikliais)
# Štai kaip atrodytų skriptas, kuris ignoruoja „tuščias“ arba „skurdžias“ kategorijas:

root_id = 5758
root_category = env['product.public.category'].browse(root_id)

if not root_category.exists():
    log("KLAIDA: Kategorija nerasta!", level='error')
else:
    all_categories = env['product.public.category'].search([('id', 'child_of', root_id)])
    sorted_categories = all_categories.sorted(key=lambda c: c.display_name)

    used_attributes = set()
    report_lines = []
    report_lines.append("=== IŠMANUS ATRIBUTŲ PASKIRSTYMAS ===")

    for category in sorted_categories:
        # 1. Randame produktus, kurie turi BENT 2 atributų eilutes
        # Taip atmetame prekes be parametrų arba su labai mažai info
        sub_tree_products = env['product.template'].search([
            ('public_categ_ids', 'child_of', category.id),
            ('attribute_line_ids', '!=', False)
        ])
        
        # Filtruojame: paliekame tik tuos, kurie turi bent 2 atributus
        qualified_products = sub_tree_products.filtered(lambda p: len(p.attribute_line_ids) >= 2)

        # Jei qualified_products tuščias - šią kategoriją praleidžiame
        if not qualified_products:
            continue

        attr_counts = {}
        for product in qualified_products:
            for line in product.attribute_line_ids:
                name = line.attribute_id.name
                if name not in used_attributes:
                    attr_counts[name] = attr_counts.get(name, 0) + 1
        
        # Rūšiuojame
        sorted_available = sorted(attr_counts.items(), key=lambda x: x[1], reverse=True)
        top_5 = sorted_available[:5]
        
        if top_5:
            formatted_path = category.display_name.replace(' / ', ' > ')
            report_lines.append("\nKATEGORIJA: %s" % formatted_path)
            report_lines.append("Kvalifikuoti produktai (su >1 atributu): %s" % len(qualified_products))
            
            for attr_name, count in top_5:
                # Saugiklis: Jei atributas dengia mažiau nei 10% produktų, gal jis nėra toks svarbus šiam lygiui?
                coverage = (count / len(qualified_products)) * 100
                report_lines.append("  + %s (%s prod. | %s%%)" % (attr_name, count, round(coverage, 1)))
                used_attributes.add(attr_name)
            
            report_lines.append("-" * 30)

    log("\n".join(report_lines), level='info')