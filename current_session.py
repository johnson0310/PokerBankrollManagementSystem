import users
import singleton
import util
import payment
from users import user
import datetime
import time
import pymysql
from prettytable import PrettyTable

class session:
    def __init__(self):
        self.users = []
        self.user_ids = [1, 3, 5]
        self.date = datetime.date.today()
        self.starting_time = datetime.datetime.now()
        self.ending_time = None
        self.duration = None
        self.small_blind, self.big_blind = singleton.get_blinds()
        self.default_buy_in = singleton.get_default_buy_in()
        self.total_buy_in = 0
        self.total_payout = 0
        self.difference = 0

    def update_user_ids(self):
        for user in self.users:
            id = user.id
            if id not in self.user_ids:
                self.user_ids.append(id)
                print('\nAdded {} with id {} into the id list.'.format(user.nick_name, user.id))

    def add_user(self, db, user):
        try:
            # TODO
            #   1. Create session objects and operate without database
            # Added user into the users list to track the players in the current session
            # self.users.append(user)
            # self.update_user_ids()

            # Check if player is already in the current session
            cur = db.cursor()
            user_id = users.get_id_by_nick_name(db, user.nick_name)
            cur.execute('''SELECT player_id FROM current_session WHERE player_id = %s''', (user_id,))
            # Check if user id exists in current session
            row_count = cur.rowcount
            if row_count != 0:
                print('\nThis player is already playing you fool.')
                return

            # Query
            query = '''INSERT INTO current_session (player_id, session_buy_in, session_payout, entry_time) VALUES  (
            %s, %s, %s, %s) '''

            # Value
            buy_in = singleton.get_default_buy_in()
            payout = 0
            entry_time = datetime.datetime.now()
            value = (user_id, buy_in, payout, entry_time)

            # Execute
            cur.execute(query, value)

        except pymysql.Error as e:
            db.rollback()
            print('Failed to add {} to the current session.'.format(user.nick_name))
            print(e)

        # No error, commit changes
        db.commit()
        # Charge user the default buy in
        payment.buy_in(user)

        # Increase the total buy in by default buy in
        self.total_buy_in += singleton.get_default_buy_in()

        print('\nPlayer {} is buying in for ${} at {}, now the total buy in is at ${}.'.format(user.nick_name,
                                                                                               singleton.get_default_buy_in(),
                                                                                               entry_time,
                                                                                               self.total_buy_in))


# Prints current session status
def show_session_status(db):
    cur = db.cursor()
    cur.execute('''SELECT player_id from current_session''')

    # Check if user id exists in current session
    row_count = cur.rowcount
    if row_count == 0:
        print('\nThere are no players in the current session.')
        return

    cur.execute('''
                    SELECT u.id, u.nick_name, cs.session_buy_in, cs.session_payout
                    FROM users u
                    INNER JOIN current_session cs on u.id = cs.player_id
                    ''')
    current_players = cur.fetchall()

    t = PrettyTable(['ID', 'Name', 'Buy in', 'Pay out'])
    for player in current_players:
        t.add_row(list(player))

    print(t)
