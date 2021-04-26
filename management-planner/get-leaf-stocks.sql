SELECT l.protein_name as "Product Name",
       SUM(lb.weight_g) as "Kg"
FROM container_content cc
JOIN leaf_box lb ON lb.id = cc.container_id
LEFT JOIN leaves l ON cc.entity_id = l.id
LEFT JOIN location loc ON lb.location_id$ = loc.id
WHERE lb.created_at$ <= '2021-03-31'
    AND lb.archived$ = 'false'
GROUP BY l.protein_name