WITH total_vol as
    (SELECT h.file_registry_id$ as id,
            COUNT(h.file_registry_id$),
            SUM(c.homogenate_volume_l) as total_vol
     FROM clarificates c
     LEFT JOIN homogenates h ON h.id = c.homogenate
     GROUP BY h.file_registry_id$
     ORDER BY h.file_registry_id$)
SELECT CONCAT(pb.file_registry_id$, ' ', pb.name) AS "ID",
       (CASE
            WHEN pb.name = 'S1-His' THEN ROUND((COALESCE((qc.volume_ul/1000)*blitz_mgml, 0)/ROUND(((c.homogenate_volume_l/total_vol.total_vol)*h.leaf_weight)::numeric, 2))::numeric, 2)
            ELSE ROUND((COALESCE((qc.volume_ul/1000)*uv280_mgml, 0)/ROUND(((c.homogenate_volume_l/total_vol.total_vol)*h.leaf_weight)::numeric, 2))::numeric, 2)
        END) AS yield_mgkg
FROM protein_batches pb
LEFT JOIN jsonb_array_elements_text(pb.clarificate_batch) AS cla_id ON TRUE
LEFT JOIN clarificates c ON cla_id = c.id
LEFT JOIN homogenates h ON c.homogenate = h.id
LEFT JOIN total_vol ON h.file_registry_id$ = total_vol.id
LEFT JOIN quality_control qc ON pb.id = qc.protein_batch
WHERE qc.date_time >= '2021-04-01'
    AND qc.date_time <= '2021-04-30'
ORDER BY pb.file_registry_id$