--We define that number of times that a homogenate has been split
WITH total_vol as
    (SELECT h.file_registry_id$ as id,
            COUNT(h.file_registry_id$),
            SUM(c.homogenate_volume_l) as total_vol
     FROM clarificates c
     LEFT JOIN jsonb_array_elements_text(c.homogenate) hom_id ON TRUE
     LEFT JOIN homogenates h ON hom_id = h.id
     GROUP BY h.file_registry_id$
     ORDER BY h.file_registry_id$), --We get the yield per protein batch taking into account if the homogenate has been split
yield_prb AS
    (SELECT CONCAT(pb.file_registry_id$, ' ', pb.name) AS "ID",
            (CASE
                 WHEN pb.name = 'S1-His' THEN ROUND((COALESCE((qc.volume_ul/1000)*blitz_mgml, 0)/ROUND(((c.homogenate_volume_l/total_vol.total_vol)*h.leaf_weight)::numeric, 2))::numeric, 2)
                 ELSE ROUND((COALESCE((qc.volume_ul/1000)*uv280_mgml, 0)/ROUND(((c.homogenate_volume_l/total_vol.total_vol)*h.leaf_weight)::numeric, 2))::numeric, 2)
             END) AS yield_mgkg --This defines that we should use blitz conc. to calculate S1-His yields and A280 for other yields

     FROM protein_batches pb
     LEFT JOIN quality_control qc ON pb.id = qc.protein_batch
     LEFT JOIN jsonb_array_elements_text(pb.clarificate_batch) cla_id ON TRUE
     LEFT JOIN clarificates c ON cla_id = c.id
     LEFT JOIN jsonb_array_elements_text(c.homogenate) hom_id ON TRUE
     LEFT JOIN homogenates h ON hom_id = h.id
     LEFT JOIN total_vol ON h.file_registry_id$ = total_vol.id
     WHERE qc.date_time >= (CURRENT_DATE - INTERVAL '3 months')
     ORDER BY h.file_registry_id$, pb.file_registry_id$)
SELECT ROUND(AVG(yield_mgkg)::numeric, 2) AS "Avg Yield (mg/kg) 3 Months"
FROM yield_prb
WHERE yield_mgkg IS NOT NULL
    AND yield_mgkg != 0