# Projekto Laukai ir Logika

Šioje sekcijoje aprašomi pagrindiniai sistemos laukai ir jų veikimo principai.

## Naujas Web Kategorijos tab
### Mandatory attributes

## 📋 Laukų sąrašas

### 1. `x_studio_mandatory_attributes`
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


### 3. `x_forbidden_attribute_ids`
non stored
many2many
model: Website Product Category
dependencies: parent_id.x_studio_mandatory_attributes


```python
# for record in self:
#     forbidden_ids = set()
    
#     # 1. Surenkame iš visų tėvų (aukštyn)
#     current = record.parent_id
#     while current:
#         if current.x_studio_mandatory_attributes:
#             forbidden_ids.update(current.x_studio_mandatory_attributes.ids)
#         current = current.parent_id
        
#     # 2. Surenkame iš visų vaikų (žemyn)
#     # Search randa visas dukterines kategorijas, kurios tėvų medyje turi šią kategoriją
#     children = self.env['product.public.category'].search([('id', 'child_of', record.id)])
#     for child in children:
#         if child.id != record.id and child.x_studio_mandatory_attributes:
#             forbidden_ids.update(child.x_studio_mandatory_attributes.ids)
            
#     record['x_forbidden_attribute_ids'] = [(6, 0, list(forbidden_ids))]
    
for record in self:
    forbidden = set()
    
    # Aukštyn (Tėvai)
    curr = record.parent_id
    while curr:
        if curr.x_studio_mandatory_attributes:
            forbidden.update(curr.x_studio_mandatory_attributes.ids)
        curr = curr.parent_id
        
    # Žemyn (Vaikai)
    children = self.env['product.public.category'].search([('id', 'child_of', record.id)])
    for child in children:
        if child.id != record.id and child.x_studio_mandatory_attributes:
            forbidden.update(child.x_studio_mandatory_attributes.ids)
            
    # Priskiriame ID sąrašą
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

