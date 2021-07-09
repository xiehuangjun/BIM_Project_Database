import pymysql, json, configparser, os, datetime, time, shutil, base64
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS, cross_origin
from flask_api import status
from subfunction import getSize
from Ethereum_Transaction import Transaction, Verification
import hashlib
import datetime

path = os.path.abspath('.')
cfgpath = path.split('BIM_P_API')[0] + 'BIM_P_API/config.ini'

config = configparser.ConfigParser()
config.read(cfgpath)

tz_utc = datetime.timezone(datetime.timedelta(hours = int(time.timezone / -3600)))  # system timezone
tz_utc_0 = datetime.timezone(datetime.timedelta(hours = 0))  # system timezone
tz_utc_8 = datetime.timezone(datetime.timedelta(hours = 8))  # system timezone
# datetime.datetime.now().astimezone(tz_utc).isoformat()

app = Flask(__name__)

@app.route('/upload', methods = ['POST'])
@cross_origin()
def upload():
    mysql = pymysql.connect(user = config['MYSQL']['user'], password = config['MYSQL']['password'], port = int(config['MYSQL']['port']), host = config['MYSQL']['host'])
    cur = mysql.cursor()
    data_json = {}
    data_out = []

    request_data = request.get_json()

    Project_id = request_data['Project_id']
    Element_location = ','.join(str(v) for v in request_data['Element_location'])
    Object_id = request_data['Object_id']
    Project_user_id = request_data['Project_user_id']
    Element_parameters = json.dumps(request_data['Element_parameters'])
    Label_name = ','.join(str(v) for v in request_data['Label_name'])
    Label = ','.join(str(v) for v in request_data['Label'])
    Check_in_status = '1'
    Check_out_status = ''
    Check_out_time = ''
    Project_check_out_bc_start_time = ''
    Project_check_out_bc_end_time = ''
    Project_check_out_bc_time = ''
    Project_id_co_time = '0'
    Project_id_ch_time = '0'
    Project_id_so_time = '0'
    Project_id_to_time = '0'
    Project_source_ip = ''
    Project_db_time = ''
    Project_check_out_element_hashcode = ''
    Project_check_out_db_time = ''
    Project_check_out_user_id = ''
    Project_element_path = ''
    Project_element_size = ''
    Project_element_time = ''

    cur.execute('''SELECT * FROM BIMP.Project_Name WHERE Project_id = '%s';''' %Project_id)
    data = cur.fetchall()
    
    if(len(data) == 0):
        INSERT = '''INSERT INTO BIMP.Project_Name(Project_id,
                                                    Project_update_times
                                                    )VALUES(%s, %s);'''

        insert_data = (
            Project_id,
            '1'
        )

        cur.execute(INSERT,insert_data)
        mysql.commit()

        Element_id = Project_id + 'N' + '1'
        Project_update_times = '1'

    else:
        cur.execute('''UPDATE BIMP.Project_Name SET Project_update_times = '%s' WHERE Project_id = '%s';''' %(int(data[0][1]) + 1, Project_id))
        Element_id = Project_id + 'N' + str(int(data[0][1]) + 1)
        Project_update_times = str(int(data[0][1]))

    d = datetime.datetime.now().astimezone(tz_utc_8).strftime
    Project_bc_start_time = d('%Y') + '/' + d('%m') + '/' + d('%d')+'/' + d('%H') + ':' + d('%M') + ':' + d('%S') + '.' + d('%f')
    bc_start_time = time.time()
    eth_data = {}
    #eth_data["Project_update_times"] = Project_update_times
    eth_data["Project_id"] = Project_id
    eth_data["Project_user_id"] = Project_user_id
    eth_data["Object_id"] = Object_id
    eth_data["Element_id"] = Element_id
    eth_data["Element_location"] = Element_location
    eth_data["Element_parameters"] = Element_parameters
    eth_data["Label_name"] = Label_name
    eth_data["Label"] = Label
    #eth_data["Project_element_path"] = Project_element_path
    #eth_data["Project_element_size"] = Project_element_size
    Project_element_hashcode = Transaction(eth_data, config['ETHEREUM']['user'])
    bc_end_time = time.time()
    Project_bc_end_time = d('%Y') + '/' + d('%m') + '/' + d('%d')+'/' + d('%H') + ':' + d('%M') + ':' + d('%S') + '.' + d('%f')
    Project_bc_time = bc_end_time - bc_start_time

    INSERT = '''INSERT INTO BIMP.Project_Information(Project_id,
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
                                                    Check_out_time,
                                                    Project_check_in_bc_start_time,
                                                    Project_check_in_bc_end_time,
                                                    Project_check_in_bc_time,
                                                    Project_check_out_bc_start_time,
                                                    Project_check_out_bc_end_time,
                                                    Project_check_out_bc_time,
                                                    Project_id_co_time,
                                                    Project_id_ch_time,
                                                    Project_id_so_time,
                                                    Project_id_to_time,
                                                    Project_source_ip,
                                                    Project_check_in_element_hashcode,
                                                    Project_check_in_db_time,
                                                    Project_check_out_element_hashcode,
                                                    Project_check_out_db_time,
                                                    Project_check_out_user_id,
                                                    Project_element_path,
                                                    Project_element_size,
                                                    Project_element_time
                                                    )VALUES(%s, %s, %s, %s, %s, %s, 
                                                            %s, %s, %s, %s, %s, %s, 
                                                            %s, %s, %s, %s, %s, %s, 
                                                            %s, %s, %s, %s, %s, %s, 
                                                            %s, %s, %s, %s, %s, %s, %s);'''

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
        Check_in_status,
        str(Check_in_time),
        Check_out_status,
        str(Check_out_time),
        Project_bc_start_time,
        Project_bc_end_time,
        str(Project_bc_time),
        str(Project_check_out_bc_start_time), 
        str(Project_check_out_bc_end_time),
        str(Project_check_out_bc_time),
        Project_id_co_time,
        Project_id_ch_time,
        Project_id_so_time,
        Project_id_to_time,
        Project_source_ip,
        Project_element_hashcode,
        str(Project_db_time),
        str(Project_check_out_element_hashcode),
        str(Project_check_out_db_time),
        Project_check_out_user_id,
        Project_element_path,
        Project_element_size,
        str(Project_element_time)
        )

    db_time_start= time.time()
    cur.execute(INSERT, insert_data)
    mysql.commit()
    db_time_stop = time.time()

    Project_db_time = db_time_stop - db_time_start 
    cur.execute('''UPDATE BIMP.Project_Information SET Project_check_in_db_time = '%s' WHERE Project_id = '%s';''' %(Project_db_time, Project_id))
    mysql.commit()
    data_json['Element_id'] = Element_id
    mysql.close()

    return json.dumps(data_json), status.HTTP_200_OK

@app.route('/location', methods = ['POST'])
@cross_origin()
def location():
    mysql = pymysql.connect(user = config['MYSQL']['user'], password = config['MYSQL']['password'], port = int(config['MYSQL']['port']), host = config['MYSQL']['host'])
    cur = mysql.cursor() 

    data_json = {}
    data_text_name = []
    data_text_value = []
    data_out = []

    request_data = request.get_json()

    Project_id = request_data['Project_id']
    Object_id = request_data['Object_id']
    Element_id = request_data['Element_id']
    Label = request_data['Label']
    Check_in_status = request_data['Check_in_status']
    Check_in_time = request_data['Check_in_time']
    Check_out_status = request_data['Check_out_status']
    Check_out_time = request_data['Check_out_time']

    if(Project_id != ""):
        data_text_name.append('Project_id')
        data_text_value.append(Project_id)
    else:
        pass
    if(Object_id != ""):
        data_text_name.append('Object_id')
        data_text_value.append(Object_id)
    else:
        pass
    if(Element_id != ""):
        data_text_name.append('Element_id')
        data_text_value.append(Element_id)
    else:
        pass
    if(Label != ""):
        data_text_name.append('Label')
        data_text_value.append(Label)
    else:
        pass    
    if(Check_in_status != ""):
        data_text_name.append('Check_in_status')
        data_text_value.append(Check_in_status)
    else:
        pass
    if(Check_in_time != ""):
        data_text_name.append('Check_in_time')
        data_text_value.append(Check_in_time)
    else:
        pass
    if(Check_out_status != ""):
        data_text_name.append('Check_out_status')
        data_text_value.append(Check_out_status)
    else:
        pass
    if(Check_out_time != ""):
        data_text_name.append('Check_out_time')
        data_text_value.append(Check_out_time)
    else:
        pass

    if(len(data_text_name) == 0):
        data_json['Log'] = "Please Input parameters !"
        data_out.append(data_json)
        return json.dumps(data_out), status.HTTP_400_BAD_REQUEST
    
    elif(len(data_text_name) == 1):
        cur.execute('''SELECT * FROM BIMP.Project_Information WHERE %s LIKE '%s';''' %(data_text_name[0], '%'+data_text_value[0]+'%'))
        data = cur.fetchall()

        for raw in data:
            data_json = {}
            data_json['Project_id'] = raw[0]
            data_json['Object_id'] = raw[2]
            data_json['Element_id'] = raw[3]
            data_json['Element_location'] = raw[4]
            data_json['Label'] = raw[7]
            data_json['Check_in_status'] = raw[8]
            data_json['Check_in_time'] = raw[9]
            data_json['Check_out_status'] = raw[10]
            data_json['Check_out_time'] = raw[11]

            data_out.append(data_json)
        
        return json.dumps(data_out), status.HTTP_200_OK
    
    elif(len(data_text_name) == 2):
        cur.execute('''SELECT * FROM BIMP.Project_Information WHERE (%s LIKE '%s') AND (%s LIKE '%s');'''
            %(data_text_name[0], '%'+data_text_value[0]+'%', data_text_name[1], '%'+data_text_value[1]+'%'))
        data = cur.fetchall()

        for raw in data:
            data_json = {}
            data_json['Project_id'] = raw[0]
            data_json['Object_id'] = raw[2]
            data_json['Element_id'] = raw[3]
            data_json['Element_location'] = raw[4]
            data_json['Label'] = raw[7]
            data_json['Check_in_status'] = raw[8]
            data_json['Check_in_time'] = raw[9]
            data_json['Check_out_status'] = raw[10]
            data_json['Check_out_time'] = raw[11]
            
            data_out.append(data_json)
        
        return json.dumps(data_out), status.HTTP_200_OK

    elif(len(data_text_name) == 3):
        cur.execute('''SELECT * FROM BIMP.Project_Information WHERE (%s LIKE '%s') AND (%s LIKE '%s') 
            AND (%s LIKE '%s');'''%(data_text_name[0], '%'+data_text_value[0]+'%', data_text_name[1], 
            '%'+data_text_value[1]+'%', data_text_name[2], '%'+data_text_value[2]+'%'))
        data = cur.fetchall()

        for raw in data:
            data_json = {}
            data_json['Project_id'] = raw[0]
            data_json['Object_id'] = raw[2]
            data_json['Element_id'] = raw[3]
            data_json['Element_location'] = raw[4]
            data_json['Label'] = raw[7]
            data_json['Check_in_status'] = raw[8]
            data_json['Check_in_time'] = raw[9]
            data_json['Check_out_status'] = raw[10]
            data_json['Check_out_time'] = raw[11]
            
            data_out.append(data_json)
        
        return json.dumps(data_out), status.HTTP_200_OK

    elif(len(data_text_name) == 4):
        cur.execute('''SELECT * FROM BIMP.Project_Information WHERE (%s LIKE '%s') AND (%s LIKE '%s') 
            AND (%s LIKE '%s') AND (%s LIKE '%s');'''%(data_text_name[0], '%'+data_text_value[0]+'%', 
            data_text_name[1], '%'+data_text_value[1]+'%', data_text_name[2], '%'+data_text_value[2]+'%', 
            data_text_name[3], '%'+data_text_value[3]+'%'))
        data = cur.fetchall()

        for raw in data:
            data_json = {}
            data_json['Project_id'] = raw[0]
            data_json['Object_id'] = raw[2]
            data_json['Element_id'] = raw[3]
            data_json['Element_location'] = raw[4]
            data_json['Label'] = raw[7]
            data_json['Check_in_status'] = raw[8]
            data_json['Check_in_time'] = raw[9]
            data_json['Check_out_status'] = raw[10]
            data_json['Check_out_time'] = raw[11]
            
            data_out.append(data_json)
        
        return json.dumps(data_out), status.HTTP_200_OK
    
    elif(len(data_text_name) == 5):
        cur.execute('''SELECT * FROM BIMP.Project_Information WHERE (%s LIKE '%s') AND (%s LIKE '%s') 
            AND (%s LIKE '%s') AND (%s LIKE '%s') AND (%s LIKE '%s');'''
            %(data_text_name[0], '%'+data_text_value[0]+'%', data_text_name[1], '%'+data_text_value[1]+'%', 
            data_text_name[2], '%'+data_text_value[2]+'%', data_text_name[3], '%'+data_text_value[3]+'%',
            data_text_name[4], '%'+data_text_value[4]+'%'))
        data = cur.fetchall()

        for raw in data:
            data_json = {}
            data_json['Project_id'] = raw[0]
            data_json['Object_id'] = raw[2]
            data_json['Element_id'] = raw[3]
            data_json['Element_location'] = raw[4]
            data_json['Label'] = raw[7]
            data_json['Check_in_status'] = raw[8]
            data_json['Check_in_time'] = raw[9]
            data_json['Check_out_status'] = raw[10]
            data_json['Check_out_time'] = raw[11]
            
            data_out.append(data_json)
        
        return json.dumps(data_out), status.HTTP_200_OK
    
    elif(len(data_text_name) == 6):
        cur.execute('''SELECT * FROM BIMP.Project_Information WHERE (%s LIKE '%s') AND (%s LIKE '%s') 
            AND (%s LIKE '%s') AND (%s LIKE '%s') AND (%s LIKE '%s') AND (%s LIKE '%s');'''
            %(data_text_name[0], '%'+data_text_value[0]+'%', data_text_name[1], '%'+data_text_value[1]+'%', 
            data_text_name[2], '%'+data_text_value[2]+'%', data_text_name[3], '%'+data_text_value[3]+'%',
            data_text_name[4], '%'+data_text_value[4]+'%', data_text_name[5], '%'+data_text_value[5]+'%'))
        data = cur.fetchall()

        for raw in data:
            data_json = {}
            data_json['Project_id'] = raw[0]
            data_json['Object_id'] = raw[2]
            data_json['Element_id'] = raw[3]
            data_json['Element_location'] = raw[4]
            data_json['Label'] = raw[7]
            data_json['Check_in_status'] = raw[8]
            data_json['Check_in_time'] = raw[9]
            data_json['Check_out_status'] = raw[10]
            data_json['Check_out_time'] = raw[11]
            
            data_out.append(data_json)
        
        return json.dumps(data_out), status.HTTP_200_OK

    elif(len(data_text_name) == 7):
        cur.execute('''SELECT * FROM BIMP.Project_Information WHERE (%s LIKE '%s') AND (%s LIKE '%s') 
            AND (%s LIKE '%s') AND (%s LIKE '%s') AND (%s LIKE '%s') AND (%s LIKE '%s') AND (%s LIKE '%s');'''
            %(data_text_name[0], '%'+data_text_value[0]+'%', data_text_name[1], '%'+data_text_value[1]+'%', 
            data_text_name[2], '%'+data_text_value[2]+'%', data_text_name[3], '%'+data_text_value[3]+'%',
            data_text_name[4], '%'+data_text_value[4]+'%', data_text_name[5], '%'+data_text_value[5]+'%',
            data_text_name[6], '%'+data_text_value[6]+'%'))
        data = cur.fetchall()

        for raw in data:
            data_json = {}
            data_json['Project_id'] = raw[0]
            data_json['Object_id'] = raw[2]
            data_json['Element_id'] = raw[3]
            data_json['Element_location'] = raw[4]
            data_json['Label'] = raw[7]
            data_json['Check_in_status'] = raw[8]
            data_json['Check_in_time'] = raw[9]
            data_json['Check_out_status'] = raw[10]
            data_json['Check_out_time'] = raw[11]
            
            data_out.append(data_json)
        
        return json.dumps(data_out), status.HTTP_200_OK   

    elif(len(data_text_name) == 8):
        cur.execute('''SELECT * FROM BIMP.Project_Information WHERE (%s LIKE '%s') AND (%s LIKE '%s') 
            AND (%s LIKE '%s') AND (%s LIKE '%s') AND (%s LIKE '%s') AND (%s LIKE '%s') AND (%s LIKE '%s') 
            AND (%s LIKE '%s');'''
            %(data_text_name[0], '%'+data_text_value[0]+'%', data_text_name[1], '%'+data_text_value[1]+'%', 
            data_text_name[2], '%'+data_text_value[2]+'%', data_text_name[3], '%'+data_text_value[3]+'%',
            data_text_name[4], '%'+data_text_value[4]+'%', data_text_name[5], '%'+data_text_value[5]+'%',
            data_text_name[6], '%'+data_text_value[6]+'%', data_text_name[7], '%'+data_text_value[7]+'%'))
        data = cur.fetchall()

        for raw in data:
            data_json = {}
            data_json['Project_id'] = raw[0]
            data_json['Object_id'] = raw[2]
            data_json['Element_id'] = raw[3]
            data_json['Element_location'] = raw[4]
            data_json['Label'] = raw[7]
            data_json['Check_in_status'] = raw[8]
            data_json['Check_in_time'] = raw[9]
            data_json['Check_out_status'] = raw[10]
            data_json['Check_out_time'] = raw[11]
            
            data_out.append(data_json)
        
        return json.dumps(data_out), status.HTTP_200_OK 

@app.route('/upload_file', methods = ['POST'])
@cross_origin()
def upload_file():
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()
    
    data_json = {}
    data_out = []

    Element_id = request.form.get('Element_id')
    Check_element_id = cur.execute("SELECT * FROM BIMP.Project_Information WHERE Element_id = '%s'"%(Element_id))
    if Check_element_id == 0:
        return jsonify({"error" : "Element_id not exist"})
    
    if (not request.files['Element_location_file']):
        return jsonify({"error" : "request file", "code" : "file_01"}), status.HTTP_400_BAD_REQUEST

    File = request.files['Element_location_file']
    File_name = File.filename.rsplit('.',1)[1]
    if File_name != '3dm':
        return jsonify({"error": 1001, "msg": "not the 3dm file"}), status.HTTP_400_BAD_REQUEST

    cur.execute("SELECT * FROM BIMP.Project_Information WHERE Element_id = '%s'"%(Element_id))
    data = cur.fetchall()
    Project_id = data[0][0]

    file_path = os.path.join(config['PATH']['file_path'], Project_id, Element_id)

    if not os.path.isdir(file_path):
        os.makedirs(file_path)

    Element_file_path = os.path.join(file_path, Element_id + '.' + File_name)
    print(Element_file_path)

    file_time_start = time.time()
    File.save(Element_file_path)
    file_time_stop = time.time()
    Element_file_time = file_time_stop - file_time_start

    Element_file_size = getSize(File)

    cur.execute('''UPDATE BIMP.Project_Information SET Project_element_path = '%s', Project_element_size = '%s',
                Project_element_time = '%s' WHERE Element_id = '%s';''' %(Element_file_path, Element_file_size, Element_file_time, Element_id))
    mysql.commit()
    data_json['Log'] = "Upload Success"
    data_json['File_Path'] = Element_file_path

    data_out.append(data_json)

    mysql.close()

    return json.dumps(data_out), status.HTTP_200_OK

@app.route('/download_file', methods = ['POST'])
@cross_origin()
def download_file():
    data_json = {}
    Element_id = request.form.get('Element_id')

    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()
    cur.execute('''SELECT * FROM BIMP.Project_Information WHERE Element_id = '%s';''' %Element_id)
    data = cur.fetchall()
    if(len(data) == 0):
        data_json['Log'] = "Download Failed"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST
    else:
        file_time_start = time.time()
        Project_element_path = data[0][28]
        file_time_stop = time.time()
        Download_file_time = file_time_stop - file_time_start

        cur.execute('''UPDATE BIMP.Project_Information SET Project_source_ip = '%s' WHERE Element_id = '%s';''' %(Download_file_time, Element_id))
        mysql.commit()

        return send_from_directory(Project_element_path.rsplit("/", 1)[0], Project_element_path.rsplit("/", 1)[1], as_attachment = True), status.HTTP_200_OK


@app.route('/check_out', methods = ['POST'])
@cross_origin()
def check_out():
    mysql = pymysql.connect(user = config['MYSQL']['user'], password = config['MYSQL']['password'], port = int(config['MYSQL']['port']), host = config['MYSQL']['host'])
    cur = mysql.cursor()
    data_json = {}
    data_out = []

    request_data = request.get_json()

    Project_id = request_data['Project_id']
    Project_check_out_user_id = request_data['Project_check_out_user_id']
    Element_id = ','.join(str(v) for v in request_data['Element_id'])

    cur.execute('''SELECT * FROM BIMP.Project_Name WHERE Project_id = '%s';''' %Project_id)
    data = cur.fetchall()
    
    if(len(data) == 0):
        data_json['Log'] = "Project_id isn't exist"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST

    #print(request_data['Element_id'][0])
    #print(len(request_data['Element_id']))

    for i in range(len(request_data['Element_id'])):
        
        #print(request_data['Element_id'][i])
        #print(type(request_data['Element_id'][i]))

        cur.execute('''SELECT * FROM BIMP.Project_Information WHERE Element_id = '%s';''' %((request_data['Element_id'][i])))
        data = cur.fetchall()

        if(data[0][10] != "1"):
            
            d = datetime.datetime.now().astimezone(tz_utc_8).strftime
            Check_out_bc_start_time = d('%Y') + '/' + d('%m') + '/' + d('%d')+'/' + d('%H') + ':' + d('%M') + ':' + d('%S') + '.' + d('%f')
            bc_start_time = time.time()
            eth_data = {}
            eth_data["Project_id"] = Project_id
            eth_data["Element_id"] = request_data['Element_id'][i]
            eth_data["Project_check_out_user_id"] = Project_check_out_user_id
            Check_out_element_hashcode = Transaction(eth_data, config['ETHEREUM']['USER'])
            bc_end_time = time.time()
            Check_out_bc_end_time = d('%Y') + '/' + d('%m') + '/' + d('%d')+'/' + d('%H') + ':' + d('%M') + ':' + d('%S') + '.' + d('%f')
            Check_out_bc_time = bc_end_time - bc_start_time

            d = datetime.datetime.now().astimezone(tz_utc_8).strftime
            Check_out_time = d('%Y') + '/' + d('%m') + '/' + d('%d')+'/' + d('%H') + ':' + d('%M') + ':' + d('%S') + '.' + d('%f')

            Check_out_status = '1'
            
            db_time_start = time.time()

            cur.execute('''UPDATE BIMP.Project_Information SET Check_out_status = '%s', Check_out_time = '%s',
                        Project_check_out_bc_start_time = '%s', Project_check_out_bc_end_time = '%s',
                        Project_check_out_bc_time = '%s', Project_check_out_element_hashcode = '%s',
                        Project_check_out_user_id = '%s' WHERE Element_id = '%s';''' %(Check_out_status, 
                        str(Check_out_time), str(Check_out_bc_start_time), str(Check_out_bc_end_time),
                        str(Check_out_bc_time), str(Check_out_element_hashcode), Project_check_out_user_id,
                        request_data['Element_id'][i]))

            mysql.commit()
            db_time_stop = time.time()

            check_out_db_time = db_time_stop - db_time_start
            cur.execute('''UPDATE BIMP.Project_Information SET Check_in_status = '%s', Project_check_out_db_time = '%s' WHERE Element_id = '%s';''' %('0', check_out_db_time, request_data['Element_id'][i]))
            mysql.commit()
            data_json = {}
            data_json[request_data['Element_id'][i]] = 'Check out success!'
            
            data_out.append(data_json)

        else : 
            data_json = {}
            data_json[request_data['Element_id'][i]] = 'Element_ID has been checked out!'
            
            data_out.append(data_json)
        
    
    mysql.close()

    return json.dumps(data_out), status.HTTP_200_OK

@app.route('/Checkin_verification', methods = ['POST'])
@cross_origin()
def Checkin_verification():
    mysql = pymysql.connect(user = config['MYSQL']['user'], password = config['MYSQL']['password'], port = int(config['MYSQL']['port']), host = config['MYSQL']['host'])
    cur = mysql.cursor()
    data_json = {}
    
    request_data = request.get_json()

    Check_in_hash = request_data['Check_in_hashcode']

    total_start = time.time()

    cur.execute('''SELECT * FROM BIMP.Project_Information WHERE Project_check_in_element_hashcode = '%s';''' %(Check_in_hash))
    data = cur.fetchall()

    if(len(data) == 0):
        data_json['Log'] = "Check_in_hashcode isn't exist"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST

    else:
        db_start = time.time()

        data_json['Project_id'] = data[0][0]
        data_json['Project_user_id'] = data[0][1]
        data_json['Object_id'] = data[0][2]
        data_json['Element_id'] = data[0][3]
        data_json['Element_location'] = data[0][4]
        data_json['Element_parameters'] = data[0][5]
        data_json['Label_name'] = data[0][6]
        data_json['Label'] = data[0][7]

        #data_json = data_json.replace('\'', '\"')

        str1 = json.dumps(data_json).replace('\"', '\'')
        str1 = str1.replace('\\','')

        db_stop = time.time()
        db_total = db_stop - db_start

        #print(str1)

        #print("DB資料抓取時間:", db_total)

        db_md5_start = time.time()

        md5 = hashlib.md5()
        md5.update(str1.encode('utf-8'))
        res1 = md5.hexdigest()

        db_md5_stop = time.time()
        db_md5_total = db_md5_stop - db_md5_start

        #print("DB加密結果:",res1)

        #print("DB加密時間:", db_md5_total)

        bc_start = time.time()

        verify_data = Verification(Check_in_hash)

        verify_data = verify_data.replace('\\','')
        verify_data = verify_data.replace('\"', '\'')

        bc_stop = time.time()

        bc_total = bc_stop - bc_start

        #print(verify_data)

        #print ("BC資料抓取時間:", bc_total)

        bc_md5_start = time.time()

        md5 = hashlib.md5()
        md5.update(verify_data.encode('utf-8'))
        res2 = md5.hexdigest()

        bc_md5_stop = time.time()
        bc_md5_total = bc_md5_stop - bc_md5_start

        #print("md5加密結果:", res2)

        #print("md5加密時間:", bc_md5_total)

        compare_start = time.time()

        if (res2 == res1):
            data_json1 = {}
            data_json1['Information'] = "Data is safe !"
            data_json1['Data'] = verify_data

            compare_stop = time.time()
            compare_total = compare_stop - compare_start

            #print("比較時間:", compare_total)

            total_stop = time.time()
            total_time = total_stop - total_start

            #print("整體驗證時間:", total_time)

            INSERT = '''INSERT INTO BIMP.Project_hash_verify(
                                                    Project_id,
                                                    Element_id,
                                                    Check_in_status,
                                                    Project_element_hashcode,
                                                    DB_get_data_time,
                                                    DB_data_encrypt_time,
                                                    BC_get_data_time,
                                                    BC_data_encrypt_time,
                                                    Compared_time,
                                                    Verify_time
                                                    )VALUES(%s, %s, %s, %s, %s, %s, 
                                                            %s, %s, %s, %s);'''

    
            insert_data = (
                            data[0][0],
                            data[0][3],
                            data[0][8],
                            Check_in_hash,
                            db_total,
                            db_md5_total,
                            bc_total,
                            bc_md5_total,
                            compare_total,
                            total_time  
                        )

                        
            cur.execute(INSERT, insert_data)
            mysql.commit()
            mysql.close()

            return json.dumps(data_json1), status.HTTP_200_OK

        else:
            data_json1 = {}
            data_json1['Information'] = "Data is unsafe !"
            data_json1['The Original Data From Blockchain'] = verify_data

            compare_stop = time.time()
            compare_total = compare_stop - compare_start

            #print("比較時間:", compare_total)

            total_stop = time.time()
            total_time = total_stop - total_start

            #print("整體驗證時間:", total_time)

            INSERT = '''INSERT INTO BIMP.Project_hash_verify(
                                                    Project_id,
                                                    Element_id,
                                                    Check_in_status,
                                                    Project_element_hashcode,
                                                    DB_get_data_time,
                                                    DB_data_encrypt_time,
                                                    BC_get_data_time,
                                                    BC_data_encrypt_time,
                                                    Compared_time,
                                                    Verify_time
                                                    )VALUES(%s, %s, %s, %s, %s, %s, 
                                                            %s, %s, %s, %s);'''

    
            insert_data = (
                            data[0][0],
                            data[0][3],
                            data[0][8],
                            Check_in_hash,
                            db_total,
                            db_md5_total,
                            bc_total,
                            bc_md5_total,
                            compare_total,
                            total_time  
                        )

                        
            cur.execute(INSERT, insert_data)
            mysql.commit()
            mysql.close()

            return json.dumps(data_json1), status.HTTP_200_OK

@app.route('/Checkout_verification', methods = ['POST'])
@cross_origin()
def Checkout_verification():
    mysql = pymysql.connect(user = config['MYSQL']['user'], password = config['MYSQL']['password'], port = int(config['MYSQL']['port']), host = config['MYSQL']['host'])
    cur = mysql.cursor()
    data_json = {}
    
    request_data = request.get_json()

    Check_out_hash = request_data['Check_out_hashcode']

    total_start = time.time()

    cur.execute('''SELECT * FROM BIMP.Project_Information WHERE Project_check_out_element_hashcode = '%s';''' %(Check_out_hash))
    data = cur.fetchall()

    if(len(data) == 0):
        data_json['Log'] = "Check_out_hashcode isn't exist"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST

    else:
        db_start = time.time()

        data_json['Project_id'] = data[0][0]
        data_json['Element_id'] = data[0][3]
        data_json['Project_check_out_user_id'] = data[0][27]

        #data_json = data_json.replace('\'', '\"')

        str1 = json.dumps(data_json).replace('\"', '\'')
        str1 = str1.replace('\\','')

        db_stop = time.time()
        db_total = db_stop - db_start

        #print(str1)

        #print("DB資料抓取時間:", db_total)

        db_md5_start = time.time()

        md5 = hashlib.md5()
        md5.update(str1.encode('utf-8'))
        res1 = md5.hexdigest()

        db_md5_stop = time.time()
        db_md5_total = db_md5_stop - db_md5_start

        #print("DB加密結果:",res1)

        #print("DB加密時間:", db_md5_total)

        bc_start = time.time()

        verify_data = Verification(Check_out_hash)

        verify_data = verify_data.replace('\\','')
        verify_data = verify_data.replace('\"', '\'')

        bc_stop = time.time()

        bc_total = bc_stop - bc_start

        #print(verify_data)

        #print ("BC資料抓取時間:", bc_total)

        bc_md5_start = time.time()

        md5 = hashlib.md5()
        md5.update(verify_data.encode('utf-8'))
        res2 = md5.hexdigest()

        bc_md5_stop = time.time()
        bc_md5_total = bc_md5_stop - bc_md5_start

        #print("md5加密結果:", res2)

        #print("md5加密時間:", bc_md5_total)

        compare_start = time.time()

        if (res2 == res1):
            data_json1 = {}
            data_json1['Information'] = "Data is safe !"
            data_json1['Data'] = verify_data

            compare_stop = time.time()
            compare_total = compare_stop - compare_start

            #print("比較時間:", compare_total)

            total_stop = time.time()
            total_time = total_stop - total_start

            #print("整體驗證時間:", total_time)

            INSERT = '''INSERT INTO BIMP.Project_hash_verify(
                                                    Project_id,
                                                    Element_id,
                                                    Check_in_status,
                                                    Project_element_hashcode,
                                                    DB_get_data_time,
                                                    DB_data_encrypt_time,
                                                    BC_get_data_time,
                                                    BC_data_encrypt_time,
                                                    Compared_time,
                                                    Verify_time
                                                    )VALUES(%s, %s, %s, %s, %s, %s, 
                                                            %s, %s, %s, %s);'''

    
            insert_data = (
                            data[0][0],
                            data[0][3],
                            data[0][8],
                            Check_out_hash,
                            db_total,
                            db_md5_total,
                            bc_total,
                            bc_md5_total,
                            compare_total,
                            total_time  
                        )

                        
            cur.execute(INSERT, insert_data)
            mysql.commit()
            mysql.close()

            return json.dumps(data_json1), status.HTTP_200_OK

        else:
            data_json1 = {}
            data_json1['Information'] = "Data is unsafe !"
            data_json1['The Original Data From Blockchain'] = verify_data

            compare_stop = time.time()
            compare_total = compare_stop - compare_start

            #print("比較時間:", compare_total)

            total_stop = time.time()
            total_time = total_stop - total_start

            #print("整體驗證時間:", total_time)

            INSERT = '''INSERT INTO BIMP.Project_hash_verify(
                                                    Project_id,
                                                    Element_id,
                                                    Check_in_status,
                                                    Project_element_hashcode,
                                                    DB_get_data_time,
                                                    DB_data_encrypt_time,
                                                    BC_get_data_time,
                                                    BC_data_encrypt_time,
                                                    Compared_time,
                                                    Verify_time
                                                    )VALUES(%s, %s, %s, %s, %s, %s, 
                                                            %s, %s, %s, %s);'''

    
            insert_data = (
                            data[0][0],
                            data[0][3],
                            data[0][8],
                            Check_out_hash,
                            db_total,
                            db_md5_total,
                            bc_total,
                            bc_md5_total,
                            compare_total,
                            total_time  
                        )

                        
            cur.execute(INSERT, insert_data)
            mysql.commit()
            mysql.close()

            return json.dumps(data_json1), status.HTTP_200_OK

@app.route('/sql_select', methods = ['POST'])
@cross_origin()
def sql_select():
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()

    data_json = {}
    request_data = request.get_json()

    SQL_string = request_data['SQL_command']
    #Where = request_data['WHE']

    cur.execute('''%s''' %SQL_string)
    #cur.execute('''%s WHERE %s;''' %(SQL_string, Where))
    data = cur.fetchall()
    if(len(data) == 0):
        data_json['Log'] = "GET Failed"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST
    else:
        data_json['Data'] = data

        return json.dumps(data_json), status.HTTP_200_OK

@app.route('/sql_insert', methods = ['POST'])
@cross_origin()
def sql_insert():
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()

    data_json = {}
    request_data = request.get_json()
    
    SQL_string = request_data['SQL_command']
    
    if(SQL_string == ''):
        data_json['Log'] = "Please Enter SQL Command!"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST
    else:
        cur.execute('''%s''' %SQL_string)
        mysql.commit()
        mysql.close()
        data_json['Log'] = "Insert Success!"
        return json.dumps(data_json), status.HTTP_200_OK

@app.route('/sql_update', methods = ['POST'])
@cross_origin()
def sql_update():
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()

    data_json = {}
    request_data = request.get_json()
    
    SQL_string = request_data['SQL_command']
    #Where = request_data['WHE']
    
    if(SQL_string == ''):
        data_json['Log'] = "Please Enter SQL Command!"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST
    else:
        cur.execute('''%s''' %SQL_string)
        #cur.execute('''%s WHERE %s;''' %(SQL_string, Where))
        mysql.commit()
        mysql.close()
        data_json['Log'] = "Update Success!"
        return json.dumps(data_json), status.HTTP_200_OK

@app.route('/sql_delete', methods = ['POST'])
@cross_origin()
def sql_delete():
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()

    data_json = {}
    request_data = request.get_json()
    
    SQL_string = request_data['SQL_command']
    #Where = request_data['WHE']
    
    if(SQL_string == ''):
        data_json['Log'] = "Please Enter SQL Command!"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST
    else:
        cur.execute('''%s''' %SQL_string)
        #cur.execute('''%s WHERE %s;''' %(SQL_string, Where))
        mysql.commit()
        mysql.close()
        data_json['Log'] = "Delete Success!"
        return json.dumps(data_json), status.HTTP_200_OK

#@app.route("/test",  methods=['POST'])
#def index():
#    request_data = request.get_json()
#    print(request_data["cmd"])
#    return request_data["cmd"]

app.run(host = config['FLASK']['host'], port = int(config['FLASK']['port']), debug=True )


# if __name__ == '__main__':
#    app.run(host='0.0.0.0',port=5052,debug=True)
