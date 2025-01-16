import hashlib

def get_hashed_password(plain_text_password, salt):
    plain_text_password += salt
    return hashlib.sha256(plain_text_password.encode("utf-8")).digest()

def check_password(plain_text_password, hashed_password):
    return get_hashed_password(plain_text_password) == hashed_password

def check_passworda(hashed_password):
    import pyodbc as odbc

    conn = odbc.connect('Driver={SQL Server};'
                            'Server=34.151.220.250;'
                            'Database=maconha2;'
                            'Trusted_Connection=no;'
                            'uid=sqlserver;'
                            'pwd=proarc;')
        
    cursor = conn.cursor()
    cursor.execute("SELECT hash_and_salt FROM UsuariosTeste1")
    a = cursor.fetchall()

    for hash_and_salt in a:
        if hash_and_salt[0] == hashed_password:
            return True

    return False

if __name__ == "__main__":
    # password = input("Enter a password: ")
    # hashed_password = get_hashed_password(password)
    # print(f"Hashed password: {hashed_password}")
    # print(f"Check password: {check_password(password, hashed_password)}")
    print(check_passworda(get_hashed_password("passworda", "proarc").hex("-").upper()))