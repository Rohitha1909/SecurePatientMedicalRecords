import csv
import tkinter
import certifi

from tkinter import *
from all_frames import *



def check_for_db(test_client, db_name):
    dblist = test_client.list_database_names()
    print(dblist)
    if db_name in dblist:
        return True
    else:
        return False


def add_nurse(name, password, client):
    try:
        client.hospital.command('createUser', name, pwd=password, roles=[{'role': 'read', 'db': 'hospital'}])
    except:
        pass


def add_doctor(name, password, client):
    try:
        client.hospital.command('createUser', name, pwd=password, roles=[{'role': 'readWrite', 'db': 'hospital'}])
    except:
        pass


def checkPatients(client):
    mydb = client['hospital']
    collist = mydb.list_collection_names()
    if "patients" in collist:
        return True


def checkAllergies(client):
    mydb = client['hospital']
    collist = mydb.list_collection_names()
    if "allergies" in collist:
        return True


def checkMedications(client):
    mydb = client['hospital']
    collist = mydb.list_collection_names()

    if "medications" in collist:
        return True


def checkDoctors(client):
    mydb = client['hospital']
    collist = mydb.list_collection_names()

    if "doctors" in collist:
        return True


def checkNurses(client):
    mydb = client['hospital']
    collist = mydb.list_collection_names()

    if "nurses" in collist:
        return True


def addUsers(client):

    db = client['hospital']
    mycoll = db['nurses']

    for i in mycoll.find():
        add_nurse(i['username'], i['password'], client)

    mycoll2 = db['doctors']

    for i in mycoll2.find():
        add_doctor(i['username'], i['password'], client)


def userAuth(MongoClient, username, password, db):
    CONNECTION_STRING = f"mongodb+srv://{username}:{password}@cluster0.xvcpg.mongodb.net/{db}?retryWrites=true&w=majority"
    test_client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())

    db = test_client[db]

    try:
        db.command("serverStatus")
        return True
    except:
        return False


def main():
    from pymongo import MongoClient
    CONNECTION_STRING = f"mongodb+srv://rc60921997:rohi1997@cluster0.xvcpg.mongodb.net"
    client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())

    add_data(client)
    addUsers(client)

    top = tkinter.Tk()
    top.geometry("900x600")
    top.title("Hospital")

    login_page(top)

    top.mainloop()


def add_data(client):
    from cryptography.fernet import Fernet

    if not checkPatients(client):
        client['admin_details']['key'].drop()

        key = Fernet.generate_key()
        db = client['admin_details']
        admin_col = db['key']

        data = {
            'key_details': key
        }

        admin_col.insert_one(data)

        """ else:
            db = client['admin_details']
            admin_col = db['key']
            key = admin_col.find_one()['key_details']"""

        fernet = Fernet(key)

        with open('./data/patients.csv', 'r') as f:
            db = client['hospital']

            new_col = db['patients']

            csv_reader = csv.reader(f, delimiter=',')

            column_names = []

            for line in csv_reader:
                column_names = line
                break
            next(f)

            all_data = []

            for line in csv_reader:
                new_line = line

                new_dict = {}

                for i in range(len(column_names)):
                    if column_names[i] == "SSN":
                        new_ssn = fernet.encrypt(new_line[i].encode())
                        new_dict[column_names[i]] = new_ssn
                    elif column_names[i] == "DRIVERS":
                        new_data = fernet.encrypt(new_line[i].encode())
                        new_dict[column_names[i]] = new_data
                    elif column_names[i] == "PASSPORT":
                        new_data = fernet.encrypt(new_line[i].encode())
                        new_dict[column_names[i]] = new_data
                    elif column_names[i] == "ADDRESS":
                        new_data = fernet.encrypt(new_line[i].encode())
                        new_dict[column_names[i]] = new_data
                    else:
                        new_dict[column_names[i]] = new_line[i]

                # print(fernet.decrypt(new_dict["SSN"]).decode())

                all_data.append(new_dict)

            new_col.insert_many(all_data)

    if not checkAllergies(client):
        with open('./data/allergies.csv', 'r') as f:
            db = client['hospital']

            new_col = db['allergies']

            csv_reader = csv.reader(f, delimiter=',')

            column_names = []

            for line in csv_reader:
                column_names = line
                break
            next(f)

            all_data = []

            for line in csv_reader:
                new_line = line

                new_dict = {}

                for i in range(len(column_names)):
                    new_dict[column_names[i]] = new_line[i]

                all_data.append(new_dict)

            new_col.insert_many(all_data)

    if not checkMedications(client):
        with open('./data/medications.csv', 'r') as f:
            db = client['hospital']

            new_col = db['medications']

            csv_reader = csv.reader(f, delimiter=',')

            column_names = []

            for line in csv_reader:
                column_names = line
                break
            next(f)

            all_data = []

            for line in csv_reader:
                new_line = line

                new_dict = {}

                for i in range(len(column_names)):
                    new_dict[column_names[i]] = new_line[i]

                all_data.append(new_dict)

            new_col.insert_many(all_data)

    if not checkDoctors(client):
        db = client['hospital']

        new_col = db['doctors']

        all_data = [{
            'username': 'user2',
            'password': 'pass',
            'key': ''
        }]

        new_col.insert_many(all_data)

    if not checkNurses(client):
        db = client['hospital']

        new_col = db['nurses']

        all_data = [{
            'username': 'user2',
            'password': 'pass'
        }]

        new_col.insert_many(all_data)


if __name__ == '__main__':
    main()

