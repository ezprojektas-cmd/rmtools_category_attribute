# Prod 

for record in self:
    forbidden = set()
    
    # 1. APSAUGA: Jei įrašas neturi tikro ID, praleidžiame paiešką
    if not isinstance(record.id, int):
        record['x_rmtools_forbidden_attribute_ids'] = [(6, 0, [])]
        continue

    # 2. Aukštyn (Tėvai) - čia saugu, nes jei tėvas yra NewId, jis tiesiog nebus rastas
    curr = record.parent_id
    while curr:
        # Pridedame saugiklį: jei curr yra NewId, jo .ids bus tuščias arba mes jį ignoruojame
        if isinstance(curr.id, int) and curr.x_rmtools_mandatory_attributes:
            forbidden.update(curr.x_rmtools_mandatory_attributes.ids)
        curr = curr.parent_id
        
    # 3. Žemyn (Vaikai) - va čia buvo klaida
    # Kadangi jau patikrinome record.id viršuje, čia record.id yra tikras skaičius
    children = self.env['product.public.category'].search([('id', 'child_of', record.id)])
    
    for child in children:
        # Papildoma apsauga, nors search grąžins tik tikrus ID
        if child.id != record.id and child.x_rmtools_mandatory_attributes:
            forbidden.update(child.x_rmtools_mandatory_attributes.ids)
            
    # 4. Priskiriame ID sąrašą
    record['x_rmtools_forbidden_attribute_ids'] = [(6, 0, list(forbidden))]