SELECT l.protein_name as "Name", l.file_registry_id$, SUM(lb.weight_g) as "Kg"
    FROM container_content cc
    JOIN leaf_box lb ON lb.id = cc.container_id
    LEFT JOIN leaves l ON cc.entity_id = l.id
    LEFT JOIN location loc ON lb.location_id$ = loc.id
    WHERE lb.archived$ = 'false'
    GROUP BY l.protein_name, l.file_registry_id$