SELECT CONCAT(pb.file_registry_id$, ' ', pb.name) AS "ID",
       (CASE
            WHEN pb.name = 'S1-His' THEN COALESCE((qc.volume_ul/1000)*blitz_mgml, 0)
            ELSE COALESCE((qc.volume_ul/1000)*uv280_mgml, 0)
        END) AS "Mass (mg)"
FROM protein_batches pb
LEFT JOIN quality_control qc ON pb.id = qc.protein_batch
WHERE qc.date_time >= '2021-05-01'
       AND qc.date_time <= '2021-06-01'
       AND pb.file_registry_id$ != 'PR-B114'
       AND pb.file_registry_id$ != 'PR-B116'
       AND (qc.quality_control_passfail != 'Fail'
            OR qc.quality_control_passfail IS NULL)
ORDER BY pb.file_registry_id$