# Užtikriname, kad visi tėvai ir jų atributai būtų Cache atmintyje prieš pradedant ciklą
all_parents = self.mapped('parent_id')
all_parents.mapped('x_rmtools_mandatory_attributes') 

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
        attrs = cat.x_rmtools_mandatory_attributes.mapped('name')
        
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