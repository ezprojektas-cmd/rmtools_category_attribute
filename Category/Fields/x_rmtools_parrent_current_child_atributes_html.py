# 1. PREFETCHING (Sprendžiame N+1 problemą)
# Išfiltruojame tikrus įrašus, kad išvengtume NewId klaidų masinėje užklausoje
valid_records = self.filtered(lambda r: isinstance(r.id, int))

if valid_records:
    # Vienu kartu paimame visus tėvus ir vaikus visoms matomoms eilutėms
    all_parents = valid_records.mapped('parent_id')
    all_children = valid_records.mapped('child_id')
    
    # "Paliečiame" atributus, kad Odoo juos visus užkrautų į Cache (viena SQL užklausa)
    if all_parents:
        all_parents.mapped('x_rmtools_mandatory_attributes')
    if all_children:
        all_children.mapped('x_rmtools_mandatory_attributes')
    # Taip pat užkrauname pačių įrašų atributus
    valid_records.mapped('x_rmtools_mandatory_attributes')

# 2. PAGRINDINIS CIKLAS
for record in self:
    # Laukas iš tavo paskutinės konfigūracijos (su dviem 'r' ir viena 't')
    f_name = 'x_rmtools_parrent_current_child_atributes_html'
    
    # Pradinė reikšmė (svarbu!)
    record[f_name] = ""
    
    if not isinstance(record.id, int):
        continue

    sections = []
    
    # --- A: Tėvai (Pilka) ---
    # Kadangi duomenys jau kėše (Cache), šis ciklas nevykdys SQL užklausų
    path_parents = []
    curr = record.parent_id
    while curr:
        if curr in path_parents: break
        path_parents.insert(0, curr)
        curr = curr.parent_id
    
    p_tags = []
    for p in path_parents:
        # Paimame display_name (jis taip pat bus kėše po mapped() viršuje)
        # attrs = p.x_rmtools_mandatory_attributes.mapped('display_name')
        # for a in attrs:
        #     p_tags.append(f'<span class="badge rounded-pill bg-200 text-600 border" style="margin: 2px;">{a}</span>')
        
        for attr in p.x_rmtools_mandatory_attributes:
            label = f"({attr.id}) {attr.display_name}"
            p_tags.append(f'<span class="badge rounded-pill bg-200 text-600 border" style="margin: 2px;">{label}</span>')

    if p_tags:
        sections.append("".join(p_tags))

    # --- B: Esamas (Žalia) ---
    # curr_attrs = record.x_rmtools_mandatory_attributes.mapped('display_name')
    # if curr_attrs:
    #     c_tags = "".join([f'<span class="badge rounded-pill bg-success-subtle text-success border border-success-subtle" style="margin: 2px;">{a}</span>' for a in curr_attrs])
    #     sections.append(c_tags)
    curr_tags_list = [f"({a.id}) {a.display_name}" for a in record.x_rmtools_mandatory_attributes]
    if curr_tags_list:
        c_tags = "".join([f'<span class="badge rounded-pill bg-success-subtle text-success border border-success-subtle" style="margin: 2px;">{t}</span>' for t in curr_tags_list])
        sections.append(c_tags)

    # --- C: Vaikai (Gelsva) ---
    # .child_id jau yra užkrautas viršuje per Prefetching
    # child_recs = record.child_id.filtered(lambda r: isinstance(r.id, int))
    # c_attrs = child_recs.mapped('x_rmtools_mandatory_attributes').mapped('display_name')
    # unique_c = sorted(list(set(c_attrs)))
    
    # if unique_c:
    #     ch_tags = "".join([f'<span class="badge rounded-pill bg-warning-subtle text-warning-heading border border-warning-subtle" style="margin: 2px;">{a}</span>' for a in unique_c])
    #     sections.append(ch_tags)

    # # --- Rezultato sujungimas ---
    # if sections:
    #     sep = '<i class="oi oi-chevron-right text-muted mx-2" style="font-size: 0.7rem;"></i>'
    #     record[f_name] = f'<div class="d-flex flex-wrap align-items-center">{sep.join(sections)}</div>'

    child_attrs_list = []
    for child in record.child_id.filtered(lambda r: isinstance(r.id, (int, float))):
        for a in child.x_rmtools_mandatory_attributes:
            child_attrs_list.append((a.id, a.display_name))
    
    # Pašaliname dublikatus TIK vaikų lygmenyje (jei keli vaikai turi tą patį), 
    # bet paliekame lyginant su tėvais
    unique_c = sorted(list(set(child_attrs_list)))
    
    if unique_c:
        ch_tags = "".join([f'<span class="badge rounded-pill bg-warning-subtle text-warning-heading border border-warning-subtle" style="margin: 2px;">({c[0]}) {c[1]}</span>' for c in unique_c])
        sections.append(ch_tags)

    # --- Sujungimas ---
    if sections:
        sep = '<i class="oi oi-chevron-right text-muted mx-2" style="font-size: 0.7rem;"></i>'
        record['x_rmtools_parrent_current_child_atributes_html'] = f'<div class="d-flex flex-wrap align-items-center">{sep.join(sections)}</div>'