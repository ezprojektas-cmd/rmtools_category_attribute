# Projekto Laukai ir Logika

Šioje sekcijoje aprašomi pagrindiniai sistemos laukai ir jų veikimo principai.

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


### 2. `x_forbidden_attribute_ids`
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
    # children = self.env['product.public.category'].search([('id', 'child_of', record.id)])
    # for child in children:
    #     if child.id != record.id and child.x_studio_mandatory_attributes:
    #         forbidden.update(child.x_studio_mandatory_attributes.ids)
            
    # Priskiriame ID sąrašą
    record['x_forbidden_attribute_ids'] = [(6, 0, list(forbidden))]

```