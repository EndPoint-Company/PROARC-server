import psycopg2

conn = psycopg2.connect(database = "proarc-1", 
                        user = "postgres", 
                        host= '34.95.242.42',
                        password = "proarc",
                        port = 5432)
cursor = conn.cursor()
cursor.execute("SELECT * FROM Procuradores")
print(cursor.fetchall())
