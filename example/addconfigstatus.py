#!/usr/bin/python -x
import sqlite3
sql = """alter table service_config add column "service_config_status" VARCHAR(50) DEFAULT NULL;"""

status = {
1: "inactive",
2: "inactive",
3: "inactive",
4: "inactive",
5: "inactive",
6: "inactive",
7: "inactive",
8: "inactive",
9: "inactive",
10: "inactive",
11: "inactive",
12: "inactive",
13: "inactive",
14: "inactive",
15: "inactive",
16: "inactive",
17: "inactive",
18: "inactive",
19: "inactive",
20: "inactive",
21: "inactive",
22: "inactive",
23: "inactive",
24: "inactive",
25: "inactive",
26: "inactive",
27: "inactive",
28: "active",
29: "active",
30: "inactive",
31: "inactive",
32: "inactive",
33: "inactive",
34: "inactive",
35: "inactive",
36: "inactive",
37: "inactive",
38: "active",
39: "inactive",
40: "active",
41: "active",
42: "active",
43: "active"
}


conn = sqlite3.connect("masar.db-20140714")
cur = conn.cursor()

try:
    cur.execute(sql)
except sqlite3.OperationalError:
    print "sqlite3.OperationalError: duplicate column name: service_config_status"

for k, v in status.iteritems():
    sql = """update service_config set service_config_status = ? where service_config_id = ?"""
    cur.execute(sql, (v, k))
conn.commit()
conn.close()
print "finished."
