import pymysql, json, configparser, os, datetime

path = os.path.abspath('.')
cfgpath = path.split('BIM_P_API')[0] + 'BIM_P_API/config.ini'

config = configparser.ConfigParser()
config.read(cfgpath)


mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
cur = mysql.cursor()
cur.execute('''CREATE DATABASE BIMP;''')

cur.execute('''CREATE TABLE IF NOT EXISTS BIMP.Project_Name (
                Project_id CHAR(100) NOT NULL PRIMARY KEY, 
                Project_update_times CHAR(50) NOT NULL,
                Project_getall_times CHAR(100))ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;''')
mysql.commit()

cur.execute('''CREATE TABLE IF NOT EXISTS BIMP.Project_Information(
    Project_id VARCHAR(100),
    Project_user_id VARCHAR(100),
    Object_id VARCHAR(100),
    Element_id VARCHAR(100),
    Element_location TEXT,
    Element_parameters TEXT,
    Label_name VARCHAR(100),
    Label VARCHAR(100),
    Check_in_status VARCHAR(50),
    Check_in_time VARCHAR(1000),
    Check_out_status VARCHAR(50),
    Check_out_time VARCHAR(1000),
    Project_check_in_bc_start_time VARCHAR(1000),
    Project_check_in_bc_end_time VARCHAR(1000),
    Project_check_in_bc_time VARCHAR(1000),
    Project_check_out_bc_start_time VARCHAR(1000),
    Project_check_out_bc_end_time VARCHAR(1000),
    Project_check_out_bc_time VARCHAR(1000),
    Project_id_co_time VARCHAR(1000),
    Project_id_ch_time VARCHAR(1000),
    Project_id_so_time VARCHAR(1000),
    Project_id_to_time VARCHAR(1000),
    Project_source_ip VARCHAR(500),
    Project_check_in_element_hashcode VARCHAR(150),
    Project_check_in_db_time VARCHAR(1000),
    Project_check_out_element_hashcode VARCHAR(150),
    Project_check_out_db_time VARCHAR(1000),
    Project_check_out_user_id VARCHAR(100),
    Project_element_path VARCHAR(1000),
    Project_element_size VARCHAR(1000),
    Project_element_time VARCHAR(1000)
    )ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;''')

mysql.commit()



cur.close()




