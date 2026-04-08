# x_rmtools_product_attribute_constraint_html
# type: htmt
# Model: Product Template Attribute Line
# Label: Warning Values
# Demendencies: value_ids
# Stored = false

for record in self:
    if len(record.value_ids) > 1:
        record['x_rmtools_product_attribute_constraint_html'] = """
            <div class="alert alert-danger m-0 p-1" role="alert" style="display:inline-block;">
                val>1
            </div>
        """
    else:
        record['x_rmtools_product_attribute_constraint_html'] = False