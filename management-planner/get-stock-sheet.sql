SELECT pb.name as "Name",
       pb.file_registry_id$ as "Benchling ID",
       e.label_cat_no as "Cat. No.",
       e.manufacture_date as "Manufacture Date",
       COALESCE(e.volume_si$*1000, ft.volume_si$*1000) as "Volume (ml)",
       cc.concentration_si*1000 as "Concentration (mg/ml)",
       COALESCE((e.volume_si$*1000*cc.concentration_si*1000), (ft.volume_si$*1000*cc.concentration_si*1000)) as "Mass (mg)",
       b.name as "Box Name",
       l.name as "Location"
FROM container_content cc
LEFT JOIN eppendorf_tube e ON e.id = cc.container_id
LEFT JOIN falcon_tube ft ON ft.id = cc.container_id
LEFT JOIN protein_batches pb ON cc.entity_id = pb.id
LEFT JOIN box b ON b.id = e.box_id$
LEFT JOIN location l ON b.location_id = l.id
OR ft.location_id$ = l.id
WHERE (l.name = 'Antigen Stocks'
       OR l.name = 'Antibody Stocks')
ORDER BY "Name" DESC