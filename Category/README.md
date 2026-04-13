# Projekto Laukai ir Logika

Šioje sekcijoje aprašomi pagrindiniai sistemos laukai ir jų veikimo principai.

## Naujas Web Kategorijos tab
### Mandatory attributes

## 📋 Laukų sąrašas

### 1. `x_studio_mandatory_attributes` prod `x_rmtools_mandatory_attributes`
stored
many2many
model: Website Product Category
Related Model: product.attribute


Šiame lauke saugomi visi konkretiam įrašui priskirti privalomi atributai.

### 2. `x_rmtools_parent_attributes`

Stored false
many2many
model: Website Product Category
dependencies: parent_id.x_studio_mandatory_attributes
Tai yra skaičiuojamas laukas, kuris surenka visus atributus iš aukštesnių lygmenų (tėvinių įrašų).

Žemiau pateikiamas kodas, skirtas rekursyviai surinkti visus tėvinius atributus per visą medžio struktūrą aukštyn:

```python
for record in self:
    all_parent_attrs = set()
    # Pradedame nuo tiesioginio tėvo
    current = record.parent_id
    
    while current:
        if current.x_studio_mandatory_attributes:
            all_parent_attrs.update(current.x_studio_mandatory_attributes.ids)
        
        # Lipame aukštyn per medį (rekursija)
        current = current.parent_id
        
    # Priskiriame surinktus ID į many2many lauką
    record['x_rmtools_parent_attributes'] = [(6, 0, list(all_parent_attrs))]
```


### 3. `x_forbidden_attribute_ids` prod `x_rmtoos_forbidden_attribute_ids`
non stored
many2many
model: Website Product Category
dependencies: parent_id.x_studio_mandatory_attributes


```python
for record in self:
    forbidden = set()
    
    # 1. APSAUGA: Jei įrašas neturi tikro ID, praleidžiame paiešką
    if not isinstance(record.id, int):
        record['x_forbidden_attribute_ids'] = [(6, 0, [])]
        continue

    # 2. Aukštyn (Tėvai) - čia saugu, nes jei tėvas yra NewId, jis tiesiog nebus rastas
    curr = record.parent_id
    while curr:
        # Pridedame saugiklį: jei curr yra NewId, jo .ids bus tuščias arba mes jį ignoruojame
        if isinstance(curr.id, int) and curr.x_studio_mandatory_attributes:
            forbidden.update(curr.x_studio_mandatory_attributes.ids)
        curr = curr.parent_id
        
    # 3. Žemyn (Vaikai) - va čia buvo klaida
    # Kadangi jau patikrinome record.id viršuje, čia record.id yra tikras skaičius
    children = self.env['product.public.category'].search([('id', 'child_of', record.id)])
    
    for child in children:
        # Papildoma apsauga, nors search grąžins tik tikrus ID
        if child.id != record.id and child.x_studio_mandatory_attributes:
            forbidden.update(child.x_studio_mandatory_attributes.ids)
            
    # 4. Priskiriame ID sąrašą
    record['x_forbidden_attribute_ids'] = [(6, 0, list(forbidden))]

```

### 4. `x_rmtools_formated_parent_html`
non stored
html
model: Website Product Category
dependencies: parent_id, x_studio_mandatory_attributes

```python
# Užtikriname, kad visi tėvai ir jų atributai būtų Cache atmintyje prieš pradedant ciklą
all_parents = self.mapped('parent_id')
all_parents.mapped('x_studio_mandatory_attributes') 

for record in self:
    if not record.id:
        record['x_rmtools_formated_parent_html'] = ""
        continue
    
    path_categories = []
    curr = record
    while curr:
        path_categories.append(curr)
        curr = curr.parent_id
    path_categories.reverse()
    
    html_parts = []
    total = len(path_categories)
    
    for index, cat in enumerate(path_categories):
        # Dabar 'cat' duomenys jau 100% yra Cache, jokių SQL užklausų čia nebus
        attrs = cat.x_studio_mandatory_attributes.mapped('name')
        
        if attrs:
            is_current = (index == total - 1)
            
            if is_current:
                badge_class = "bg-success-subtle text-success border border-success-subtle"
            else:
                badge_class = "badge rounded-pill bg-200 text-600 border"
            
            tags = "".join([
                f'<span class="badge rounded-pill {badge_class}" '
                f'style="margin: 2px;">{a}</span>' 
                for a in attrs
            ])
            html_parts.append(tags)
    
    if html_parts:
        sep = (
            '<div style="display: inline-flex; align-items: center; justify-content: center; min-height: 20px;">'
            '<i class="oi oi-chevron-right text-muted mx-2" style="font-size: 0.7rem;"></i>'
            '</div>'
        )
        record['x_rmtools_formated_parent_html'] = f'<div class="d-flex flex-wrap align-items: center;">{sep.join(html_parts)}</div>'
    else:
        record['x_rmtools_formated_parent_html'] = ""
```


### 5. Atributu filtravimas kategorijose
prie lauko `x_studio_mandatory_attributes` prideti domain 
`[('id', 'not in', x_forbidden_attribute_ids)]`


### 6. `x_rmtools_parrent_current_child_atributes_html`
non stored
html
model: Website Product Category
dependencies: parent_id, x_studio_mandatory_attributes, child_id

```python
# 1. PREFETCHING (Sprendžiame N+1 problemą)
# Išfiltruojame tikrus įrašus, kad išvengtume NewId klaidų masinėje užklausoje
valid_records = self.filtered(lambda r: isinstance(r.id, int))

if valid_records:
    # Vienu kartu paimame visus tėvus ir vaikus visoms matomoms eilutėms
    all_parents = valid_records.mapped('parent_id')
    all_children = valid_records.mapped('child_id')
    
    # "Paliečiame" atributus, kad Odoo juos visus užkrautų į Cache (viena SQL užklausa)
    if all_parents:
        all_parents.mapped('x_studio_mandatory_attributes')
    if all_children:
        all_children.mapped('x_studio_mandatory_attributes')
    # Taip pat užkrauname pačių įrašų atributus
    valid_records.mapped('x_studio_mandatory_attributes')

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
        # attrs = p.x_studio_mandatory_attributes.mapped('display_name')
        # for a in attrs:
        #     p_tags.append(f'<span class="badge rounded-pill bg-200 text-600 border" style="margin: 2px;">{a}</span>')
        
        for attr in p.x_studio_mandatory_attributes:
            label = f"({attr.id}) {attr.display_name}"
            p_tags.append(f'<span class="badge rounded-pill bg-200 text-600 border" style="margin: 2px;">{label}</span>')

    if p_tags:
        sections.append("".join(p_tags))

    # --- B: Esamas (Žalia) ---
    # curr_attrs = record.x_studio_mandatory_attributes.mapped('display_name')
    # if curr_attrs:
    #     c_tags = "".join([f'<span class="badge rounded-pill bg-success-subtle text-success border border-success-subtle" style="margin: 2px;">{a}</span>' for a in curr_attrs])
    #     sections.append(c_tags)
    curr_tags_list = [f"({a.id}) {a.display_name}" for a in record.x_studio_mandatory_attributes]
    if curr_tags_list:
        c_tags = "".join([f'<span class="badge rounded-pill bg-success-subtle text-success border border-success-subtle" style="margin: 2px;">{t}</span>' for t in curr_tags_list])
        sections.append(c_tags)

    # --- C: Vaikai (Gelsva) ---
    # .child_id jau yra užkrautas viršuje per Prefetching
    # child_recs = record.child_id.filtered(lambda r: isinstance(r.id, int))
    # c_attrs = child_recs.mapped('x_studio_mandatory_attributes').mapped('display_name')
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
        for a in child.x_studio_mandatory_attributes:
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

```

Planas:
Categorijos:
- prie mandatory sudėti kad patytusi ir teviviniai ir current ir vaikiniai <- padaryta
- paleisti koda ant visu categoriju (padaryti kad imtu tik web site rmtolls. Pries tai patikrinti kiek yra i kitu saito)
- Jei spesiu isvesti i produktus privalomus atributus pagal categorijas.

- issivedam kiek atributu yra ne rmtools.eu
- issivedam kiek atributu nera nustatuta "Never" bet tik prie aktyviu.
