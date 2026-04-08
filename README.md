# RMtools category attribute


## eComerce atrribute Constraint
1. Sukurta User-defined Default Variant Creation -> Never
2. ViewsInherited Variant Creation -> read only


## Product template > Attributes & Variants (Tab) > Attribute line add
1. Sukuriam Field `x_rmtools_product_attribute_constraint_html` kuris atvaizduojai jei prie atribututo priskirta value > 1
2. Sukuriam Field `x_rmtools_product_attribute_constraint_required` kuris padaromas required jei atribututo priskirta value > 1, kadangi grazinamas tuščias tai neleidzia issaugoti.
3. Sukuriam InheritedViews idedam i ta pati `RmTools: product.template.mandatory.attributes` pakeičiam į `RmTools: product.template.custom_fields`

## Product Template > Attributes & Variants (Tab) -> sukuriam mygtuka kuris sukurs trukstamus atributus.
<!-- 1. Sukuriam server action `RmTools: create product mandatory attributes lines` gal reikes istrinti  -->
1. Sukuriam papildoma lauka `x_rmtools_add_mandatory_attributes`, kuris bus boolean trigeris On Change Automation rules
2. Sukuriam Automation rules `RmTools: create madatory attributes`, Kuri sukuria naujas trukstabu atributu eilutes prie produktų.
3. Ikeliam mygtuka



Pastabas:
Ką reiketų sekti, kad sistema būtų tvarkinga sistem
- ar yra sukurta produktu variantu su kitokiu nustatymu nei `Never`
- ar yra priskirtu atributu su daugiau nei viena reiksme
- Parodyti produktus kurie neturi visų privalomu atributų
- parodyti produktus kurie turi daugiau nei numatyta atributų
- parodyti kategorijas kurios yra paskutinės, is ju neiseina jokiu šakų ir jos neturi aktyviu produktu
- Parodyti šaknines kategorijas kuriose yra produktų (šakninese negali buti)  ??? (turbut kad gali buti)
