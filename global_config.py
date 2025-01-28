db_config = {'Driver': '{SQL Server}',
            'Server':'34.151.220.250;',
            'Database':'testando1',
            'Trusted_Connection':'no;',
            'uid':'sqlserver;',
            'pwd':'proarc;'}

def get_db_config():
    return db_config

#VM: /opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.6.1
#Local: SQL Server