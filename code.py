import pyodbc

#connect = pyodbc.connect('DRIVER={SQL Server};SERVER=MYSERVER;DATABASE=Healthcare;Trusted_Connection=yes')
#cursor = connect.cursor()

def customer():
    c = input('[1]Login\n[2]Register\n[3]Back\n')
    if c == '1':
        #login
        uid = input('Username: ')
        pwd = input('Password: ')
        try:
            cconnect = pyodbc.connect(f"Driver={{SQL Server}};Server=MYSERVER;Database=Healthcare;UID={uid};PWD={pwd};")
            print("Login successful")
            ccursor = cconnect.cursor()
            #customer module
            while True:
                appointment = input("[1]Make appointment\n[2]Remove appointment\n[3]Log out\n")
                if appointment == '1':
                    doc = input('Please select your doctor: ')
                    time = input('Please select your time (HH:MM, 24 hours format): ')
                    #temporary access to window login
                    connect = pyodbc.connect('DRIVER={SQL Server};SERVER=MYSERVER;DATABASE=Healthcare;Trusted_Connection=yes')
                    cursor = connect.cursor()
                    cursor.execute("OPEN SYMMETRIC KEY NameKey DECRYPTION BY CERTIFICATE NameCert;")
                    cursor.execute("""
                        SELECT 1
                        FROM Doctor
                        WHERE DecryptByKey(Name) = EncryptByKey(Key_GUID('NameKey'), ?)
                    """, (doc,))
                    if not cursor.fetchone():
                        print("Doctor does not exist. Please choose a valid doctor.")
                    else:
                        cursor.execute(f"SELECT 1 FROM Appointments WHERE CONVERT(varchar(100), DecryptByKey(DoctorName)) = ? AND ABS(DATEDIFF(MINUTE, AppointmentTime, ?)) < 30", (doctor, time))
                        if cursor.fetchone():
                            print("The appointment is taken by someone else. Please choose another session.")
                        else:
                            cursor.execute(f"SELECT Name FROM Patient WHERE CONVERT(VARCHAR(100), DecryptByKey(ID)) = ?", (uid,))
                            line = cursor.fetchone()
                            one = line[2]
                            if one == 1:
                                print("You have an existing appointment")
                            else:
                                patient = line[0]
                                cursor.execute(f"""
                                    INSERT INTO Appointments (PatientName, DoctorName, AppointmentTime)
                                    VALUES (
                                        ?,
                                        ?,
                                        ?
                                        )
                                    """, (patient, doc, time))
                                cursor.execute("UPDATE Patient SET Status = 1 WHERE CONVERT(int, DecryptByKey(ID)) = ?", (uid,))

                                print("Appointment successful.")
                                conn.commit()
                                cursor.execute("CLOSE SYMMETRIC KEY NameKey;")
                                connect.close()
                        #close access from window
                elif appointment == '2':
                    confirm = input('Are you sure you want to remove your appointment?(y/n)')
                    if confirm == 'y':
                        connect = pyodbc.connect('DRIVER={SQL Server};SERVER=MYSERVER;DATABASE=Healthcare;Trusted_Connection=yes')
                        cursor = connect.cursor()
                        cursor.execute("SELECT Status FROM Patient WHERE CONVERT(VARCHAR, DecryptByKey(ID)) = ?", (uid,))
                        get = cursor.fetchone()
                        if get[0] == 1:
                            cursor.execute("DELETE FROM Appointments WHERE DecryptByKey(ID) = ?", (uid,))
                            cursor.execute("SELECT CONVERT(varchar, DecryptByKey(Name)) FROM Patient WHERE ID = ?", (uid,))
                            pname = cursor.fetchone()
                            patient = pname[0]
                            cursor.execute("UPDATE Patient SET Status = 0 WHERE DecryptByKey(PatientName) = ?", (patient,))
                    elif confirm == 'n':
                        customer()
                    else:
                        print('You have no appointment')
                        customer()
                elif appointment == '3':
                    cconnect.commit()
                    cconnect.close()
                    break
                else:
                    print('Please choose a valid option.')
        except pyodbc.Error as e:
            print("Error: ", e)
            customer()
        
        
    elif c =='2':
        #register
        ruid = input('Create Username: ')
        rpwd = input('Create Password: ')
        name = input('Your name: ')
        try:
            connect = pyodbc.connect('DRIVER={SQL Server};SERVER=MYSERVER;DATABASE=Healthcare;Trusted_Connection=yes')
            cursor = connect.cursor()
            cursor.execute(f"CREATE LOGIN [{ruid}] WITH PASSWORD = '{rpwd}', CHECK_POLICY = OFF;")
            cursor.execute(f"CREATE USER [{ruid}] FOR LOGIN [{ruid}];")
            cursor.execute(f"EXEC sp_addrolemember 'Customer', '{ruid}';")
            cursor.execute(f"INSERT INTO dbo.Patient (Name, ID, Status) VALUES (?, ?, 0)", (name, ruid))
            cursor.execute(f"OPEN SYMMETRIC KEY NameKey DECRYPTION BY CERTIFICATE NameCert;")
            cursor.execute("""
                UPDATE dbo.Patient
                SET [Name] = ENCRYPTBYKEY(Key_GUID('NameKey'), ?)
                WHERE [ID] = ?;
            """, (name, ruid))
            cursor.execute("CLOSE SYMMETRIC KEY NameKey;")
            connect.commit()
            connect.close()
            print("Registration successful.")

        except pyodbc.Error as e:
            print("Error during registration:", e)
        customer()
        
    else:
        start()

def doctor():
    d = input('[1]Login\n[2]Back') #register as doctor at admin to prevent anyone can be doctor
    if d == '1':
        #login
        uid = input('Username: ')
        pwd = input('Password: ')
        try:
            dconnect = pyodbc.connect(f"Driver={{SQL Server}};Server=MYSERVER;Database=Healthcare;UID={uid};PWD={pwd};")
            print("Login successful")
            dcursor = dconnect.cursor()
            #doctor module
            while True:
                service = input('[1]Add appointment\n[2]Remove appointment\n[3]View appointments\n[4]Log out')
                if service == '1':
                    doc = input('Please select your doctor: ')
                    time = input('Please select your time (HH:MM, 24 hours format): ')
                    #temporary access to window login
                    connect = pyodbc.connect('DRIVER={SQL Server};SERVER=MYSERVER;DATABASE=Healthcare;Trusted_Connection=yes')
                    cursor = connect.cursor()
                    cursor.execute("SELECT 1 FROM Doctor WHERE DoctorName = ?", (doctor,))
                    if not cursor.fetchone():
                        print("Doctor does not exist. Please choose a valid doctor.")
                    else:
                        cursor.execute("OPEN SYMMETRIC KEY NameKey DECRYPTION BY CERTIFICATE NameCert;")
                        cursor.execute("SELECT 1 FROM Appointments WHERE CONVERT(varchar, DecryptByKey(DoctorName)) = ? AND ABS(DATEDIFF(MINUTE, AppointmentTime, ?)) < 30", (doctor, time))
                        if cursor.fetchone():
                            print("The appointment is taken by someone else. Please choose another session.")
                        else:
                            cursor.execute("SELECT Name FROM Patient WHERE CONVERT(VARCHAR, DecryptByKey(ID)) = ?", (uid,))
                            line = cursor.fetchone()
                            one = line[2]
                            if one == 1:
                                print("You have an existing appointment")
                            else:
                                pname = cursor.fetchone()
                                patient = pname[0]
                                cursor.execute("""
                                    INSERT INTO Appointments (PatientName, DoctorName, AppointmentTime)
                                    VALUES (
                                        ?,
                                        ?,
                                        ?
                                        )
                                    """, (patient, doctor, time))
                                cursor.execute("UPDATE Patient SET Status = 1 WHERE DecryptByKey(ID) = ?", (uid,))

                                print("Appointment successful.")
                                conn.commit()
                                cursor.execute("CLOSE SYMMETRIC KEY NameKey;")
                                connect.close()
                        #close access from window
                elif service == '2':
                    rem = input("Please choose the time you want to remove appointment (HH:MM)")
                    try:
                        dcursor.execute("DELETE FROM Appointments WHERE AppointmentTime={rem}")
                    except pyodbc.Error as e:
                        print("Failed to delete\nError: ", e)
                elif service == '3':
                    connect = pyodbc.connect('DRIVER={SQL Server};SERVER=MYSERVER;DATABASE=Healthcare;Trusted_Connection=yes')
                    cursor = connect.cursor()
                    cursor.execute("""
                        SELECT 
                            CONVERT(varchar, DecryptByKey(PatientName)) AS DecryptedPatientName,
                            CONVERT(varchar, DecryptByKey(DoctorName)) AS DecryptedDoctorName,
                            AppointmentTime
                        FROM Appointments
                    """)
                    rows = cursor.fetchall()
                    for row in rows:
                        print(f" Patient: {row.DecryptedPatientName}, Doctor: {row.DecryptedDoctorName}, AppointmentTime: {row.AppointmentTime}")

                elif service == '4':
                    dconnect.commit()
                    dconnect.close()
                    break
                else:
                    print("Please choose a valid option.")
        except pyodbc.Error as e:
            print("Error: ", e)
            doctor()
    else:
        start()

def admin():
    a = input('[1]Login\n[2]Back')
    if a == '1':
        #login
        uid = input('Username: ')
        pwd = input('Password: ')
        try:
            aconnect = pyodbc.connect(f"Driver={{SQL Server}};Server=MYSERVER;Database=Healthcare;UID={uid};PWD={pwd};")
            print("Login successful")
            acursor = aconnect.cursor()
            #admin module
            while True:
                control = input('[1]Add doctor\n[2]Remove doctor/customer\n[3]View appointments details\n[4]Master key management\n[5]Log out')
                if control == '1':
                    ruid = input('Create Username: ')
                    rpwd = input('Create Password: ')
                    name = input("Doctor's name: ")
                    try:
                        acursor.execute(f"CREATE LOGIN [{ruid}] WITH PASSWORD = '{rpwd}', CHECK_POLICY = OFF;")
                        acursor.execute(f"CREATE USER [{ruid}] FOR LOGIN [{ruid}];")
                        acursor.execute("EXEC sp_addrolemember 'Doctor', ?;", (ruid,))
                        acursor.execute(f"INSERT INTO dbo.Doctor ([Name], [ID]) VALUES (?, ?)", (name, ruid))
                        acursor.execute(f"OPEN SYMMETRIC KEY NameKey DECRYPTION BY CERTIFICATE NameCert;")
                        acursor.execute("""
                            UPDATE dbo.Doctor
                            SET [Name] = ENCRYPTBYKEY(Key_GUID('NameKey'), ?)
                            WHERE [ID] = ?;
                        """, (name, ruid))
                        acursor.execute("CLOSE SYMMETRIC KEY NameKey;")
                        aconnect.commit()
                        aconnect.close()
                        print("Doctor registration successful.")

                    except pyodbc.Error as e:
                        print("Error during registration:", e)
                    admin()
                elif control == "2":
                    print("\n[1] Remove Doctor\n[2] Remove Patient\nPress any key to go back")
                    choice = input("Select removal type: ")
                    
                    if choice == '1':
                        try:
                            acursor.execute("OPEN SYMMETRIC KEY NameKey DECRYPTION BY CERTIFICATE NameCert;")

                            doc_id = input("Enter Doctor ID to remove: ")
                            
                            acursor.execute("SELECT Name FROM Doctor WHERE CONVERT(varchar, DecryptByKey(ID) = ?;",doc_id)
                            n = acursor.fetchone()
                            doc_name = n[0]
                            acursor.execute("DELETE FROM Appointments WHERE DoctorName = ?", doc_name)
                            
                            acursor.execute("DELETE FROM Doctor WHERE CONVERT(varchar, DecryptByKey(ID)) = ?",(doc_id,))
                            
                            acursor.execute(f"DROP USER [{doc_id}];")
                            acursor.execute(f"DROP LOGIN [{doc_id}];")
                            aconnect.commit()
                            print("Doctor removed successfully.")
                            acursor.execute("CLOSE SYMMETRIC KEY NameKey;")
                        except pyodbc.Error as e:
                            print("Error: ", e)
                    elif choice == '2':
                        try:
                            acursor.execute("OPEN SYMMETRIC KEY NameKey DECRYPTION BY CERTIFICATE NameCert;")

                            patient_id = input("Enter Patient ID to remove: ")
                            
                            acursor.execute("SELECT CONVERT(varchar, DecryptByKey(Name)) AS patientname FROM Patient WHERE CONVERT(varchar, DecryptByKey(ID)) = ?;",patient_id)
                            n = acursor.fetchone()
                            acursor.execute("DELETE FROM Appointments WHERE CONVERT(varchar, DecryptByKey(PatientName)) = ?", (n[0],))
                            # Delete patient
                            acursor.execute("DELETE FROM Patient WHERE CONVERT(varchar, DecryptByKey(ID)) = ?", (patient_id,))
                            # Drop login/user
                            acursor.execute(f"DROP USER [{patient_id}];")
                            acursor.execute(f"DROP LOGIN [{patient_id}];")
                            aconnect.commit()
                            print("Patient removed successfully.")
                            acursor.execute("CLOSE SYMMETRIC KEY NameKey;")
                        except pyodbc.Error as e:
                            print("Error: ", e)
                    else:
                        continue

                elif control == '3':
                    acursor.execute("""
                        SELECT 
                            CONVERT(varchar, DecryptByKey(PatientName)) AS DecryptedPatientName,
                            CONVERT(varchar, DecryptByKey(DoctorName)) AS DecryptedDoctorName,
                            AppointmentTime
                        FROM Appointments
                    """)
                    rows = acursor.fetchall()
                    for row in rows:
                        print(f"Patient: {row.DecryptedPatientName}, Doctor: {row.DecryptedDoctorName}, Time: {row.AppointmentTime}")

                elif control == '4':
                    master = input('Please enter the master key: ')
                    try:
                        acursor.execute("OPEN MASTER KEY DECRYPTION BY PASSWORD = '{master}';")
                        close = input("[1]Close master key\n[2]Back")
                        if close == '1':
                            acursor.execute("CLOSE MASTER KEY;")
                        else:
                            continue
                    except pyodbc.Error as e:
                        print("Invalid key: ", e)
                elif control == '5':
                    aconnect.commit()
                    aconnect.close()
                    break
        except pyodbc.Error as e:
            print("Error: ", e)
            admin()
    else:
        start()

def out():
    connect = pyodbc.connect('DRIVER={SQL Server};SERVER=MYSERVER;DATABASE=Healthcare;Trusted_Connection=yes')
    cursor = connect.cursor()
    cursor.execute(f"OPEN SYMMETRIC KEY NameKey DECRYPTION BY CERTIFICATE NameCert;")
    cursor.execute("""
        UPDATE dbo.Patient
        SET [Name] = ENCRYPTBYKEY(Key_GUID('NameKey'), ?)
        WHERE [ID] = ?;
    """, (name, ruid))
    acursor.execute("""
        UPDATE dbo.Doctor
        SET [Name] = ENCRYPTBYKEY(Key_GUID('NameKey'), ?)
        WHERE [ID] = ?;
     """, (name, ruid))
    cursor.execute("CLOSE SYMMETRIC KEY NameKey;")
    connect.commit()
    connect.close()
     
    
    
def start():
    while True:
        user = int(input('[1]Customer\n[2]Doctor\n[3]Admin\n[4]Exit\n'))
        if user == 1:
            customer()
        elif user == 2:
            doctor()
        elif user == 3:
            admin()
        elif user == 4:
            print("Exiting program.")
            break
        else:
            print('Please select a valid user')
start()



