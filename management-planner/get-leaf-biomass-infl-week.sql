WITH cte AS
    (SELECT pb.id as "ID",
            pb.file_registry_id$ as "Plant Batch",
            i.infiltrated_on::date as "Infiltration Date",
            EXTRACT('week'
                    FROM i.infiltrated_on::date) as "Week",
            AVG(pm.avg_plant_weight_g) as "Avg Leaf Weight",
            SUM(i.plant_count) AS "Plant Count",
            AVG(pm.avg_plant_weight_g)*SUM(i.plant_count)/1000 as "Leaf Biomass Infiltrated (kg)"
     FROM plant_batches pb
     LEFT JOIN plant_measurements$raw pm ON pb.id = pm.plant_batch
     LEFT JOIN infiltrations i ON pb.id = i.plant_lot
     WHERE avg_plant_weight_g IS NOT NULL
     GROUP BY pb.id,
              "Week",
              i.infiltrated_on,
              pb.file_registry_id$
     ORDER BY "Infiltration Date"),
     cte2 as
    (SELECT "ID",
            "Plant Batch",
            STRING_AGG("Infiltration Date"::text, '; ') AS "Infiltration Date(s)",
            "Week" as "Week No.",
            AVG("Avg Leaf Weight") as "Leaf Weight Per Plant (g)",
            SUM("Plant Count") as "No. Plants",
            SUM("Leaf Biomass Infiltrated (kg)") as "Leaf Weight per Batch (kg)"
     FROM cte
     GROUP BY cte."Plant Batch",
              cte."ID",
              "Week No."
     ORDER BY "Infiltration Date(s)")
SELECT STRING_AGG("Plant Batch", '; ') as "Plant Batch ID's",
       STRING_AGG("Infiltration Date(s)", '; ') as "Dates of Infiltration",
       "Week No.",
       ROUND(AVG("Leaf Weight Per Plant (g)"::numeric), 2) as "Avg Leaf Weight Per Plant (g)",
       SUM("No. Plants") as "No. Plants Infiltrated",
       ROUND((AVG("Leaf Weight Per Plant (g)"::numeric)/1000)*SUM("No. Plants"), 2) as "Biomass Infiltrated (kg)"
FROM cte2
GROUP BY "Week No."
ORDER BY "Week No."