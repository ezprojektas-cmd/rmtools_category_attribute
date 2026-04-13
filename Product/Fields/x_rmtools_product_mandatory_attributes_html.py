# x_rmtools_product_mandatory_attributes_html
# type: htmt
# Label: Product Mandatory Attributes
# Demendencies: public_categ_ids, attribute_line_ids.attribute_id, public_categ_ids.x_rmtools_mandatory_attributes for prod public_categ_ids.x_rmtools_mandatory_attributes
# Stored = false

# 1. Iš anksto užkrauname visus susijusius duomenis visiems įrašams (Prefetching)
self.mapped('public_categ_ids')
self.mapped('attribute_line_ids.attribute_id')

for record in self:
    categories = record.public_categ_ids 
    if not categories:
        record['x_rmtools_product_mandatory_attributes_html'] = False
        continue

    # Naudojame set() greitesnei paieškai (O(1) vietoj O(n))
    # existing_attr_ids = set(record.attribute_line_ids.attribute_id.ids).ids
    existing_attr_ids = record.attribute_line_ids.mapped('attribute_id').ids

    # existing_attr_ids = set()
    # for line in record.attribute_line_ids:
    #     if line.attribute_id:
    #         # paimame .id, kuris Odoo 18 automatiškai ištraukia tikrąjį ID net iš NewId
    #         existing_attr_ids.add(line.attribute_id.id)
    
    html_output = '<div class="d-flex flex-column gap-4">'
    
    for cat in categories:
        # 2. Optimizuota hierarchija: naudojame parent_path, jei įmanoma, 
        # bet Technical režime paprasčiausia naudoti cat.parent_id ciklą, 
        # nes Odoo 18 turi gerą cache tėvinėms kategorijoms.
        category_hierarchy = []
        curr = cat
        while curr:
            category_hierarchy.insert(0, curr)
            curr = curr.parent_id
        
        cat_path = " <i class='fa fa-angle-right mx-1 small opacity-50'></i> ".join([c.name for c in category_hierarchy])
        
        html_output += '<div>'
        html_output += f'<div class="mb-2 small text-muted fw-bold italic" style="letter-spacing: 0.5px;">{cat_path}</div>'
        html_output += '<div class="d-flex flex-wrap gap-1 align-items-center">'
        
        levels_with_attrs = []
        for c in category_hierarchy:
            # Prieiga prie Studio lauko
            mandatory_attrs = c.x_rmtools_mandatory_attributes
            if not mandatory_attrs:
                continue
                
            attr_badges = []
            # Rūšiuojame atmintyje (Python lygmenyje), kad neliestume DB
            for attr in mandatory_attrs.sorted('name'):
                actual_id = attr._origin.id if attr._origin else attr.id
                is_existing = actual_id in existing_attr_ids
                # is_existing = attr.id in existing_attr_ids
                color_index = "10" if is_existing else "1"
                icon = '' if is_existing else 'fa-exclamation'
                
                tag_style = "padding: 1px 10px; line-height: 1.5; font-size: 12px; height: 22px; cursor: default;"
                tag_classes = f"o_tag d-inline-flex align-items-center mw-100 o_badge badge rounded-pill o_tag_color_{color_index}"
                
                attr_badges.append(f"""
                    <span class="{tag_classes}" style="{tag_style}">
                        <i class="fa {icon} {'me-1' if icon else ''}" style="font-size: 10px;"></i>
                        <span class="text-truncate">{attr.name}</span>
                    </span>
                """)
            
            if attr_badges:
                levels_with_attrs.append(" ".join(attr_badges))
        
        if levels_with_attrs:
            separator = '<i class="fa font-weight-bold fa-angle-right mx-2 text-muted opacity-75"></i>'
            html_output += separator.join(levels_with_attrs)
        else:
            html_output += '<span class="text-muted small italic" style="font-size: 11px;">No mandatory attributes defined</span>'
            
        html_output += '</div></div>'
        
    html_output += '</div>'
    record['x_rmtools_product_mandatory_attributes_html'] = html_output