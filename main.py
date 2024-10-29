import os
import msvcrt
from sql import Database, User


def menu():
    os.system('cls')  # clear terminal
    print("--- THE BANK ---")
    print('1. Add user to bank\n'
          '2. Deposit money to the user\n'
          '3. Chceck balance at account\n'
          '4. Exit')
    return input('>> ')


def create_user() -> tuple:

    # Define fields with data type and validation
    fields = {
        "name": {"type": str, "validation": lambda x: len(x) > 0},
        "surname": {"type": str, "validation": lambda x: len(x) > 0},
        "mail": {"type": str, "validation": lambda x: "@" in x},
        "pesel": {"type": int, "validation": lambda x: len(str(x)) == 11},
        "money": {"type": int, "validation": lambda x: x >= 0}
    }

    user_data = []

    for field, rules in fields.items():
        data_type = rules["type"]
        validation = rules["validation"]
        while True:
            try:
                # Download value from user and append to the list
                value = data_type(input(f"Enter {field}: "))
                if validation(value):
                    user_data.append(value)
                    break
            except ValueError:
                print(
                    f"Please enter a valid {field}"
                    f" (expected {data_type.__name__}).")

    return tuple(user_data)


def add_user_to_bank(name: str, surname: str, mail: str,
                     pesel: int, money: int, db: Database) -> None:
    user = User(db)
    user.insert_user(name, surname, mail, pesel)
    user.insert_account(money, pesel)


def check_account_exists(pesel: int, db: Database) -> bool:

    usr = User(db)
    if usr.get_records(pesel):
        return True
    else:
        return False


def get_pesel() -> int:
    while True:
        pesel = input('PESEL: ')
        if pesel.isdigit() and len(pesel) == 11:
            return int(pesel)
        else:
            print('PESEL must consist of 11 digits.')


def press_enter() -> None:
    print('Press ENTER key to continue...')
    msvcrt.getche()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))  # main catalog
    file_path = os.path.join(script_dir, 'clients.db')
    db = Database(file_path)

    while True:

        try:
            choose = menu()
        except ValueError as e:
            print(f"Error: {e}")
            continue

        if 0 < int(choose) < 5:
            if choose == '1':
                print('--- ADD USER ---')
                tuple_of_user = create_user()
                add_user_to_bank(*tuple_of_user, db)
            elif choose == '2':
                validate = {'money': {"validation": lambda x: x > 0}}

                print('--- DEPOSIT MONEY ---')

                pesel = get_pesel()
                add_money = validate['money']['validation'](
                    int(input('add money:')))

                u = User.deposit_money(pesel, add_money)
                print('Complete!')
                press_enter()

            elif choose == '3':

                print('---BALANCE---')
                usr = User(db)

                pesel = get_pesel()
                if check_account_exists(pesel, db):
                    data = usr.get_records(pesel)
                    print(f"Name: {data['name']} | Surname: {data['surname']}"
                          f"\n\nBalance: {data['money']}")
                else:
                    print("This user doesn't exists in Database")

                press_enter()
            elif choose == '4':
                exit()
            else:
                print('Wrong option, please select again')
                press_enter()
