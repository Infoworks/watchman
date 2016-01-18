from os import path
from utils import misc
import jaydebeapi
import sys
import json


validation_sql = '''
--test1: no rows of current_view are in history_view
--test2, test3, test4: all dates are derived from the equivalent timestamp values
--test5: confirm the assumption that ZIW_START_TIME_STAMP < ZIW_END_TIME_STAMP
--test6: all rows of history_view are inactive
--test7: all rows of current_view are active
--test8: all rows of current_view have unique rowid
--test9: only the latest row is marked as active
--test10: no overlapping start-end

WITH
current_view AS (SELECT * FROM table),
history_view AS (SELECT * FROM history_vw_table),
all_view AS (SELECT * FROM current_view UNION DISTINCT SELECT * FROM history_view),
temp1 AS (SELECT count(*) c FROM all_view),
temp2 AS (SELECT count(*) c FROM history_view),
temp3 AS (SELECT count(*) c FROM current_view),
test1 AS (SELECT (temp1.c - temp2.c - temp3.c) c FROM temp1, temp2, temp3),
test2 AS (SELECT count(*) c FROM all_view WHERE cast(ZIW_LOAD_TIME_STAMP AS date) <> ZIW_LOAD_DATE),
test3 AS (SELECT count(*) c FROM all_view WHERE cast(ZIW_START_TIME_STAMP AS date) <> ZIW_START_DATE),
test4 AS (SELECT count(*) c FROM
    all_view WHERE months_between(cast(ZIW_END_TIME_STAMP AS date), ZIW_END_DATE) <> 0),
test5 AS (SELECT count(*) c FROM all_view WHERE months_between(ZIW_END_TIME_STAMP, ZIW_START_TIME_STAMP) < 0),
test6 AS (SELECT count(*) c FROM history_view WHERE ZIW_ACTIVE='true'),
test7 AS (SELECT count(*) c FROM current_view WHERE ZIW_ACTIVE='false'),
test8 AS (SELECT count(*) c FROM (SELECT 1 FROM current_view GROUP BY id HAVING count(*) > 1) i1),
test9 AS (SELECT count(*) c FROM all_view i1 INNER JOIN
    (SELECT id, MAX(ZIW_START_TIME_STAMP) ZIW_START_TIME_STAMP FROM all_view i2 GROUP BY id) i2
    ON (i1.id=i2.id) WHERE i1.ZIW_ACTIVE='true' AND i1.ZIW_START_TIME_STAMP<i2.ZIW_START_TIME_STAMP),
temp4 AS (SELECT id, ZIW_START_TIME_STAMP, ZIW_END_TIME_STAMP,
    row_number() OVER (ORDER BY id, ZIW_START_TIME_STAMP) AS rowid FROM all_view),
test10 AS (SELECT count(*) c FROM temp4 i1 INNER JOIN temp4 i2 ON
    (i1.id=i2.id AND i2.rowid=(i1.rowid+1)) WHERE
    months_between(i1.ZIW_END_TIME_STAMP, i2.ZIW_START_TIME_STAMP) < 0)
SELECT test1.c, test2.c, test3.c, test4.c, test5.c, test6.c, test7.c, test8.c, test9.c, test10.c FROM
    test1, test2, test3, test4, test5, test6, test7, test8, test9, test10
'''


def main(config_path):
    with open(config_path, 'r') as config_file:
        test_conf = json.loads(config_file.read())['config']
        config_path = path.join(path.dirname(config_path), test_conf['source'])
        with open(config_path, 'r') as config_file:
            test_conf = json.loads(config_file.read())['config']

    cursor = jaydebeapi.connect(
        'org.apache.hive.jdbc.HiveDriver',
        ['jdbc:hive2://localhost:10000/%s?hive.execution.engine=tez' % test_conf['hive_schema'], '', '']).cursor()

    for table in test_conf['tables']:
        table_name = table['table']
        print '==============='
        print 'Validating', table_name

        tests_failed = False
        cursor.execute(validation_sql.replace('table', table_name))
        result = cursor.fetchall()
        for i, r in enumerate(result[0]):
            r = r.value
            if r != 0:
                print 'Test %d failed. Result: %d.' % (i + 1, r)
                tests_failed = True

        if tests_failed:
            misc.g_exit_code = 1
        else:
            print 'All tests passed.'


if __name__ == '__main__':
    main(sys.argv[1])
    sys.exit(misc.g_exit_code)
