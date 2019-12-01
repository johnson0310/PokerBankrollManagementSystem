import pymysql


# Initialize connection to the mysql server,
# Return cursor
def init_sql():
    conn = pymysql.connect(
        host='localhost',
        user='Johnson',
        passwd='foobar',
        database='PokerTracker2'
    )
    cur = conn.cursor()
    return cur
