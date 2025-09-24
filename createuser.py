import os
import json
import getpass

if getpass.getpass("Admin Password: ") == "Dealer":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, "users.json")

    finished = False
    while not finished:
        username = input("Username: ")

        with open(json_file_path, "r") as file:
            users = json.load(file)
            finished = True
            for user in users:
                if user["name"].lower() == username.lower():
                    finished = False
                    print("Username Already In Use")

    finished = False
    while not finished:
        password = getpass.getpass("Password: ")

        if len(password) > 0:
            finished = True
        else:
            print("Password Is Empty")

    finished = False
    while not finished:
        password2 = getpass.getpass("Confirm Password: ")

        if password == password2:
            finished = True
        else:
            print("Wrong Password Confirmation")

    with open(json_file_path, "r") as file:
        users = json.load(file)
        users.append({
            "name": username,
            "password": password,
            "money": 100
        })
        with open(json_file_path, "w") as f:
            f.write(json.dumps(users, indent=4))
        print("New User Created!")
else:
    print("Access Denied!")