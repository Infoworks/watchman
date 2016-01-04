INSERT INTO type_one (version, record_add_ts, record_update_ts) VALUES (2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1' SECOND)
INSERT INTO type_one (version, record_add_ts, record_update_ts) VALUES (2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1' SECOND)
INSERT INTO type_one (version, record_add_ts, record_update_ts) VALUES (2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1' SECOND)
INSERT INTO type_one (version, record_add_ts, record_update_ts) VALUES (2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1' SECOND)
INSERT INTO type_one (version, record_add_ts, record_update_ts) VALUES (2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1' SECOND)

INSERT INTO type_two (effective_ts, expiry_ts) VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1' SECOND)
INSERT INTO type_two (effective_ts, expiry_ts) VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1' SECOND)
INSERT INTO type_two (effective_ts, expiry_ts) VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1' SECOND)
INSERT INTO type_two (effective_ts, expiry_ts) VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1' SECOND)
INSERT INTO type_two (effective_ts, expiry_ts) VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1' SECOND)

INSERT INTO type_two (id, version, effective_ts, expiry_ts) SELECT id, max(version)+1, CURRENT_TIMESTAMP + INTERVAL '1' SECOND, '2999-12-31 23:59:59' AS expiry_ts FROM type_two WHERE id > 1000010 GROUP BY id;

