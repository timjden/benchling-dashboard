SELECT pb.name as "Product Name", --COALESCE(e.volume_si$*1000, ft.volume_si$*1000) as "Volume (ml)",
 --cc.concentration_si*1000 as "Concentration (mg/ml)",
 SUM(COALESCE((e.volume_si$*1000*cc.concentration_si*1000), (ft.volume_si$*1000*cc.concentration_si*1000))) as "Mass (mg)",
 COALESCE(e.archive_purpose$, ft.archive_purpose$) as "Purpose"
FROM container_content cc
LEFT JOIN eppendorf_tube$raw e ON e.id = cc.container_id
LEFT JOIN falcon_tube$raw ft ON ft.id = cc.container_id
LEFT JOIN protein_batches pb ON cc.entity_id = pb.id
WHERE e.archived$ = 'true'
    AND e.archive_purpose$ = 'Shipped'
GROUP BY pb.name,
         "Purpose"