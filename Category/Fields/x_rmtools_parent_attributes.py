for record in self:
    all_parent_attrs = set()
    # Pradedame nuo tiesioginio tėvo
    current = record.parent_id
    
    while current:
        if current.x_rmtools_mandatory_attributes:
            all_parent_attrs.update(current.x_rmtools_mandatory_attributes.ids)
        
        # Lipame aukštyn per medį
        current = current.parent_id
        
    record['x_rmtools_parent_attributes'] = [(6, 0, list(all_parent_attrs))]