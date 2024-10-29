import sqlite3
import re
from typing import List, Union


class Database:

    def __init__(self, db_name: str) -> None:
        self._con = sqlite3.connect(db_name)
        self._cur = self._con.cursor()
        self.create_table()

    def create_table(self) -> None:
        """
        Creates the required tables if they do not exist.
        """
        self._cur.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                         PESEL VARCHAR(11) PRIMARY KEY,
                         name TEXT NOT NULL,
                         surname TEXT NOT NULL,
                         mail TEXT NOT NULL   
                    )
                    ''')

        # self._cur.execute('''
        #             CREATE TABLE IF NOT EXISTS users_accounts (
        #                  user_PESEL VARCHAR(11),
        #                  account_id INTEGER NOT NULL,
        #                  PRIMARY KEY (user_PESEL, account_id),
        #                  FOREIGN KEY (user_pesel) REFERENCES users(PESEL),
        #                  FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        #             )
        #             ''')

        self._cur.execute('''
                    CREATE TABLE IF NOT EXISTS accounts (
                         account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                         money INTEGER NOT NULL,
                         PESEL VARCHAR(11),
                         FOREIGN KEY (PESEL) REFERENCES users (PESEL)
                    )
                    ''')

        self.commit()

    def commit(self) -> None:
        """
        Commits the current transaction to the database.
        """
        self._con.commit()

    def close(self) -> None:
        """
        Closes the connection to the database.
        """
        self._con.close()


class User:

    def __init__(self, db: Database) -> None:
        self.db = db

    def insert_user(self, name: str, surname: str,
                    mail: str, pesel: str) -> None:
        """
        Inserts a new user into the database.
        """
        self.pesel = pesel

        self.db.cur.execute('''
                    INSERT INTO users (PESEL, name, surname, mail)
                    VALUES (?, ?, ?, ?)
                    ''', (self.pesel, name.capitalize(),
                          surname.capitalize(), mail))

        self.db.commit()

    def insert_account(self, money: int, pesel: str) -> None:
        """
        Creates an account for the user with the specified initial balance.
        """
        self.pesel = pesel

        self.db.cur.execute('''
                    INSERT INTO accounts (money, PESEL)
                    VALUES (?, ?)
                    ''', (money, self.pesel))

        self.db.commit()

    def get_list_of_column(self) -> tuple:
        """
        Retrieves a list of all column names in the users and accounts tables.
        """
        self.column = self.db._con.execute('SELECT * FROM users, accounts')
        return tuple(map(lambda x: x[0], self.column.description))

    def get_user(self) -> List[tuple]:
        """
        Retrieves a list of all users in the database.
        """
        self.db.cur.execute('''
                            SELECT id, name, surname, mail, PESEL
                            FROM users
                            ''')

        return self.db.cur.fetchall()

    def get_records(self, arg) -> dict:
        """
        Retrieves all records for a user by PESEL.

        Returns:
            dict: A dictionary of user and account details for the specified PESEL.
            None: If no records are found for the PESEL.
        """

        self.db._cur.execute('''
                    SELECT users.PESEL, users.name,
                           users.surname, users.mail,
                           accounts.account_id, accounts.money
                    FROM users
                    JOIN accounts ON users.PESEL = accounts.PESEL
                    WHERE users.PESEL = ?
                ''', (str(arg),))

        if self.db._cur.fetchall():
            return {x: y for (x, y) in zip(self.get_list_of_column(),
                                           self.db._cur.fetchall()[0])}
        else:
            return None

    def deposit_money(self, pesel: int, money: int) -> None:
        """
        Deposits the specified amount of money to the user's account.
        """
        self.db.cur.execute('''
                    UPDATE accounts
                    SET money = money + ?
                    WHERE PESEL = ?
                    ''', (money, pesel)
        )
        self.db.commit()

    @property
    def pesel(self):
        """The pesel property."""
        return self._pesel

    @pesel.setter
    def pesel(self, value: Union[str, int]):

        if re.search("^\d{11}$", str(value)):
            self._pesel = value
        else:
            raise ValueError("ERROR: PESEL must consist 11 digits")
