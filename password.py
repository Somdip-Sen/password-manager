import random
import sqlite3
from tabulate import tabulate
from cryptography.fernet import Fernet
import os


def generate_key():
    key = Fernet.generate_key()  # Generates a key and save it into a file
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    return key


def load_key():
    if os.path.exists("secret.key") and os.access("secret.key", os.R_OK):
        return open("secret.key", "rb").read()  # Load the previously generated key
    else:
        return generate_key()  # create new key if not exists


def encrypt_message(message):  # Encrypts a message
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return encrypted_message


def decrypt_message(encrypted_message):  # Decrypts an encrypted message
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message.decode()


def initialize_key():
    pass


def create_password(num, char):
    letters = {"lower_": list(map(chr, range(97, 123))), "upper_": list(map(chr, range(65, 91))),
               "number_": list(map(str, list(range(0, 10))))}
    total_symbols = [*letters["lower_"], *letters["upper_"], *letters["number_"]]
    passwrd = []
    for i in random.sample(total_symbols, num):
        passwrd.append(i)

    # placing the symbols
    for _ in range(len(passwrd) // 3):
        passwrd[random.randint(0, len(passwrd) - 1)] = random.choice(char)

    passwrd_str = ""
    return passwrd_str.join(passwrd)


def connect_db():
    try:
        conn = sqlite3.connect("password.db")
    except sqlite3.Error:
        print("Error open db.")
        return False
    cur = conn.cursor()
    sql = """
    create table if not exists Password(
    service string,
    password string,
    date string
    )
    """
    cur.execute(sql)
    conn.commit()
    return cur, conn


def show_db(sub=""):
    cur, conn = connect_db()
    if sub:
        try:
            sql = f"select * from Password where service = '{sub}'"
        except Exception as e:
            print(e)
    else:
        sql = "select * from Password order by date desc"
    try:
        cur.execute(sql)
        results = cur.fetchall()
    except Exception as e:
        print(e)
        return []
    return results


def add_pass(sub, passwrd):
    cur, conn = connect_db()
    from datetime import datetime
    cur_date = str(datetime.now())
    sql = f"""
            insert into Password values (
    '{sub}',
    '{passwrd}',
    '{cur_date}'
    )
            """
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)
        return False

    return True


def take_input():
    chars = []
    confirm = False
    while not confirm:
        sub = input("For which Field: ")
        confirm = confirmation("Confirm")
    if show_db(sub):
        print("Password already exists....")
        return sub, 0, []
    spl_char = input("Enter the list of special characters with space: ").split()
    total_length = int(input("Enter the total number of character: "))
    for i in spl_char:
        chars.append(i)
    return sub, total_length, chars


def confirmation(types):
    while True:
        x = input(f"Do you want to {types} ? (y/n)  ").upper()
        if x == "Y":
            return True
        elif x == "N":
            return False
        else:
            print("Invalid Confirmation...")


def create():
    confirm = False
    while not confirm:
        sub, total_length, chars = take_input()
        if total_length == 0:
            return
        confirm = confirmation("proceed with these characters")

    change = True
    while change:
        passwrd = create_password(total_length, chars)
        print(f"\nNew password: {passwrd}\n")
        change = confirmation("change")  # want to change the password
    encrypted_password = encrypt_message(passwrd)
    print(f"\n\nThe final password for {sub} is {passwrd}")
    if add_pass(sub, encrypted_password.decode()):
        print("\n Password has been stored successfully")


def admin():  # admin access
    admin_pass = "admin"
    if (input("Enter the admin password: ")) == admin_pass:
        result = show_db()
        result_list = [list(elem) for elem in result]  # converting the list of tuple to list of list for future decode
        for i in range(len(result_list)):
            encoded_password = result_list[i][1].encode()
            password = decrypt_message(encoded_password)  # decoding and altering the hash codes
            result_list[i][1] = password
        print("\nFull Database: \n")
        print(tabulate(result_list, headers=["Field", "Password", "Time of Creation"]))


while True:
    f = input("Field : ")
    if f == "all":
        admin()
    else:
        s = show_db(f)
        if not s:
            if input("No recorded password exists.\nDo you want to create new ? (y/n) ").upper() == 'Y':
                create()
        else:
            encoded_password = s[0][1].encode()
            password = decrypt_message(encoded_password)
            print(f"\nPassword : {password} \nTime of creation: {s[0][2]}\n")
            


