import base64
import os, jwt
import sqlite3, uuid, datetime, json
import time
from runMelodyRNN import runRnn
from runMusicat import run, convertMidiToMusicat
from flask import Flask, request,Response, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from runCreativityScoring import calculateCreativityScores

import wave
load_dotenv()
app = Flask(__name__)
cors = CORS(app)


SECRET_KEY = os.getenv("MY_SECRET")
USER_DIR = os.getenv("USER_DIR")

def get_db_connection():
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn



@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        conn = get_db_connection()
        f = request.files['file']
        jwtToken = request.form['jwtToken']
        count = request.form['count']
        try:
            decodedToken = jwt.decode(jwtToken, SECRET_KEY, algorithms=["HS256"])
        except:
            return "JWT Token expired", 401
        subjectId = decodedToken['id']
        composition_uuid = str(uuid.uuid4())
        midfilepath = "/home/olli/midiDataSubjects/" + subjectId + "/trial_" + count + ".mid"
        f.save(midfilepath)
        result = run(os.getcwd()+"/RhythmCat.exe", midfilepath)
        conn.execute("INSERT INTO compositions (id,fk,filepath) VALUES( ?,?,?)", (composition_uuid, subjectId, midfilepath))
        conn.commit()
        conn.close()
        return Response(result, status=200)

@app.route('/start', methods=['GET'])
def startApp():
    conn = get_db_connection()
    subject_uuid = str(uuid.uuid4())

    conn.execute("INSERT INTO subject (id) VALUES( '%s')" % subject_uuid)
    conn.commit()
    conn.close()
    os.mkdir(USER_DIR + subject_uuid)
    os.mkdir(USER_DIR + subject_uuid + "/generatedMelodies")

    encoded_jwt = jwt.encode({"id": subject_uuid,"exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=30000)}, SECRET_KEY, algorithm="HS256")
    print(encoded_jwt)
    return jsonify(encoded_jwt), 200


@app.route('/sendBlob', methods=['POST'])
def sendBlob():
    base64_string = request.form['wavFile']
    base64_stringarr = base64_string.split(",")
    base64_string = base64_stringarr[1]
    cmd =  'echo '+ base64_string + '| base64 --decode' + ' > ~/backend/temp2.wav'
    try:
        os.system(cmd)

    except:
        print("cmd not working")

    return Response(request.form['wavFile'] ,status=200)



@app.route('/runRNN', methods=['POST'])
def runRNN():
    if request.method == 'POST':
        data = request.json['data']
        meter = request.json['meter']
        jwtToken = request.json['jwtToken']
        try:
            decodedToken = jwt.decode(jwtToken, SECRET_KEY, algorithms=["HS256"])
        except:
            return "JWT Token expired", 401
        subjectId = decodedToken['id']

        UserPath = USER_DIR + subjectId + "/generatedMelodies"
        response = runRnn(data, UserPath,meter)
        return Response(response, status=200)
@app.route('/runMusicat', methods=['POST'])
def runMusicat():
    if request.method == 'POST':

        '''#conn = get_db_connection()
        
        #jwtToken = request.form['jwtToken']
        #count = request.form['count']
        #try:
           # decodedToken = jwt.decode(jwtToken, SECRET_KEY, algorithms=["HS256"])
        except:
            return "JWT Token expired", 401
        subjectId = decodedToken['id']
        composition_uuid = str(uuid.uuid4())
        '''
        #composition = request.form['composition']

        #result = run(os.getcwd()+"/RhythmCat.exe", composition)
        #conn.execute("INSERT INTO compositions (id,fk,filepath) VALUES( ?,?,?)", (composition_uuid, subjectId, midfilepath))
        #conn.commit()
        #conn.close()
        data = request.json['data']
        meter = request.json['meter']
        response = run(os.getcwd()+"/RhythmCat.exe", data)
        print(response)
        return Response(response,status=200)

@app.route('/submitComposition', methods=['POST'])
def submitComposition():
    if request.method == 'POST':
        '''#conn = get_db_connection()

        #jwtToken = request.form['jwtToken']
        #count = request.form['count']
        #try:
           # decodedToken = jwt.decode(jwtToken, SECRET_KEY, algorithms=["HS256"])
        except:
            return "JWT Token expired", 401
        subjectId = decodedToken['id']
        composition_uuid = str(uuid.uuid4())
        '''
        # composition = request.form['composition']

        # result = run(os.getcwd()+"/RhythmCat.exe", composition)
        # conn.execute("INSERT INTO compositions (id,fk,filepath) VALUES( ?,?,?)", (composition_uuid, subjectId, midfilepath))
        # conn.commit()
        # conn.close()
        jwtToken = request.json['jwtToken']

        try:
            decodedToken = jwt.decode(jwtToken, SECRET_KEY, algorithms=["HS256"])
        except:
            return "JWT Token expired", 401
        conn = get_db_connection()
        cur = conn.cursor()
        composition_uuid = str(uuid.uuid4())
        subjectId = decodedToken['id']
        data = request.json['data']
        print(type(data))

        cur.execute("SELECT * FROM compositions WHERE id=?",(composition_uuid,))
        row = cur.fetchone()
        while row is not None:
            composition_uuid = str(uuid.uuid4())
            cur.execute("SELECT * FROM compositions WHERE id=?",(composition_uuid,))
            row = cur.fetchone()
        os.mkdir(USER_DIR + subjectId + "/" + composition_uuid )
        os.mkdir(USER_DIR + subjectId + "/" + composition_uuid + "/musicatPNG")
        pathToImageDir = USER_DIR + subjectId + "/" + composition_uuid + "/musicatPNG/"
        jsonComposition = json.dumps(data)
        pathToComposition = USER_DIR + subjectId + "/" + composition_uuid + "/compositionData.json"
        with open(pathToComposition,'w') as f:
            json.dump(jsonComposition,f)
        conn.execute("""INSERT INTO compositions (id,fk,filepath,composition) VALUES( ?,?,?,?);""",
                     (composition_uuid, subjectId, pathToImageDir, pathToComposition))

        print(pathToImageDir)
        result = run(os.getcwd() + "/RhythmCat.exe", data, pathToImageDir)

        print(result)
        response = {}
        orig,flex,fluency = calculateCreativityScores(data)
        response['originality'] = orig
        response['flexability'] = flex
        response['fluency'] = fluency
        with open(pathToImageDir+"out.png",'rb') as musicatImage:
            im_bytes = musicatImage.read()
        encoded = base64.b64encode(im_bytes).decode("utf8")
        response['musicatPNG'] = encoded


        # store values in db
        # store composition in db
        # run musicat and produce the png
        # return also the results from musicats computation
        response = json.dumps(response)
        print(response)
        return Response(response, status=200)



@app.route('/calculateCreativity', methods=['POST'])
def runCreativityScoring():
    if request.method == 'POST':
        '''#conn = get_db_connection()

        #jwtToken = request.form['jwtToken']
        #count = request.form['count']
        #try:
           # decodedToken = jwt.decode(jwtToken, SECRET_KEY, algorithms=["HS256"])
        except:
            return "JWT Token expired", 401
        subjectId = decodedToken['id']
        composition_uuid = str(uuid.uuid4())
        '''
        # composition = request.form['composition']

        # result = run(os.getcwd()+"/RhythmCat.exe", composition)
        # conn.execute("INSERT INTO compositions (id,fk,filepath) VALUES( ?,?,?)", (composition_uuid, subjectId, midfilepath))
        # conn.commit()
        # conn.close()
        data = request.json['data']


        response = {}
        orig,flex,fluency = calculateCreativityScores(data)
        response['originality'] = orig
        response['flexability'] = flex
        response['fluency'] = fluency

        response = json.dumps(response)
        print(response)
        return Response(response, status=200)
