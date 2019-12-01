import pymysql
import init
import util
from pprint import pprint
from contextlib import closing
import datetime


class users:
    def __init__(self, id, first_name, last_name, nick_name, venmo_address, password, is_admin, register_date):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.nick_name = nick_name
        self.venmo_address = venmo_address
        self.password = password
        self.is_admin = is_admin
        self.register_date = register_date


# Create new users
# Nick name default is first name, if duplicated, then join first and last name
def users_add_new(db, value):
    # value format: First name, last name, venmo address, password

    try:
        cur = db.cursor()

        first_name, last_name, venmo_address, password = value

        # Check if name and address formatting are right
        if util.name_format_checking(first_name) or util.name_format_checking(
                last_name) or util.venmo_address_format_checking(venmo_address) or util.password_format_checking(
                password):
            return

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
        query = 'INSERT INTO users (first_name, last_name, nick_name, venmo_address, password, is_admin, ' \
                'register_date) ' \
                'VALUES (%s,%s,%s,%s,%s,%s,%s)'

        # Executing query
        cur.execute(query, value)
    except pymysql.Error as e:
        db.rollback()
        print("\nFailed to add new user")
        print(e)

    # No error, commit changes
    db.commit()
    print("\nCreated user '{}'.".format(value[2]))
    print(cur.rowcount, "record inserted.")


# Change nick name for a user
def users_change_nick_name(db, user_id, new_nick_name):
    # id: INT, name: String
    try:
        cur = db.cursor()

        # Find old nick name for corresponding user_id
        cur.execute("""SELECT nick_name FROM users WHERE id = %s""", (user_id,))

        # Check if user id is valid
        row_count = cur.rowcount
        if row_count == 0:
            print('\nUser ID does not exist, try again  you fool.')
            return

        # Check if name formatting is right
        if util.name_format_checking(new_nick_name):
            return

        # user id is valid
        old_nick_name = util.tuple_to_str(cur.fetchone())

        # Check if the old nick name is the same as the new nick name
        if old_nick_name == new_nick_name:
            print("\nYour new nick name has to be different from the old nick name you fool.")
            return

        # Executing query
        cur.execute("""UPDATE users SET nick_name = %s WHERE id = %s""", (new_nick_name, user_id))

    except pymysql.Error as e:
        db.rollback()
        print("\nFailed to change nick name.\n")
        print(e)

    # No error, commit changes
    db.commit()
    print('\nNick name for user ID: {} changed from "{}" to "{}"'.format(user_id, old_nick_name, new_nick_name))
    print(cur.rowcount, "record changed.")


# Change first name for a user
def users_change_first_name(db, user_id, new_first_name):
    # id: INT, name: String
    try:
        cur = db.cursor()

        # Find old first name for corresponding user_id
        cur.execute("""SELECT first_name FROM users WHERE id = %s""", (user_id,))

        # Check if user id is valid
        row_count = cur.rowcount
        if row_count == 0:
            print('\nUser ID does not exist, try again  you fool.')
            return

        # Check if name formatting is right
        if util.name_format_checking(new_first_name):
            return

        # user id is valid
        old_first_name = util.tuple_to_str(cur.fetchone())

        # Check if the old first name is the same as the new first name
        if old_first_name == new_first_name:
            print("\nYour new first name has to be different from the old first name you fool.")
            return

        # Executing query
        cur.execute("""UPDATE users SET first_name = %s WHERE id = %s""", (new_first_name, user_id))

    except pymysql.Error as e:
        db.rollback()
        print("\nFailed to change first name.\n")
        print(e)

    # No error, commit changes
    db.commit()
    print('\nFirst name for user ID: {} changed from "{}" to "{}"'.format(user_id, old_first_name, new_first_name))
    print(cur.rowcount, "record changed.")


# Change last name for a user
def users_change_last_name(db, user_id, new_last_name):
    # id: INT, name: String
    try:
        cur = db.cursor()

        # Find old last name for corresponding user_id
        cur.execute("""SELECT last_name FROM users WHERE id = %s""", (user_id,))

        # Check if user id is valid
        row_count = cur.rowcount
        if row_count == 0:
            print('\nUser ID does not exist, try again you fool.')
            return

        # Check if name formatting is right
        if util.name_format_checking(new_last_name):
            return

        # user id is valid
        old_last_name = util.tuple_to_str(cur.fetchone())

        # Check if the old last name is the same as the new last name
        if old_last_name == new_last_name:
            print("\nYour new last name has to be different from the old last name you fool.")
            return

        # Executing query
        cur.execute("""UPDATE users SET last_name = %s WHERE id = %s""", (new_last_name, user_id))

    except pymysql.Error as e:
        db.rollback()
        print("\nFailed to change last name.\n")
        print(e)

    # No error, commit changes
    db.commit()
    print('\nLast name for user ID: {} changed from "{}" to "{}"'.format(user_id, old_last_name, new_last_name))
    print(cur.rowcount, "record changed.")


# Change venmo address for a user
def users_change_venmo_address(db, user_id, new_venmo_address):
    # id: INT, name: String
    try:
        cur = db.cursor()

        # Find old venmo_address for corresponding user_id
        cur.execute("""SELECT venmo_address FROM users WHERE id = %s""", (user_id,))

        # Check if user id is valid
        row_count = cur.rowcount
        if row_count == 0:
            print('\nUser ID does not exist, try again you fool.')
            return

        # Check if venmo address format is right
        if util.venmo_address_format_checking(new_venmo_address):
            return

        # user id is valid
        old_venmo_address = util.tuple_to_str(cur.fetchone())

        # Check if the old venmo_address is the same as the venmo_address
        if old_venmo_address == new_venmo_address:
            print("\nYour new venmo address has to be different from the old venmo address you fool.")
            return

        # Executing query
        cur.execute("""UPDATE users SET venmo_address = %s WHERE id = %s""", (new_venmo_address, user_id))

    except pymysql.Error as e:
        db.rollback()
        print("\nFailed to change venmo address.\n")
        print(e)

    # No error, commit changes
    db.commit()
    print('\nVenmo address for user ID: {} changed from "{}" to "{}"'.format(user_id, old_venmo_address,
                                                                             new_venmo_address))
    print(cur.rowcount, "record changed.")


# Change password for a user
def users_change_password(db, user_id, new_password):
    # id: INT, name: String
    try:
        cur = db.cursor()

        # Find old password for corresponding user_id
        cur.execute("""SELECT password FROM users WHERE id = %s""", (user_id,))

        # Check if user id is valid
        row_count = cur.rowcount
        if row_count == 0:
            print('\nUser ID does not exist, try again you fool.')
            return

        # Check if name formatting is right
        if util.password_format_checking(new_password):
            return

        # user id is valid
        old_password = util.tuple_to_str(cur.fetchone())

        # Check if the old password is the same as the new password
        if old_password == new_password:
            print("\nYour new password has to be different from the old password you fool.")
            return

        # Executing query
        cur.execute("""UPDATE users SET password = %s WHERE id = %s""", (new_password, user_id))

    except pymysql.Error as e:
        db.rollback()
        print("\nFailed to change password.\n")
        print(e)

    # No error, commit changes
    db.commit()
    print('\nPassword for user ID: {} changed from "{}" to "{}"'.format(user_id, old_password, new_password))
    print(cur.rowcount, "record changed.")


# Show all existing users
def users_show_all(db):
    try:
        cur = db.cursor()
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()
        print()
        for user in users:
            print(user)
    except pymysql.Error as e:
        print('\nFailed to show all users')
        print(e)
