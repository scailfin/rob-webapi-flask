from robcore.db.driver import DatabaseDriver
from psycopg2.extras import RealDictCursor

con = DatabaseDriver.get_connector().connect().con

cur = con.cursor(cursor_factory=RealDictCursor)
sql = 'SELECT u.user_id, b.benchmark_id, s.name '
sql += 'FROM api_user u, benchmark b, benchmark_submission s '
sql += 'WHERE u.user_id = s.owner_id AND s.benchmark_id = b.benchmark_id'
cur.execute(sql)
row = cur.fetchone()

print(row['user_id'])
