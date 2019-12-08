import singleton
import users
import venmo

current_bank = singleton.get_bank_id()


# Charge user default buy in amount
def buy_in(db, user_id):
    # If the added user is the bank, then stop
    if user_id == singleton.get_bank_id():
        print("\nDon't you charge the bank himself you fool.")
        return

    # User is not bank
    cur = db.cursor()
    cur.execute('''SELECT venmo_address FROM users WHERE id=%s''', (user_id,))

    # Check if user id exists
    row_count = cur.rowcount
    if row_count == 0:
        print("\nThis player doesn't exist.")
        return

    user_venmo = cur.fetchone()[0]

    try:
        print('\nCharged without auth')
        # venmo.payment.charge(user_venmo, singleton.get_default_buy_in(), 'Congratulations, you are one step closer to '
        #                                                                  'becoming a degenerate.')
    except KeyError as e:
        # If catches a key error, re-auth and charge again
        print('\nCurrent access token expired')
        # venmo.auth.configure()
        print('Charged with auth')
        # venmo.payment.charge(user_venmo, singleton.get_default_buy_in(), 'Congratulations, you are one step closer to '
        #                                                                  'becoming a degenerate.')


# Pay user venmo by user_id reference
def pay_out(db, user_id, final_amount):
    # If the pay out user is the bank, then stop
    if user_id == singleton.get_bank_id():
        bank_name = users.get_nick_name_by_id(db, user_id)
        print('"{}" will not be paid since he is the bank.'.format(bank_name))
        return

    # User is not bank
    cur = db.cursor()
    cur.execute('''SELECT nick_name, venmo_address FROM users WHERE id = %s''', (user_id,))
    nick_name, user_venmo = cur.fetchone()

    try:
        print('\nPaid without auth')
        print('\nPaid "{}" ${}.'.format(nick_name, final_amount))
        # venmo.payment.charge(user_venmo, final_amount, "Thanks for your kind donation to Zhang's foundation!")
        print('\n' + '*' * 60)
    except KeyError as e:
        # If catches a key error, re-auth and charge again
        print('\nCurrent access token expired')
        # venmo.auth.configure()
        print('\nPaid with auth')
        print('\nPaid "{}" ${}.'.format(nick_name, final_amount))
        # venmo.payment.charge(user_venmo, final_amount, "Thanks for your kind donation to Zhang's foundation!")
