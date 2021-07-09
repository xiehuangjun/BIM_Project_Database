import pymysql, json, configparser, os, datetime

path = os.path.abspath('.')
cfgpath = path.split('BIM_P_API')[0] + 'BIM_P_API/config.ini'

config = configparser.ConfigParser()
config.read(cfgpath)


mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
cur = mysql.cursor()
#cur.execute('''CREATE DATABASE BIMP;''')

#cur.execute('''CREATE TABLE IF NOT EXISTS BIMP.Project_Name (
#                Project_id CHAR(100) NOT NULL PRIMARY KEY, 
#                Project_update_times CHAR(50) NOT NULL,
#                Project_getall_times CHAR(100))ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;''')
#mysql.commit()

cur.execute('''CREATE TABLE IF NOT EXISTS TEST.test(
    Project_id VARCHAR(100),
    Project_user_id VARCHAR(100),
    Object_id VARCHAR(100),
    Element_id VARCHAR(100),
    Element_location TEXT,
    Element_parameters TEXT,
    Label_name VARCHAR(100),
    Label VARCHAR(100)
    )ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;''')

mysql.commit()



cur.close()