import pymysql
import init
from pprint import pprint
from contextlib import closing
import datetime


# Converts tuple of strings into 1 string
def tuple_to_str(tup):
    result = ''.join(tup)
    return result


# Create new users
# Nick name default is first name, if duplicated, then join first and last name
def users_add_new(db, value):
    # value format: First name, last name, venmo address, password

    try:
        cur = db.cursor()

        first_name, last_name, venmo_address, password = value

        # Check if current first name already exists in the database, then nick_name = first_name + last_name
        # Else nick_name = first_name
        cur.execute('SELECT first_name FROM users')
        existed_first_name = cur.fetchall()

        if first_name in [name for names in existed_first_name for name in names]:
            nick_name = value[0] + value[1]
            value = value[:2] + (nick_name,) + value[2:] + (0, datetime.datetime.now())
            print('\nFirst name "{}" exists in the database, nick name will be "{}" instead.'.format(first_name,
                                                                                                     nick_name))

        else:
            value = value[:2] + (first_name,) + value[2:] + (0, datetime.datetime.now())

        # Query to insert user into TABLE users
        query = 'INSERT INTO users (first_name, last_name, nick_name, venmo_address, password, is_admin, register_date) ' \
                'VALUES (%s,%s,%s,%s,%s,%s,%s)'

        # Executing query
        cur.execute(query, value)
    except pymysql.Error as e:
        db.rollback()
        print("Failed to add new user")
        print(e)

    # No error, commit changes
    db.commit()
    print("\nCreated user '{}'.".format(value[2]))
    print(cur.rowcount, "record inserted.")


# Change nick name for specific user
def users_change_nick_name(db, user_id, new_nick_name):
    # id: INT, name: String
    try:
        cur = db.cursor()

        # Find old nick name for corresponding user_id
        cur.execute("""SELECT nick_name FROM users WHERE id = %s""", (user_id,))
        old_nick_name = tuple_to_str(cur.fetchone())

        # Check if the old nick name is the same as the new nick name
        if old_nick_name == new_nick_name:
            print("\nYour new nick name has to be different from the old nick name you fool.")
            return

        # Executing query
        cur.execute("""UPDATE users SET nick_name = %s WHERE id = %s""", (new_nick_name, user_id))

    except pymysql.Error as e:
        db.rollback()
        print("\nFailed to change nickname.\n")
        print(e)

    # No error, commit changes
    db.commit()
    print('\nNick name for user ID: {} changed from "{}" to "{}"'.format(user_id, old_nick_name, new_nick_name))
    print(cur.rowcount, "record changed.")



# Show all existing users
def users_show_all(db):
    cur = db.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    print()
    for user in users:
        print(user)
