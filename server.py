import base64
import os, jwt, datetime
import sqlite3, uuid, datetime, json
import time
from runMelodyRNN import runRnn
from runMusicat import run, convertMidiToMusicat
from flask import Flask, request,Response, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from runCreativityScoring import calculateCreativityScores
from prometheus_flask_exporter import PrometheusMetrics
import wave
load_dotenv()
app = Flask(__name__)
cors = CORS(app)
metrics = PrometheusMetrics(app)


SECRET_KEY = os.getenv("MY_SECRET")
USER_DIR = os.getenv("USER_DIR")

metrics.info('app_info', 'Application info', version='1.0.3')





common_counter = metrics.counter(
    'by_path_counter', 'Request count by request paths',
    labels={'path': lambda: request.path}
)



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



@app.route('/start', methods=['POST'])
@common_counter
def startApp():
    if request.method == 'POST':
        user = request.json['data']
        conn = get_db_connection()
        subject_uuid = str(uuid.uuid4())
       

        conn.execute("""INSERT INTO subject (id,user) VALUES(?,?);""", (subject_uuid, user))
        conn.commit()
        conn.close()
        os.mkdir(os.getcwd()+"/../userData/" + subject_uuid)
        os.mkdir(os.getcwd()+"/../userData/" + subject_uuid + "/generatedMelodies")
        os.mkdir(os.getcwd()+"/../userData/"+ subject_uuid + "/compositions")

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
@common_counter
def runRNN():
    if request.method == 'POST':
        data = request.json['data']
        meter = request.json['meter']
        jwtToken = request.json['jwtToken']
        temperature = request.json['temperature']
        try:
            decodedToken = jwt.decode(jwtToken, SECRET_KEY, algorithms=["HS256"])
        except:
            return "JWT Token expired", 401
        subjectId = decodedToken['id']

        UserPath = USER_DIR + subjectId + "/generatedMelodies"
        response = runRnn(data, UserPath,meter,temperature)
        return Response(response, status=200)


@app.route('/runMusicat', methods=['POST'])
@common_counter
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
@common_counter
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
        pathToCompositions = USER_DIR + subjectId + "/compositions/"

        userCompositions = []
        for file in os.listdir(pathToCompositions):

            with open(pathToCompositions + file+"/compositionData.json") as tmpFile:
                jsonData = json.load(tmpFile)
                jsonData = json.loads(jsonData)

                userCompositions.append(jsonData)

        orig,flex,fluency = calculateCreativityScores(data,userCompositions) 

        cur.execute("SELECT * FROM compositions WHERE id=?",(composition_uuid,))
        row = cur.fetchone()
        while row is not None:
            composition_uuid = str(uuid.uuid4())
            cur.execute("SELECT * FROM compositions WHERE id=?",(composition_uuid,))
            row = cur.fetchone()
        os.mkdir(USER_DIR + subjectId + "/compositions/" + composition_uuid )
        os.mkdir(USER_DIR + subjectId + "/compositions/" + composition_uuid + "/musicatPNG")
        pathToImageDir = USER_DIR + subjectId + "/compositions/" + composition_uuid + "/musicatPNG/"
        jsonComposition = json.dumps(data)
        pathToComposition = USER_DIR + subjectId + "/compositions/" + composition_uuid + "/compositionData.json"


       
        with open(pathToComposition,'w') as f:
            json.dump(jsonComposition,f)
        now = datetime.datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    
        conn.execute("""INSERT INTO compositions (id,fk,filepath,pathToComposition,timestamp) VALUES( ?,?,?,?,?);""",
                     (composition_uuid, subjectId, pathToImageDir, pathToComposition, date_time))
        conn.commit()

        print(pathToImageDir)
        result = run(os.getcwd() + "/RhythmCat.exe", data, pathToImageDir)
        analogies = result["analogies"]
        groups = result["groups"]
        strengths = result["strengths"]
        
        totalResult, musicat = computeTotalResult(orig,flex,fluency,analogies,groups,data)
        response = {}
    
        
        score_uuid = str(uuid.uuid4())
        conn.execute("""INSERT INTO Scores (id,composition,fluency,flexability,originality,total,musicat)VALUES( ?,?,?,?,?,?,?);""",
                     (score_uuid, composition_uuid, fluency, flex, orig,totalResult,musicat))
        conn.commit()
        
        
        
        
        response['totalScore'] = totalResult
        
        with open(pathToImageDir+"out.png",'rb') as musicatImage:
            im_bytes = musicatImage.read()
        encoded = base64.b64encode(im_bytes).decode("utf8")
        response['musicatPNG'] = encoded


        # store values in db
        # store composition in db
        # run musicat and produce the png
        # return also the results from musicats computation
        response = json.dumps(response)
        return Response(response, status=200)


def computeTotalResult(orig,flex,fluency,analogies,groups,score):
    scoreLen = len(score)
    minAnalogies = scoreLen/2
    minGroups = scoreLen
    analogiesScore = len(analogies)/minAnalogies
    groupsScore = len(groups)/(minGroups-2)
    musicatScore = (analogiesScore+groupsScore)/2
    creativityScore = (orig+flex+fluency)/3
   
    return creativityScore, musicatScore




@app.route('/calculateCreativity', methods=['POST'])
def runCreativityScoring():
    if request.method == 'POST':
        conn = get_db_connection()

        jwtToken = request.json['jwtToken']
        #count = request.form['count']
        try:
            decodedToken = jwt.decode(jwtToken, SECRET_KEY, algorithms=["HS256"])
        except:
            return "JWT Token expired", 401
        subjectId = decodedToken['id']
        pathToCompositions = USER_DIR + subjectId + "/compositions/"
        
        userCompositions = []
        for file in os.listdir(pathToCompositions):
           
            with open(pathToCompositions + file+"/compositionData.json") as tmpFile:
                jsonData = json.load(tmpFile)
                jsonData = json.loads(jsonData)
                
                userCompositions.append(jsonData)

        
        
        # composition = request.form['composition']

        # result = run(os.getcwd()+"/RhythmCat.exe", composition)
        # conn.execute("INSERT INTO compositions (id,fk,filepath) VALUES( ?,?,?)", (composition_uuid, subjectId, midfilepath))
        # conn.commit()
        # conn.close()
        data = request.json['data']


        response = {}
        orig,flex,fluency = calculateCreativityScores(data,userCompositions)
        response['originality'] = orig
        response['flexability'] = flex
        response['fluency'] = fluency

        response = json.dumps(response)
        print(response)
        return Response(response, status=200)



metrics.register_default(
    common_counter
)
