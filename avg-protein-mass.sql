--Get relevant QC data for each protein batch analysed less than 3 months ago
WITH prb_qc AS (
SELECT  prb.file_registry_id$ AS prb_id, prb.name, DATE_PART('week', qc.date_time) AS week, qc.volume_ul/1000 as volume_ml, 
        qc.uv280_mgml AS conc_mgml, qc.blitz_mgml
FROM protein_batches prb
LEFT JOIN quality_control qc ON prb.id = qc.protein_batch
WHERE qc.date_time >= (CURRENT_DATE - INTERVAL '3 months') 
ORDER BY prb.file_registry_id$
),

--Calculate the mass (mg) for each protein batch - S1-His is calculated via Blitz reading
mass AS (
SELECT prb_id, week,
(CASE WHEN name = 'S1-His' THEN volume_ml * blitz_mgml
ELSE volume_ml * conc_mgml END) AS mass_mg
FROM prb_qc
),

mass_per_week AS (
SELECT week, ROUND(SUM(mass_mg)::numeric, 2) AS mg_produced
FROM mass
WHERE mass_mg IS NOT NULL
GROUP BY week
ORDER BY week
)

SELECT ROUND(AVG(mg_produced)::numeric, 2) AS "Avg Mg Protein Produced/Week 3 Months"
FROM mass_per_week