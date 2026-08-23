"""
Helper script to create a new user or change a password.
Run from the command line: python create_user.py
Outputs a JSON block to paste into users.json.
"""

import bcrypt
import getpass
import json
import os

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")

def main():
    print("Photo Album - User Management")
    print("=" * 40)

    username = input("Enter username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return

    password = getpass.getpass("Enter password: ")
    if not password:
        print("Password cannot be empty.")
        return

    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.")
        return

    # Generate bcrypt hash
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Load existing users file or start fresh
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            data = {"users": []}
    else:
        data = {"users": []}

    # Check if username already exists
    existing = next((u for u in data["users"] if u["username"] == username), None)

    if existing:
        confirm_update = input(f"User '{username}' already exists. Update password? (y/n): ").strip().lower()
        if confirm_update != "y":
            print("Cancelled.")
            return
        existing["password"] = hashed
        print(f"Password updated for user '{username}'.")
    else:
        data["users"].append({"username": username, "password": hashed})
        print(f"User '{username}' created.")

    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Saved to {USERS_FILE}")

if __name__ == "__main__":
    main()