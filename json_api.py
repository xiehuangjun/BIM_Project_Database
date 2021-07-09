import pymysql, json, configparser, os, datetime, time, shutil, base64
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS, cross_origin
from flask_api import status
from pathlib import Path
import pandas

app = Flask(__name__)
CORS(app)

tz_utc = datetime.timezone(datetime.timedelta(hours = int(time.timezone / -3600)))  # system timezone
tz_utc_0 = datetime.timezone(datetime.timedelta(hours = 0))  # system timezone
tz_utc_8 = datetime.timezone(datetime.timedelta(hours = 8))  # system timezone

path = os.path.abspath('.')
cfgpath = path.split('BIM_P_API')[0] + 'BIM_P_API/config.ini'

config = configparser.ConfigParser()
config.read(cfgpath)

mysql = pymysql.connect(host = '140.118.121.100', port = 3307, user = 'root', password = '12345678', db = 'TEST')
cur = mysql.cursor() 

# cur.execute('''CREATE DATABASE TEST;''')

cur.execute('''CREATE TABLE IF NOT EXISTS TEST.Project_Name (
                Project_id CHAR(100) PRIMARY KEY,
                Project_update_times CHAR(100),
                Project_getall_times CHAR(100))ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;''')
mysql.commit()

cur.execute('''CREATE TABLE IF NOT EXISTS TEST.Test_Information(
    Project_id VARCHAR(1000),
    Project_user_id VARCHAR(1000), 
    Object_id VARCHAR(1000),
    Element_id VARCHAR(1000), 
    Element_location TEXT,
    Element_parameters TEXT,
    Label_name VARCHAR(1000),
    Label VARCHAR(1000),
    Check_in_status VARCHAR(1000),
    Check_in_time VARCHAR(1000),
    Check_out_status VARCHAR(1000),
    Check_out_time VARCHAR(1000)
    )ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;''')

mysql.commit()
cur.close()

@app.route('/upload', methods = ['POST'])
@cross_origin()
def upload():

    mysql = pymysql.connect(host = '140.118.121.100', port = 3307, user = 'root', password = '12345678', db = 'TEST')
    cur = mysql.cursor() 

    data_json = {}
    data_out = []

    request_data = request.get_json()

    #j = json.dumps(request_data)
    # print(len(request_data))
    # i = 0

    Project_id = request_data['Project_id']
    # Element_location = ",".join(request_data['Element_location'])
    Project_user_id = request_data['Project_user_id']
    Object_id = request_data['Object_id']
    Element_location = ','.join(str(v) for v in request_data['Element_location'])
   
    
    Element_parameters = json.dumps(request_data['Element_parameters'])
    Label_name = ','.join(str(v) for v in request_data['Label_name'])
    Label = ','.join(str(v) for v in request_data['Label'])

    # print ( len(request_data['Element_location']))
    # print ( request_data['Element_location'][0])
    # Project_object_path = request_data[i]['Project_object_path']
    # print(Project_id)
    # print(Element_location)
    # print(type(Element_location))
    # print(Object_id)
    # print(Project_user_id)
    # print(Element_parameters)
    # print(Project_object_path)

    cur.execute('''SELECT * FROM TEST.Project_Name WHERE Project_id = '%s';''' %Project_id)
    data = cur.fetchall()

    if(len(data) == 0):
            INSERT = '''INSERT INTO TEST.Project_Name(Project_id,
                                                    Project_update_times
                                                    )VALUES(%s, %s);'''
            
            insert_data = (
                Project_id,
                '1'
            )
            cur.execute(INSERT,insert_data)
            mysql.commit()

            Element_id = Project_id + 'N' + '1'

    else:
        cur.execute('''UPDATE TEST.Project_Name SET Project_update_times = '%s' Where Project_id = '%s';''' %(int(data[0][1]) + 1, Project_id))
        Element_id = Project_id + 'N' + str(int(data[0][1]) + 1)

    # for x in range(len(request_data['Label_name'])):
        # print(request_data['Label_name'][x])
        # print(request_data['Label'][x])

    INSERT = '''INSERT INTO TEST.Test_Information(Project_id,
                                                Project_user_id,
                                                Object_id,
                                                Element_id,
                                                Element_location,
                                                Element_parameters,
                                                Label_name,
                                                Label,
                                                Check_in_status,
                                                Check_in_time,
                                                Check_out_status,
                                                Check_out_time
                                                )VALUES(%s, %s, %s, %s, %s, %s, 
                                                            %s,%s, %s, %s, %s, %s);'''

    d = datetime.datetime.now().astimezone(tz_utc_8).strftime
    Check_in_time = d('%Y') + '/' + d('%m') + '/' + d('%d')+'/' + d('%H') + ':' + d('%M') + ':' + d('%S') + '.' + d('%f')

    insert_data = (
        Project_id,
        Project_user_id,
        Object_id,
        Element_id,
        Element_location,
        Element_parameters,
        Label_name,
        Label,
        '1',
        Check_in_time,
        '0',
        ''
    )

    cur.execute(INSERT, insert_data)
    mysql.commit()

    # data_out.append(Project_Object_id)
    
    data_json['Element_id'] = Element_id

    return json.dumps(data_json), status.HTTP_200_OK

@app.route('/location', methods = ['POST'])
@cross_origin()
def location():
    mysql = pymysql.connect(host = '140.118.121.100', port = 3307, user = 'root', password = '12345678', db = 'TEST')
    cur = mysql.cursor() 

    data_json = {}
    data_text = []
    data_out = []

    request_data = request.get_json()

    Project_id = request_data['Project_id']
    Check_in_status = request_data['Check_in_status']

    cur.execute('''SELECT * FROM TEST.Test_Information WHERE Project_id = '%s';''' %Project_id)
    data = cur.fetchall()
    
    if(len(data) == 0):
        data_json['Log'] = "Project ID isn't existed !"
        data_out.append(data_json)
        return json.dumps(data_out), status.HTTP_400_BAD_REQUEST

    else:
        for raw in data:
            data_text.append(raw[3])
            # print(data_out[0])

        data_text = pandas.unique(data_text).tolist()

        for x in range(len(data_text)):
            # print(data_text[x])

            cur.execute('''SELECT * FROM TEST.Test_Information WHERE Element_id = '%s' limit 1;''' %data_text[x])
            data1 = cur.fetchall()
            # print(data1)
            
            data_json = {}
            # for raw1 in data1:
            data_json['Element_id'] = data1[0][3]
            # print(data1[0][3])
            data_json['Element_location'] = data1[0][4]
            # print(data1[0][4])

            # print (data_json)

            data_out.append(data_json)

            # print(data_out)

        return json.dumps(data_out), status.HTTP_200_OK 

@app.route('/file_store', methods = ['POST'])
@cross_origin()
def file_store():
    # mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    # cur = mysql.cursor()
    
    data_json = {}
    data_out = []

    request_data = request.get_json()
    
    Element_location_file = request_data["Element_location_file"]

    print(Element_location_file)

    os.getcwd()
    os.chdir('../')
    os.getcwd()

    print(os.listdir(os.curdir))
    file = Path(Element_location_file)

    print(file.exists())
    # print(file.stat())
    # Element_file = request.files[Element_location_file]

    # print(type(Element_location_file))

    # file_path = os.path.join('/home/garbagedog/Files', 'test_file', 'test')

    # if not os.path.isdir(file_path)ㄘㄣ
    #     os.makedirs(file_path)

    # Test_file_path = os.path.join(file_path, 'test.3dm')

    # file.save(Test_file_path)

    # mysql.close()

    data_out.append('ok')

    return json.dumps(data_out), status.HTTP_200_OK 

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5051,debug=True)