import cx_Oracle


def get_connection():
    server = '172.16.200.24'
    port = '1521'
    sid = 'PLAHF'
    user = 'DATA_SOURCE'
    password = 'DATA_SOURCE'
    dsn = cx_Oracle.makedsn(server, port, sid)
    conn = cx_Oracle.connect(user, password, dsn, encoding='gbk')
    return conn
