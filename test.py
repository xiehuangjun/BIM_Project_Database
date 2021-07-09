import pymysql, json, configparser, os, datetime, time, shutil, base64
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS, cross_origin
from flask_api import status
import pandas

mysql = pymysql.connect(host = '140.118.121.100', port = 3307, user = 'root', password = '12345678', db = 'TEST')
cur = mysql.cursor() 

data_json = {}
data_out = []
data_text = []

cur.execute('''SELECT * FROM TEST.Test_Information WHERE Project_id = 'Test_Project';''')
data = cur.fetchall()
    
if(len(data) == 0):
    data_json['Log'] = "Project ID isn't existed !"
    data_out.append(data_json)
    
    print(data_out)
    # return json.dumps(data_out), status.HTTP_400_BAD_REQUEST

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
        
        data_json['Project_id'] = data1[0][0]
        data_json['Project_user_id'] = data1[0][1]
        data_json['Objec_id'] = data1[0][2]
        data_json['Element_id'] = data1[0][3]
        data_json['Element_loaction'] = data1[0][4]
        data_json['Element_parameters'] = data1[0][5]
        data_json['Label_name'] = data1[0][6]
        data_json['Label'] = data1[0][7]
        data_json['Check_in_time'] = data1[0][9]
        # print(data1[0][4])

        # print (data_json)

        data_out.append(data_json)

        print(data_out[x])

    # return json.dumps(data_out), status.HTTP_200_OK 

# print(data_out)
