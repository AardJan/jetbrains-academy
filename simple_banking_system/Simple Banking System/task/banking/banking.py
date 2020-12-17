# Write your code here
import random
import sys
import sqlite3

conn = sqlite3.connect('card.s3db')
curr = conn.cursor()
curr.execute(""" 
CREATE TABLE IF NOT EXISTS card (
id Integer,
number Text,
pin Text,
balance Integer Default 0)
""")
conn.commit()

ACCOUNT_LIST = []
LAST_ACCOUNT_NUMBER = 1
BANK_NUMBER = "400000"


class Account:
    def __init__(self, account_number, pin, balance=None):
        self.account_number = account_number
        self.pin = pin
        if balance is None:
            self.balance = 0
        else:
            self.balance = balance

    @classmethod
    def create_new_account(cls):
        return cls(create_account_number(), get_random_pin())

    def get_balance(self):
        print(self.balance)

    def add_income(self):
        print("Enter income:")
        answer = int(input())
        self.balance = self.balance + answer
        curr.execute("""
        UPDATE card
        SET balance = ?
        WHERE number = ?
        """, (self.balance, self.account_number))
        conn.commit()
        print("Income was added!")

    def delete_account(self):
        curr.execute("""
        DELETE FROM card
        WHERE number = ?
        """, (self.account_number,))
        conn.commit()

    def transfer(self):
        print("Transfer")
        print("Enter card number:")
        answer_card = input()
        if answer_card is self.account_number:
            print("You can't transfer money to the same account!")
        elif get_checksum(answer_card[:-1]) != answer_card[-1]:
            print("Probably you made a mistake in the card number. Please try again!")
        elif not check_account_exists(answer_card):
            print("Such a card does not exist.")
        else:
            print("Enter how much money you want to transfer:")
            answer_value = int(input())
            if answer_value > self.balance:
                print("Not enough money!")
            else:
                # Transfer
                self.balance = self.balance - answer_value
                curr.execute("""
                UPDATE card
                SET balance = ?
                WHERE number = ?
                """, (self.balance, self.account_number))
                curr.execute("""
                UPDATE card
                SET balance = balance + ?
                WHERE number = ?
                """, (answer_value, answer_card))
                conn.commit()
                print("Success!")


def get_checksum(num_without_checksum):
    num_list = [int(letter) for letter in num_without_checksum]
    num_odd_mul = [num * 2 if idx % 2 else num for idx, num in enumerate(num_list, start=1)]
    num_min_9 = [x - 9 if x > 9 else x for x in num_odd_mul]
    num_sum = sum(num_min_9)
    for x in range(0, 10):
        if (num_sum + x) % 10 == 0:
            return str(x)


def get_random_pin():
    pin = str(random.randint(0, 9999))
    if len(pin) < 4:
        pin = pin.zfill(4)
    return pin


def create_account_number():
    number = BANK_NUMBER
    global LAST_ACCOUNT_NUMBER
    account_internal_number = str(LAST_ACCOUNT_NUMBER).zfill(9)
    LAST_ACCOUNT_NUMBER = LAST_ACCOUNT_NUMBER + 1
    number = number + account_internal_number
    check_sum = get_checksum(number)
    number = number + check_sum
    return number


def account_count():
    curr.execute("""
    SELECT count(*) as account_count
    FROM  card
    """)
    return curr.fetchone()[0]


def select_account(account_number, pin):
    curr.execute("""
    SELECT id,
    number,
    pin,
    balance
    FROM card
    WHERE number = ?
    AND pin = ?
    """, (account_number, pin))
    return curr.fetchone()


def save_new_account(account):
    curr.execute("""
    INSERT INTO card(number, pin)
    VALUES (?, ?)
    """, (account.account_number, account.pin))
    conn.commit()


def check_account_exists(account_number):
    curr.execute("""
    SELECT 1
    FROM card
    WHERE number = ?""", (account_number,))
    if curr.fetchone() == None:
        return False
    else:
        return True


def create_account():
    new_account = Account.create_new_account()
    save_new_account(new_account)
    print("Your card number:")
    print(f"{new_account.account_number}")
    print("Your card PIN:")
    print(f"{new_account.pin}")


def log_in_account():
    print("Enter your card number:")
    account_account_number = input()
    print("Enter your PIN:")
    account_pin = input()

    if account_count() > 0:
        account_row = select_account(account_account_number, account_pin)
        if account_row is None:
            print("Wrong card number or PIN!")
        else:
            print("You have successfully logged in!")
            account = Account(account_row[1], account_row[2], account_row[3])
            while True:
                print("1. Balance")
                print("2. Add income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")

                answer = int(input())

                if answer == 1:
                    account.get_balance()
                elif answer == 2:
                    account.add_income()
                elif answer == 3:
                    account.transfer()
                elif answer == 4:
                    account.delete_account()
                    break
                elif answer == 5:
                    print("You have successfully logged out!")
                    break
                elif answer == 0:
                    print("Bye!")
                    sys.exit(0)
    else:
        print("Wrong card number or PIN!")


while True:
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")

    _input = int(input())

    if _input == 1:
        create_account()
    elif _input == 2:
        log_in_account()
    elif _input == 0:
        print("Bye!")
        sys.exit(0)
