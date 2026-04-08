# RmTools: create madatory attributes 
# model: Product
# On UI Change 
# When Updating: Prideti atributus 

if record.x_rmtools_add_mandatory_attributes:
    # 1. Privalomos kategorijos (lipame aukštyn)
    all_categories = record.public_categ_ids
    temp_cats = record.public_categ_ids
    
    while temp_cats.mapped('parent_id'):
        temp_cats = temp_cats.mapped('parent_id')
        all_categories |= temp_cats

    # 2. Ištraukiame tikruosius ID sąrašą [.ids paverčia NewId į paprastus skaičius]
    mandatory_attr_ids = all_categories.mapped('x_studio_mandatory_attributes').ids
    
    existing_ids = record.attribute_line_ids.mapped('attribute_id').ids
    
    missing_ids = [i for i in mandatory_attr_ids if i not in existing_ids]
    
    new_commands = []
    for m_id in missing_ids:
        log(f">>> Ruošiame komandą ID pridėjimui: {m_id}", level='info')
        # (0, 0, {values}) - tai standartinis Odoo būdas pridėti naują eilutę į x2many lauką
        new_commands.append(Command.create({
            'attribute_id': m_id,
            'value_ids': [], # Paliekame tuščią, kad vartotojas pats pasirinktų reikšmę
        }))

    # 6. Atnaujiname įrašą (record.update)
    # Svarbu: viską darome vienu kartu, kad išvengtume klaidų
    if new_commands:
        record.update({
            'attribute_line_ids': new_commands,
            'x_rmtools_add_mandatory_attributes': False
        })
        # log(">>> UI sėkmingai atnaujintas su naujomis eilutėmis", level='info')
    else:
        # Jei trūkstamų nebuvo, tiesiog išjungiame jungiklį
        record.update({'x_rmtools_add_mandatory_attributes': False})