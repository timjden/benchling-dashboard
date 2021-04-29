WITH latest_run AS
    (SELECT DISTINCT ON (pb.name) pb.name,
                        qc.date_time,
                        (CASE
                             WHEN pb.name = 'S1-His' THEN qc.blitz_mgml*(qc.volume_ul/1000)
                             ELSE qc.uv280_mgml*(qc.volume_ul/1000)
                         END) mass,
                        h.leaf_weight
     FROM protein_batches$raw pb
     LEFT JOIN jsonb_array_elements_text(pb.clarificate_batch) cla_id ON TRUE
     LEFT JOIN clarificates c ON cla_id = c.id
     LEFT JOIN homogenates h ON c.homogenate = h.id
     LEFT JOIN quality_control qc ON pb.id = qc.protein_batch
     WHERE pb.name IS NOT NULL
         AND qc.quality_control_passfail != 'Fail'
         AND qc.date_time >= '2021-03-01'
     ORDER BY pb.name,
              qc.date_time DESC)
SELECT "name" as "Protein Name",
       SUBSTRING(date_time::text, 1, 10) as "Date",
       ROUND(mass::numeric, 2) as "Protein Mass (mg)",
       ROUND(leaf_weight::numeric, 2) "Leaf Mass (Kg)",
       ROUND((mass/leaf_weight)::numeric, 2) as "Yield (mg/kg)"
FROM latest_run