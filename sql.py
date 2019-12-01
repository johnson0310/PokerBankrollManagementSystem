import pymysql
import init
from pprint import pprint
from contextlib import closing
import datetime


# Create new users
# Nick name default is first name, if duplicated, then join first and last name
def add_new_user(db, value):
    # value format: First name, last name, venmo address, password

    cur = db.cursor()

    first_name, last_name, venmo_address, password = value

    # Check if current first name already exists in the database, then nick_name = first_name + last_name
    # Else nick_name = first_name
    cur.execute('SELECT first_name FROM users')
    existed_first_name = cur.fetchall()

    if first_name in [name for names in existed_first_name for name in names]:
        nick_name = value[0] + value[1]
        value = value[:2] + (nick_name,) + value[2:] + (0, datetime.datetime.now())
        print('First name "{}" exists in the database, nick name will be "{}" instead.'.format(first_name, nick_name))

    else:
        value = value[:2] + (first_name,) + value[2:] + (0, datetime.datetime.now())

    # Query to insert user into TABLE users
    query = 'INSERT INTO users (first_name, last_name, nick_name, venmo_address, password, is_admin, register_date) ' \
            'VALUES (%s,%s,%s,%s,%s,%s,%s)'

    # Execute query
    try:
        cur.execute(query, value)
        db.commit()
        print("Created user '{}'.".format(value[2]))
        print(cur.rowcount, "record inserted.")
    except pymysql.err as error:
        print("Failed to add user. \nError message:\n{}".format(error))


def show_all_users(db):
    cur = db.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    for user in users:
        print(user)
