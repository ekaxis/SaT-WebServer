import logging
import mysql
from mysql.connector import (connection)
from mysql.connector import errorcode


"""classe para operações com banco de dados MySQL
"""
class ConnMySQL:
    """ this class abstracts basic functions and
    operations from the mysql database and implements those. """

    config: dict = None
    cnx = None  # mysql.connector.connection.MySQLConnection
    verbose: bool = None  # Mode debugging, show info for develop

    def __init__(self, user: str, password: str, host: str, database: str, port: int=3306, verbose=True):

        # information required for connection
        self.config = {
            'user': user, 'password': password, 'host': host, 'database': database, 'port': int(port),
            'raise_on_warnings': True, 'ssl_disabled': True  # debugging mode
        }

        try:
            cnx = mysql.connector.connect(**self.config)
        except mysql.connector.errors.InterfaceError as err:
            logging.critical('cant connect to MySQL server on "%s": detail %s' % (self.config['host'], err))
        except mysql.connector.Error as err:
            # ER_ACCESS_DENIED_ERROR    1045
            # ER_BAD_DB_ERROR           1049
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.critical('access denied error "%s":"%s"' %
                                 (self.config['user'], self.config['password']))
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.critical('database does not exist')
            else:
                logging.critical('instance class err: %s' % err)
        else:
            self.cnx = cnx

    def working(self)-> bool:
        return self.cnx is not None

    def select(self, query: str)-> list or None:
        # if communication with mysql has not been
        # 	established is returned None
        if not self.working(): return None
        cursor = self.cnx.cursor()

        try:
            cursor.execute(query)
        except mysql.connector.Error as err:
            # generic treatment for consultation failure
            logging.warning('unknown error in select "%s"' % (err))
        finally:
            try:
                # if an exception occurred above
                response = cursor.fetchall()
            except mysql.connector.Error as err:
                response = None
            cursor.close()
        # returns None if there are no records or
        # 	an error has occurred
        return response

    def insert(self, params: dict)-> bool:
        # if communication with mysql has not been
        # 	established is returned false
        if not self.working(): return False

        table = 'alerts'
        select_query = "select * from alerts where text_alert = '%s'" % (params['text_alert'])
        resp = self.select(select_query)
        if len(resp) > 0: return False
        query = f"insert into {table} (`host`, `timestamp_alert`, `to_ip`, `from_ip`, `protocol`, `msg`, `sid`, `rev`, " \
                f"`priority`, `classification`, `alert_priority`, `text_alert`) VALUES (%(host)s, %(timestamp_alert)s, " \
                f"%(to_ip)s, %(from_ip)s, %(protocol)s, %(msg)s, %(sid)s, %(rev)s, %(priority)s, %(classification)s, " \
                f"%(alert_priority)s, %(text_alert)s) "
        cursor = self.cnx.cursor()
        cursor.execute(query, params)
        self.cnx.commit()  # required for changes
        cursor.close()
        return True


if __name__ == '__main__':
    import sys

    if len(sys.argv) >= 5:
        attrs = {
            'host': '127.0.0.1',
            'timestamp_alert': '04/20-18:24:37.484048',
            'to_ip': '255.255.255.255:67',
            'from_ip': '0.0.0.0:68',
            'protocol': 'UDP',
            'msg': 'BAD-TRAFFIC same SRC/DST',
            'sid': '527',
            'rev': '1',
            'priority': 0,
            'classification': '7',
            'alert_priority': 3,
            'text_alert': '05/28/2020-10:59:21.409681  [**] [1:2221010:1] SURICATA HTTP unable to match response to request [**] [Classification: Generic Protocol Command Decode] [Priority: 3] {TCP} 172.16.41.32:19999 -> 45.234.102.102:50336'
        }
        con = ConnMySQL(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[5], sys.argv[4])
        print(con.insert(attrs))
    else:
        print('usage: ' + sys.argv[0] + ' user_db pass_db host port database')
