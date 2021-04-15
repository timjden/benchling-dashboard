-- 3 Month Average Plant Leaf Biomass Prior to Infiltration

--Define table that lists the leaf biomass per plant batch (pb) prior to infiltration
WITH biomass_per_pb AS (
SELECT  pb.file_registry_id$ AS pb_id, AVG(avg_plant_weight_g) AS leaf_biomass_g
FROM plant_batches pb
LEFT JOIN plant_measurements pm ON pb.id = pm.plant_batch
LEFT JOIN infiltrations i ON pb.id = i.plant_lot
WHERE avg_plant_weight_g IS NOT NULL
AND (i.infiltrated_on >= (CURRENT_DATE - INTERVAL '3 months')) -- Specify that only pb's infiltrated less than 3 months ago should be listed
GROUP BY pb.file_registry_id$
ORDER BY pb.file_registry_id$
)

--Select the average leaf biomass of all plant batches infiltrated less than 3 months ago
SELECT ROUND(AVG(leaf_biomass_g)::numeric, 2) AS "Avg Leaf Biomass per Plant (3 Months)"
FROM biomass_per_pb