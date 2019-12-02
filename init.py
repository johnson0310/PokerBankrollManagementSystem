import pymysql


# Initialize connection to the mysql server,
# Return cursor
def init_sql():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='Johnson',
            passwd='foobar',
            database='PokerTracker'
        )
        cur = conn.cursor()

    except pymysql.connect.Error as error:
        print("Failed to connect to mySQL database, error: {}".format(error))
    return conn, cur
