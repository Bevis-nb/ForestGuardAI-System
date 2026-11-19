import csv

def get_user_data():
    USERS = {}
    with open('utils/user_data.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            USERS[row[0]] = row[1]
    return USERS

def update_user_data(user_id, user_name):
    with open('utils/user_data.csv', 'a',newline="") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, user_name])
