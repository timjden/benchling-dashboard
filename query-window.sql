SELECT file_registry_id$,
       clarificate_batch,
       clarificate_volume,
       name,
       batch_type
FROM protein_batches pb
ORDER BY file_registry_id$