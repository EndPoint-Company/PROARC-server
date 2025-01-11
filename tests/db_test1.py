import pyodbc as odbc

def main():
    conn = odbc.connect('Driver={SQL Server};'
                        'Server=34.151.220.250;'
                        'Database=maconha2;'
                        'Trusted_Connection=no;'
                        'uid=sqlserver;'
                        'pwd=proarc;')
    cursor = conn.cursor()
    a = cursor.execute("SELECT * FROM maconha2.dbo.TESTE")
    a = cursor.fetchall()
    for resultado in a:
        print(resultado)
    cursor.commit()

if __name__ == '__main__':
    main()