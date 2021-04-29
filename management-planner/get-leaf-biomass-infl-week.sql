WITH leaf_mass AS
        (SELECT pb.id,
                pb.file_registry_id$, AVG(pm.avg_plant_weight_g)
         FROM plant_batches pb
         JOIN plant_measurements$raw pm ON pb.id = pm.plant_batch
         WHERE avg_plant_weight_g IS NOT NULL
         GROUP BY pb.id,
                  pb.file_registry_id$),
     weeks AS
        (SELECT DATE_PART('week', i.infiltrated_on) AS "Week",
                SUM(i.plant_count) AS "No. Plants Infiltrated",
                (SUM(i.plant_count) * SUM(COALESCE(pm.avg, 0)))/1000 AS "Leaf Biomass Infiltrated (Kg)"
         FROM infiltrations i
         LEFT JOIN plant_batches pb ON i.plant_lot = pb.id
         LEFT JOIN leaf_mass pm ON pb.id = pm.id
         WHERE i.infiltrated_on >= '2021-02-22'
         GROUP BY i.file_registry_id$, i.infiltrated_on
         ORDER BY i.file_registry_id$)
SELECT "Week",
       SUM("No. Plants Infiltrated") AS "No. of Plants Infiltrated",
       ROUND(SUM("Leaf Biomass Infiltrated (Kg)")::numeric, 2) AS "Leaf Biomass Infiltrated (Kg)",
       ROUND(((SUM("Leaf Biomass Infiltrated (Kg)"))/(SUM("No. Plants Infiltrated"))*1000)::numeric, 2) AS "Grams per Plant"
FROM weeks
GROUP BY "Week"
ORDER BY "Week"