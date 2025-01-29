db_config_windows = {'Driver': '{SQL Server}',
            'Server':'34.151.220.250;',
            'Database':'testando1',
            'Trusted_Connection':'no;',
            'uid':'sqlserver;',
            'pwd':'proarc;'}

db_config_linux = {'Driver': '{/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.6.1}',
            'Server':'34.151.220.250;',
            'Database':'testando1',
            'Trusted_Connection':'no;',
            'uid':'sqlserver;',
            'pwd':'proarc;'}

def get_db_config():
    from sys import platform

    if platform == "win32":
        return db_config_windows
    else:
        return db_config_linux

#VM: /opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.6.1
#Local: SQL Server