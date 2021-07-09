import pymysql, json, configparser, os, datetime, time, shutil, base64
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS, cross_origin
from flask_api import status
from subfunction import getSize
from Ethereum_Transaction import Transaction

path = os.path.abspath('.')
cfgpath = path.split('BIM_API')[0] + 'BIM_API/config.ini'

config = configparser.ConfigParser()
config.read(cfgpath)

tz_utc = datetime.timezone(datetime.timedelta(hours = int(time.timezone / -3600)))  # system timezone
tz_utc_0 = datetime.timezone(datetime.timedelta(hours = 0))  # system timezone
# datetime.datetime.now().astimezone(tz_utc).isoformat()

app = Flask(__name__)

@app.route('/register', methods = ['POST'])
@cross_origin()
def register():
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()
    
    data_json = {}
    request_data = request.get_json()
    cur.execute('''SELECT * FROM BIM.account WHERE User_accountID = '%s';''' %request_data['User_accountID'])
    data = cur.fetchall()
    if(len(data) != 0):
        data_json['Log'] = "Account_ID already used"
        cur.execute('''UPDATE BIM.account SET User_status = '1' WHERE User_accountID = '%s';''' %request_data['User_accountID'])
        mysql.commit()
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST
    else:
        INSERT = '''INSERT INTO BIM.account (User_accountID, 
                                        User_account_name, 
                                        User_group, 
                                        User_password, 
                                        User_createTime, 
                                        User_status, 
                                        User_status_change) VALUES( %s, %s, %s, %s, %s, %s, %s);'''
        insert_data = (
            request_data['User_accountID'],
            request_data['User_account_name'],
            request_data['User_group'],
            request_data['User_password'],
            datetime.datetime.now().astimezone(tz_utc).isoformat(),
            '0',
            datetime.datetime.now().astimezone(tz_utc).isoformat())
        cur.execute(INSERT, insert_data)
        mysql.commit()
        data_json['Log'] = "Register Success"
        return json.dumps(data_json), status.HTTP_200_OK

@app.route('/login', methods = ['POST'])
@cross_origin()
def login():
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()
    data_json = {}
    request_data = request.get_json()
    User_accountID = request_data["User_accountID"]
    User_password = request_data["User_password"]
    cur.execute('''SELECT * FROM BIM.account WHERE User_accountID = '%s';''' %User_accountID)
    data = cur.fetchall()
    if(len(data) == 0):
        data_json['Log'] = "Login Failed1"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST
    else:
        if(data[0][3] != User_password):
            data_json['Log'] = "Login Failed"
            cur.execute('''UPDATE BIM.account SET User_status = '3',  User_status_change = '%s' WHERE User_accountID = '%s';''' %(datetime.datetime.now().astimezone(tz_utc).isoformat(), User_accountID))
            mysql.commit()
            return json.dumps(data_json), status.HTTP_400_BAD_REQUEST
        else:
            data_json['Log'] = "Login Success"
            cur.execute('''UPDATE BIM.account SET User_status = '2',  User_status_change = '%s' WHERE User_accountID = '%s';''' %(datetime.datetime.now().astimezone(tz_utc).isoformat(), User_accountID))
            mysql.commit()
            return json.dumps(data_json), status.HTTP_200_OK

@app.route('/object_store', methods = ['POST'])
@cross_origin()
def object_store():
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()
    data_json = {}
    User_accountID = request.form.get('User_accountID')
    check_account = cur.execute("SELECT * FROM BIM.account WHERE User_accountID = '%s'"%(User_accountID))
    print(check_account)
    if check_account == 0:
        return jsonify({"error" : "account not exist"})
    Object_Name = request.form.get('Object_Name')

    if(not request.files['opng']):
        return jsonify({"error" : "request png file", "code" : "file_01"}), status.HTTP_400_BAD_REQUEST
    if(not request.files['threedm']):
        return jsonify({"error" : "request 3dm file", "code" : "file_02"}), status.HTTP_400_BAD_REQUEST
    if(not request.files['gh']):
        return jsonify({"error" : "request gh file", "code" : "file_03"}), status.HTTP_400_BAD_REQUEST
    if(not request.files['pjpg']):
        return jsonify({"error" : "request jpg file", "code" : "file_04"}), status.HTTP_400_BAD_REQUEST
    if(not request.files['ojson']):
        return jsonify({"error" : "request json file", "code" : "file_05"}), status.HTTP_400_BAD_REQUEST
    if(not request.files['pdf']):
        return jsonify({"error" : "request json file", "code" : "file_06"}), status.HTTP_400_BAD_REQUEST

    File_png = request.files['opng']
    File_png_name = File_png.filename.rsplit('.',1)[1]
    if ((File_png_name != 'png') and (File_png_name != 'PNG')):
        return jsonify({"error": 1001, "msg": "不是png檔案"}), status.HTTP_400_BAD_REQUEST

    File_3dm = request.files['threedm']
    File_3dm_name = File_3dm.filename.rsplit('.',1)[1]
    if File_3dm_name != '3dm':
        return jsonify({"error": 1001, "msg": "不是3dm檔案"}), status.HTTP_400_BAD_REQUEST

    File_gh = request.files['gh']
    File_gh_name = File_gh.filename.rsplit('.',1)[1]
    if File_gh_name != 'gh':
        return jsonify({"error": 1001, "msg": "不是gh檔案"}), status.HTTP_400_BAD_REQUEST

    File_jpg = request.files['pjpg']
    File_jpg_name = File_jpg.filename.rsplit('.',1)[1]
    if((File_jpg_name != 'jpg') and (File_jpg_name != 'JPG')):
        return jsonify({"error": 1001, "msg": "不是jpg檔案"}), status.HTTP_400_BAD_REQUEST

    File_json = request.files['ojson'] 
    File_json_name = File_json.filename.rsplit('.',1)[1]
    if((File_json_name != 'json') and (File_json_name != 'JSON')):
        return jsonify({"error": 1001, "msg": "不是json檔案"}), status.HTTP_400_BAD_REQUEST

    File_pdf = request.files['pdf'] 
    File_pdf_name = File_pdf.filename.rsplit('.',1)[1]
    if((File_pdf_name != 'pdf') and (File_pdf_name != 'pdf')):
        return jsonify({"error": 1001, "msg": "不是pdf檔案"}), status.HTTP_400_BAD_REQUEST
    
    jsonload = json.load(File_json)
    
    if(File_gh.filename.rsplit('V',1)[0][len(File_gh.filename.rsplit('V',1)[0]) - 1] == 'h'):
        search_name = File_gh.filename.rsplit('.',1)[0]
    else:
        search_name = File_gh.filename.rsplit('V',1)[0]
    print(search_name)
    cur.execute('''SELECT * FROM BIM.Object_Information WHERE Object_ID = '%s';''' %search_name)
    data = cur.fetchall()

    if(len(data)  == 0):
        Object_version = ''
        Object_update_times = '0'
        # Object_ID = User_accountID + list(jsonload)[0][0] + list(jsonload)[1][0] + list(jsonload)[2][0] + datetime.datetime.now().astimezone(tz_utc_0).strftime('%Y%m%d%H%M%S%f')
        Object_ID = User_accountID + datetime.datetime.now().astimezone(tz_utc_0).strftime('%Y%m%d%H%M%S%f')
    else:
        cur.execute('''UPDATE BIM.Object_Information SET Object_update_times = '%s' WHERE Object_ID = '%s';''' %(int(data[0][17]) + 1, search_name))
        Object_update_times = ''
        Object_version = 'V' + str(int(data[0][17]) + 1)
        Object_ID = search_name + 'V' + str(int(data[0][17]) + 1)

    file_path = os.path.join(config['PATH']['file_path'], User_accountID, Object_ID)

    if not os.path.isdir(file_path):
        os.makedirs(file_path)

    Object_json_path = os.path.join(file_path, Object_ID + '.json')
    Object_png_path = os.path.join(file_path, Object_ID + '.png')
    Object_gh_path = os.path.join(file_path, Object_ID + '.gh')
    Object_3dm_path = os.path.join(file_path, Object_ID + '.3dm')
    Project_jpg_path = os.path.join(file_path, Object_ID + '.jpg')
    Object_pdf_path = os.path.join(file_path,Object_ID + '.pdf')

    png_time_start = time.time()
    File_png.save(Object_png_path)
    png_time_stop = time.time()
    Object_png_time = png_time_stop - png_time_start

    tdm_time_start = time.time()
    File_3dm.save(Object_3dm_path)
    tdm_time_stop = time.time()
    Object_3dm_time = tdm_time_stop- tdm_time_start

    gh_time_start = time.time()
    File_gh.save(Object_gh_path)
    gh_time_stop = time.time()
    Object_gh_time = gh_time_stop - gh_time_start

    jpg_time_start = time.time()
    File_jpg.save(Project_jpg_path)
    jpg_time_stop = time.time()
    Project_jpg_time = jpg_time_stop- jpg_time_start

    json_time_start = time.time()
    with open(Object_json_path, 'w', encoding='utf-8') as f:
        json.dump(jsonload, f)
    json_time_stop = time.time()
    Object_json_time = json_time_stop - json_time_start

    pdf_time_start = time.time()
    File_pdf.save(Object_pdf_path)
    pdf_time_stop = time.time()
    Object_pdf_time = pdf_time_stop- pdf_time_start

    File_png_size = getSize(File_png)
    File_3dm_size = getSize(File_3dm)
    File_gh_size = getSize(File_gh)
    File_jpg_size = getSize(File_jpg)
    File_json_size = getSize(File_json)
    File_pdf_size = getSize(File_pdf)  

    bc_time_start = time.time()
    eth_data = {}
    eth_data["User_accountID"] = User_accountID
    eth_data["Object_Name"] = Object_Name 
    eth_data["Object_parameter"] = json.dumps(jsonload)  #  反斜線問題
    eth_data["Object_json_path"] = Object_json_path
    eth_data["Object_json_size"] = File_json_size
    eth_data["Object_png_path"] = Object_png_path
    eth_data["Object_png_size"] = File_png_size  
    eth_data["Object_gh_path"] = Object_gh_path
    eth_data["Object_gh_size"] = File_gh_size
    eth_data["Object_3dm_path"] = Object_3dm_path
    eth_data["Object_3dm_size"] = File_3dm_size
    eth_data["Project_jpg_path"] = Project_jpg_path
    eth_data["Project_jpg_size"] = File_jpg_size
    eth_data["Object_pdf_path"] = Object_pdf_path
    eth_data["Object_pdf_size"] = File_pdf_size
    eth_data["Object_version"] = Object_version
    hash_code = Transaction(eth_data, config['ETHEREUM']['user'])
    bc_time_stop = time.time()
    Object_bc_time = bc_time_stop - bc_time_start

    INSERT = '''INSERT INTO BIM.Object_Information(User_accountID,
                                                   Object_Name,
                                                   Object_ID,
                                                   Object_parameter,
                                                   Object_json_path,
                                                   Object_json_size,
                                                   Object_png_path,
                                                   Object_png_size,
                                                   Object_gh_path,
                                                   Object_gh_size,
                                                   Object_3dm_path,
                                                   Object_3dm_size,
                                                   Project_jpg_path,
                                                   Project_jpg_size,
                                                   Object_pdf_path,
                                                   Object_pdf_size,
                                                   Object_version,
                                                   Object_update_times,
                                                   Object_download_times,
                                                   Object_hashcode,
                                                   Object_bc_time,
                                                   Object_db_time,
                                                   Object_total_time,
                                                   Object_json_time,
                                                   Object_png_time,
                                                   Object_gh_time,
                                                   Object_3dm_time,
                                                   Project_jpg_time,
                                                   Object_pdf_time,
                                                   Finshed_upload_time,
                                                   Id_co_times,
                                                   Id_ch_time,
                                                   Id_so_time,
                                                   Id_to_time)VALUES(%s, %s, %s, %s, %s, %s, 
                                                                     %s, %s, %s, %s, %s, %s, 
                                                                     %s, %s, %s, %s, %s, %s, 
                                                                     %s, %s, %s, %s, %s, %s, 
                                                                     %s, %s, %s, %s, %s, %s,
                                                                     %s, %s, %s, %s);'''

    insert_data = (
        User_accountID,
        Object_Name,
        Object_ID,
        json.dumps(jsonload),
        Object_json_path,
        File_json_size,
        Object_png_path,
        File_png_size,
        Object_gh_path,
        File_gh_size,
        Object_3dm_path,
        File_3dm_size,
        Project_jpg_path,
        File_jpg_size,
        Object_pdf_path,
        File_pdf_size,
        Object_version,  # Object_version
        Object_update_times, # Object_update_times
        '0', # Object_download_times
        hash_code,
        str(Object_bc_time),
        '',    #db_time
        '',    #total_time
        str(Object_json_time),
        str(Object_png_time),
        str(Object_gh_time),
        str(Object_3dm_time),
        str(Project_jpg_time),
        str(Object_pdf_time),
        '0',
        '0',
        '0',
        '0',
        '0')

    db_time_start= time.time()
    cur.execute(INSERT, insert_data)
    mysql.commit()
    db_time_stop = time.time()

    Object_db_time = db_time_stop - db_time_start
    Object_total_time = Object_db_time + Object_bc_time 
    cur.execute('''UPDATE BIM.Object_Information SET Object_db_time = '%s', Object_total_time = '%s' WHERE Object_ID = '%s';''' %(Object_db_time, Object_total_time, Object_ID))
    mysql.commit()
    data_json['Log'] = "Upload Success"

    d = datetime.datetime.now().astimezone(tz_utc_0).strftime
    Finshed_upload_time = d('%Y') + '/' + d('%m') + '/' + d('%d')+'/' + d('%H') + ':' + d('%M') + ':' + d('%S') + '.' + d('%f')
    cur.execute('''UPDATE BIM.Object_Information SET Finshed_upload_time = '%s' WHERE Object_ID = '%s';''' %(Finshed_upload_time, Object_ID))
    mysql.commit()
    return json.dumps(data_json), status.HTTP_200_OK


@app.route('/object_information', methods = ['GET'])
@cross_origin()
def object_information():
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()
    data_json = {}
    User_accountID = request.args.get('User_accountID')
    Object_Name = request.args.get('Object_Name')
    Object_ID = request.args.get('Object_ID')
    cur.execute('''SELECT * FROM BIM.Object_Information WHERE Object_ID = '%s';''' %Object_ID)
    data = cur.fetchall()
    if(len(data) == 0):
        data_json["Log"] = "Get Failed"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST
    else: 
        Object_json_path = data[0][4]
        Object_png_path = data[0][6]
        Project_jpg_path = data[0][12]

        file_png= open(Object_png_path, 'rb').read()
        file_png_64 = base64.b64encode(file_png)

        file_jpg= open(Project_jpg_path, 'rb').read()
        file_jpg_64 = base64.b64encode(file_jpg)

        file_json = open(Object_json_path, 'rb').read()
        
        data_json['User_accountID'] = User_accountID
        data_json['Object_Name'] = Object_Name
        data_json['Object_ID'] = Object_ID
        data_json['Object_json_path'] = json.loads(file_json)
        data_json['Object_png_path'] = file_png_64.decode('UTF-8')
        data_json['Object_jpg_path'] = file_jpg_64.decode('UTF-8')

        return json.dumps(data_json), status.HTTP_200_OK


@app.route('/3dm_download', methods = ['GET'])
@cross_origin()
def tdm_download():
    data_json = {}
    Object_ID = request.args.get('Object_ID')
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()
    cur.execute('''SELECT * FROM BIM.Object_Information WHERE Object_ID = '%s';''' %Object_ID)
    data = cur.fetchall()
    if(len(data) == 0):
        data_json['Log'] = "Download Failed"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST
    else:
        Object_3dm_path = data[0][10]
        return send_from_directory(Object_3dm_path.rsplit("/", 1)[0], Object_3dm_path.rsplit("/", 1)[1], as_attachment = True), status.HTTP_200_OK


@app.route('/gh_download', methods = ['GET'])
@cross_origin()
def gh_download():
    data_json = {}
    Object_ID = request.args.get('Object_ID')
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()
    cur.execute('''SELECT * FROM BIM.Object_Information WHERE Object_ID = '%s';''' %Object_ID)
    data = cur.fetchall()
    if(len(data) == 0):
        data_json['Log'] = "Download Failed"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST
    else:
        Object_gh_path = data[0][8]
        cur.execute('''UPDATE BIM.Object_Information SET Object_download_times = '%s' WHERE Object_ID = '%s';''' %(int(data[0][18]) + 1, Object_ID))
        mysql.commit()
        return send_from_directory(Object_gh_path.rsplit("/", 1)[0], Object_gh_path.rsplit("/", 1)[1], as_attachment = True), status.HTTP_200_OK

@app.route('/pdf_download', methods = ['GET'])
@cross_origin()
def pdf_download():
    data_json = {}
    Object_ID = request.args.get('Object_ID')
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()
    cur.execute('''SELECT * FROM BIM.Object_Information WHERE Object_ID = '%s';''' %Object_ID)
    data = cur.fetchall()
    if(len(data) == 0):
        data_json['Log'] = "Download Failed"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST
    else:
        Object_pdf_path = data[0][14]
        return send_from_directory(Object_pdf_path.rsplit("/", 1)[0], Object_pdf_path.rsplit("/", 1)[1], as_attachment = True), status.HTTP_200_OK

@app.route('/main', methods = ['GET'])
@cross_origin()
def main():
    data_out = []
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()
    cur.execute('''SELECT * FROM BIM.Object_Information''')
    data = cur.fetchall()
    for raw in data:
        data_json = {}
        data_json['User_accountID'] = raw[0]
        data_json['Object_Name'] = raw[1] 
        data_json['Object_ID'] = raw[2]
        Object_png_path = raw[6]
        file_png = open(Object_png_path, 'rb').read()
        data_json['Object_png_path'] = base64.b64encode(file_png).decode('UTF-8')
        data_out.append(data_json)

    return json.dumps(data_out), status.HTTP_200_OK


@app.route('/search', methods = ['GET'])
@cross_origin()
def search():
    data_out = []
    User_accountID = request.args.get('User_accountID')
    Object_Name = request.args.get('Object_Name')
    mysql = pymysql.connect(user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config["MYSQL"]["port"]), host = config['MYSQL']["host"])
    cur = mysql.cursor()
    if(User_accountID != ""):
        cur.execute('''SELECT * FROM BIM.Object_Information WHERE User_accountID = '%s';''' %User_accountID)
        data = cur.fetchall()
        for raw in data:
            data_json = {}
            data_json['User_accountID'] = raw[0]
            data_json['Object_Name'] = raw[1]
            data_json['Object_ID'] = raw[2]
            Object_png_path = raw[6]
            file_png = open(Object_png_path, 'rb').read()
            data_json['Object_png_path'] = base64.b64encode(file_png).decode('UTF-8')
            data_out.append(data_json)
        
        return json.dumps(data_out), status.HTTP_200_OK
    elif(Object_Name != ""):
        cur.execute('''SELECT * FROM BIM.Object_Information WHERE Object_Name = '%s';''' %Object_Name)
        data = cur.fetchall()
        for raw in data:
            data_json = {}
            data_json['User_accountID'] = raw[0]
            data_json['Object_Name'] = raw[1]
            data_json['Object_ID'] = raw[2]
            Object_png_path = raw[6]
            file_png = open(Object_png_path, 'rb').read()
            data_json['Object_png_path'] = base64.b64encode(file_png).decode('UTF-8')
            data_out.append(data_json)
        return json.dumps(data_out), status.HTTP_200_OK
    else:
        data_json["Log"] = "Search Failed"
        return json.dumps(data_json), status.HTTP_400_BAD_REQUEST

app.run(host = config['FLASK']['host'], port = int(config['FLASK']['port']), debug=True )

