import init
import users
import player_stats
import current_session
import performance_against
import personal_session_log
import session_log
from users import user
from current_session import session

import pymysql
import time
import venmo
from contextlib import closing
from datetime import datetime

### Init ###

# Init mySQL connection
db, cur = init.init_sql()

with closing(db.cursor()) as cur:
    # query = 'INSERT INTO users (first_name, last_name, nick_name, venmo_address, password, is_admin, register_date)
    # ' \ 'VALUES (%s,%s,%s,%s,%s,%s,%s)'

    # value = ('ASD', 'DDD', '@Benm39', 1234)

    # New user format:
    # First name, last name, venmo address, password

    # sql.users_add_new(db, value)
    # users.change_password(db, 7, "SSse3")
    # print(users.get_id_by_nick_name(db, 'Johnson'))

    sesh1 = session()
    user1 = user(2, 'Ben', 'Miller', 'ASD', '@Benm39', 'password', 0, datetime.now())
    user2 = user(2, 'Johnson', 'BBB', 'ASS', '@Benm39', 'password', 0, datetime.now())

    user3 = users.add_new_user(db, ('John', 'Doe', '@33E', 'PAS'))
    sesh1.add_user(db, user2)

    current_session.show_session_status(db)

    # sql.users_show_all(db)
db.close()

# cur.execute(query, value)
# db.commit()

# print(cur.rowcount, "record inserted")

# cur.execute('SELECT * FROM users')
# rows = cur.fetchall()
#
# for row in rows:
#     print(row)
