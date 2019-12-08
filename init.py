import pymysql


# Initialize connection to the mysql server,
# Return cursor
def init_sql():
    print('\n' + '*' * 60)
    print('\nInitiating SQL server connection ...')

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

    print('\nConnected to the SQL server ...')

    return conn, cur
