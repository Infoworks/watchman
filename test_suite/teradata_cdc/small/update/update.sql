UPDATE type_one SET version=version+1, record_update_ts=CURRENT_TIMESTAMP WHERE id <= 10;

UPDATE type_two t1 SET expiry_ts=CURRENT_TIMESTAMP WHERE t1.id <= 10 AND t1.version=(SELECT max(version) version FROM type_two t2 GROUP BY t2.id WHERE t2.id=t1.id);
INSERT INTO type_two (id, version, effective_ts, expiry_ts) SELECT id, max(version)+1, CURRENT_TIMESTAMP AS effective_ts, '2999-12-31 23:59:59' AS expiry_ts FROM type_two WHERE id <= 10 GROUP BY id;

