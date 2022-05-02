import time
from tkinter import *
from pymongo import MongoClient
from cryptography.fernet import Fernet
import certifi


def add_nurse(name, password, client):
    try:
        client.hospital.command('createUser', name, pwd=password, roles=[{'role': 'read', 'db': 'hospital'}])
    except Exception as e:
        print(e)


def add_doctor(name, password, client):
    try:
        client.hospital.command('createUser', name, pwd=password, roles=[{'role': 'readWrite', 'db': 'hospital'}])
    except Exception as e:
        print(e)


def userAuth(MongoClient, username, password, db):
    CONNECTION_STRING = f"mongodb+srv://{username}:{password}@cluster0.xvcpg.mongodb.net/{db}"

    test_client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())

    db = test_client[db]

    try:
        db.list_collection_names()
        return True

    except Exception as e:
        print(e)
        return False


def login_page(main):
    loginFrame = Frame(main)

    loginFrame.grid(column=0, row=0, padx=120, pady=60)

    users = ['Nurse', 'Doctor', 'Patient']
    variable = StringVar()
    variable.set(users[0])

    OptionMenu(loginFrame, variable, *users).grid(column=1, row=0)

    Label(loginFrame, text="Username").grid(column=0, row=1)
    username = Entry(loginFrame)
    username.grid(column=1, row=1)

    Label(loginFrame, text="Password").grid(column=0, row=2)
    password = Entry(loginFrame, show="*")
    password.grid(column=1, row=2)


    def login():
        user = variable.get()

        if user == 'Patient':
            user = username.get()
            pas = password.get()

            CONNECTION_STRING = "mongodb+srv://rc60921997:rohi1997@cluster0.xvcpg.mongodb.net"
            client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
            hospital = client['hospital']
            db = hospital['patients']

            query = {'FIRST': user}

            for x in db.find(query):
                if x['LAST'] == pas:
                    patient_frame(main, client, True, x)
                else:
                    warning.set("Incorrect Patient Credentials")

        elif user == 'Nurse':
            if userAuth(MongoClient, username.get(), password.get(), 'hospital'):
                loginFrame.grid_forget()

                try:
                    CONNECTION_STRING = f"mongodb+srv://{username.get()}:{password.get()}@cluster0.xvcpg.mongodb.net/"
                    test_client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
                except:
                    warning.set("Error in login")

                main_frame(main, test_client, False)
            else:
                warning.set("Incorrect Nurse login details")
        elif user == 'Doctor':
            if userAuth(MongoClient, username.get(), password.get(), 'hospital'):
                loginFrame.grid_forget()

                try:
                    CONNECTION_STRING = f"mongodb+srv://{username.get()}:{password.get()}@cluster0.xvcpg.mongodb.net/"
                    test_client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
                except:
                    warning.set("Error in login")

                main_frame(main, test_client, True)
            else:
                warning.set("incorrect Doctor login details")

    Button(loginFrame, text="Login", command=login).grid(column=1, row=3)

    warning = StringVar()
    Label(loginFrame, textvariable=warning).grid(column=1, row=6)


def admin_page(main):
    CONNECTION_STRING = "mongodb+srv://rc60921997" \
                        ":rohi1997@cluster0.xvcpg.mongodb.net"
    client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())

    root = Frame(main)
    root.grid(column=0, row=0)

    list_doctors = Listbox(root)
    list_doctors.grid(column=0, row=0)
    list_nurses = Listbox(root)
    list_nurses.grid(column=0, row=4)

    all_users = client.hospital.command('usersInfo')['users']
    num = 1
    for i in all_users:
        if i['roles'][0]['role'] == 'readWrite':
            list_doctors.insert(num, i['user'])
        elif i['roles'][0]['role'] == 'read':
            list_nurses.insert(num, i['user'])

        num += 1

    Label(root, text="Doctor Name").grid(column=1, row=0)
    doctor_name = Entry(root)
    doctor_name.grid(column=2, row=0)

    Label(root, text="Password").grid(column=1, row=1)
    doctor_password = Entry(root)
    doctor_password.grid(column=2, row=1)

    def add_d():
        add_doctor(doctor_name.get(), doctor_password.get(), client)

        db = client['hospital']

        new_col = db['doctors']

        new_data = {
            'username': doctor_name.get(),
            'password': doctor_password.get()
        }

        new_col.insert_many(new_data)

        warning.set("added doctor")

    Button(root, text="Add Doctor", command=add_d).grid(column=2, row=2)

    Label(root, text="Nurse Name").grid(column=1, row=4)
    nurse_name = Entry(root)
    nurse_name.grid(column=2, row=4)

    Label(root, text="Password").grid(column=1, row=5)
    nurse_password = Entry(root)
    nurse_password.grid(column=2, row=5)

    def add_n():
        add_nurse(nurse_name.get(), nurse_password.get(), client)

        db = client['hospital']

        new_col = db['nurses']

        new_data = {
            'username': nurse_name.get(),
            'password': nurse_password.get()
        }

        new_col.insert_many(new_data)

        warning.set("added nurse")

    Button(root, text="Add Nurse", command=add_n).grid(column=2, row=6)

    def logout():
        root.grid_forget()

        login_page(main)

    Button(root, text="Logout", command=logout).grid(column=2, row=10)

    warning = StringVar()
    Label(root, textvariable=warning).grid(column=2, row=7)

    return root


def patients_frame(main, client, write, patient):
    root = Frame(main)
    root.grid(column=0, row=0)

    db = client['admin_details']
    admin_col = db['key']
    key = admin_col.find_one()['key_details']

    fernet = Fernet(key)

    for key, value in patient.items():
        try:
            if not write:
                if len(value) > 40:
                    patient[key] = "XXXXXXX"
            else:
                if len(value) > 40:
                    patient[key] = fernet.decrypt(value).decode()
        except:
            pass

    if patient['MARITAL'] == 'M':
        patient['MARITAL'] = 'Married'

    if patient['GENDER'] == 'M':
        patient['GENDER'] = 'Male'
    if patient['GENDER'] == 'F':
        patient['GENDER'] = 'Female'

    Label(root, text=f"Name: {patient['PREFIX']}  {patient['FIRST']} {patient['LAST']} {patient['SUFFIX']}").grid(
        column=0, row=0)
    Label(root, text=f"Gender: {patient['GENDER']} {patient['MARITAL']}").grid(column=0, row=1)
    Label(root, text=f"Ethnicity: {patient['ETHNICITY']} {patient['RACE']}").grid(column=0, row=2)
    Label(root, text=f"Passport: {patient['PASSPORT']}").grid(column=0, row=3)
    Label(root, text=f"Drivers Licence: {patient['DRIVERS']}").grid(column=0, row=3)
    Label(root, text=f"SSN: {patient['SSN']}").grid(column=0, row=4)
    Label(root, text=f"Birthdate: {patient['BIRTHDATE']} DeathDate: {patient['DEATHDATE']}").grid(column=0, row=5)
    Label(root, text=f"BirthPlace: {patient['BIRTHPLACE']}").grid(column=0, row=6)
    Label(root,
          text=f"Address: {patient['ADDRESS']} {patient['STATE']} {patient['CITY']} {patient['COUNTY']} {patient['ZIP']}").grid(
        column=0, row=7)

    Label(root, text="Allergies").grid(column=0, row=8)
    list_allergies = Listbox(root, width=40)
    list_allergies.grid(column=0, row=9)

    Label(root, text="Medications").grid(column=0, row=10)
    list_medications = Listbox(root, width=40)
    list_medications.grid(column=0, row=11)

    allergies = client['hospital']['allergies']
    medications = client['hospital']['medications']

    myquery = {"PATIENT": patient['Id']}

    all_allergies = allergies.find(myquery)
    all_medications = medications.find(myquery)

    num = 1
    allergies_list = []
    for x in all_allergies:
        allergies_list.append(x)
        if x['STOP'] == '':
            x['STOP'] = "Allergy Active"
        allergy = f"{x['DESCRIPTION']} from:{x['START']} to:{x['STOP']}"
        list_allergies.insert(num, allergy)
        num += 1

    num = 1
    medications_list = []
    for x in all_medications:
        medications_list.append(x)
        medication = f"{x['DESCRIPTION']}"
        list_medications.insert(num, medication)
        num += 1

    def view_patients():
        root.grid_forget()
        main_frame(main, client, write)

    def logout():
        root.grid_forget()
        login_page(main)

    if write:
        def delete_allergy():
            try:
                index = list_allergies.curselection()
                query = {'PATIENT': allergies_list[index[0]]['PATIENT'],
                         'DESCRIPTION': allergies_list[index[0]]['DESCRIPTION']}
                allergies.delete_one(query)

                warning.set("deleted allergy")
            except:
                pass

        Button(root, text="Delete Allergy", command=delete_allergy).grid(column=3, row=9)

        def delete_medication():
            try:
                index = list_medications.curselection()
                query = {'PATIENT': medications_list[index[0]]['PATIENT'],
                         'DESCRIPTION': medications_list[index[0]]['DESCRIPTION']}
                medications.delete_one(query)

                warning.set("deleted medication")
            except:
                pass

        Button(root, text="Delete Medication", command=delete_medication).grid(column=3, row=11)

    Button(root, text="Go to Patients", command=view_patients).grid(column=3, row=0)
    Button(root, text="Logout", command=logout).grid(column=3, row=1)

    warning = StringVar()
    Label(root, textvariable=warning).grid(column=0, row=12)

    return root


def patient_frame(main, client, write, patient):
    root = Frame(main)
    root.grid(column=0, row=0)

    db = client['admin_details']
    admin_col = db['key']
    key = admin_col.find_one()['key_details']

    fernet = Fernet(key)

    for key, value in patient.items():
        try:
            if not write:
                if len(value) > 40:
                    patient[key] = "XXXXXXX"
            else:
                if len(value) > 40:
                    patient[key] = fernet.decrypt(value).decode()
        except:
            pass

    if patient['MARITAL'] == 'M':
        patient['MARITAL'] = 'Married'

    if patient['GENDER'] == 'M':
        patient['GENDER'] = 'Male'
    if patient['GENDER'] == 'F':
        patient['GENDER'] = 'Female'

    Label(root, text=f"Name: {patient['PREFIX']}  {patient['FIRST']} {patient['LAST']} {patient['SUFFIX']}").grid(
        column=0, row=0)
    Label(root, text=f"Gender: {patient['GENDER']} {patient['MARITAL']}").grid(column=0, row=1)
    Label(root, text=f"Ethnicity: {patient['ETHNICITY']} {patient['RACE']}").grid(column=0, row=2)
    Label(root, text=f"Passport: {patient['PASSPORT']}").grid(column=0, row=3)
    Label(root, text=f"Drivers Licence: {patient['DRIVERS']}").grid(column=0, row=3)
    Label(root, text=f"SSN: {patient['SSN']}").grid(column=0, row=4)
    Label(root, text=f"Birthdate: {patient['BIRTHDATE']} DeathDate: {patient['DEATHDATE']}").grid(column=0, row=5)
    Label(root, text=f"BirthPlace: {patient['BIRTHPLACE']}").grid(column=0, row=6)
    Label(root,
          text=f"Address: {patient['ADDRESS']} {patient['STATE']} {patient['CITY']} {patient['COUNTY']} {patient['ZIP']}").grid(
        column=0, row=7)

    Label(root, text="Allergies").grid(column=0, row=8)
    list_allergies = Listbox(root, width=40)
    list_allergies.grid(column=0, row=9)

    Label(root, text="Medications").grid(column=0, row=10)
    list_medications = Listbox(root, width=40)
    list_medications.grid(column=0, row=11)

    allergies = client['hospital']['allergies']
    medications = client['hospital']['medications']

    myquery = {"PATIENT": patient['Id']}

    all_allergies = allergies.find(myquery)
    all_medications = medications.find(myquery)

    num = 1
    allergies_list = []
    for x in all_allergies:
        allergies_list.append(x)
        if x['STOP'] == '':
            x['STOP'] = "Allergy Active"
        allergy = f"{x['DESCRIPTION']} from:{x['START']} to:{x['STOP']}"
        list_allergies.insert(num, allergy)
        num += 1

    num = 1
    medications_list = []
    for x in all_medications:
        medications_list.append(x)
        medication = f"{x['DESCRIPTION']}"
        list_medications.insert(num, medication)
        num += 1

    def logout():
        root.grid_forget()
        login_page(main)

    Button(root, text="Logout", command=logout).grid(column=3, row=1)

    warning = StringVar()
    Label(root, textvariable=warning).grid(column=0, row=12)

    return root

def main_frame(main, client, write):
    root = Frame(main)
    root.grid(column=0, row=0)

    database = client['hospital']
    nurses = database['patients']

    Label(root, text="Patients").grid(column=0, row=0)
    list_patients = Listbox(root, width=40, height=30)
    list_patients.grid(column=0, row=1, padx=20)

    allpatients = []

    num = 1
    for i in nurses.find():
        stringName = i['PREFIX'] + " " + i['FIRST'] + " " + i['LAST'] + " " + i['SUFFIX']
        list_patients.insert(num, stringName)
        allpatients.append(i)
        num += 1

    def viewPatients():
        index = list_patients.curselection()
        if len(index) > 0:
            root.grid_forget()
            patients_frame(main, client, write, allpatients[index[0]])

    def logout():
        root.grid_forget()
        login_page(main)

    Button(root, text="View Details", command=viewPatients).grid(column=0, row=2)
    Button(root, text="Logout", command=logout).grid(column=1, row=2)

    return root



