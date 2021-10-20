import json, requests
from os import abort
from flask import Flask, request, jsonify, make_response
from gatedata import isCodeCorrect, insertCode, code_generator, deleteOldCode

app = Flask(__name__)

#@app.route('/', methods=['GET'])
#def query_records():
#    name = request.args.get('name')
#    print name
#    with open('/tmp/data.txt', 'r') as f:
#        data = f.read()
#        records = json.loads(data)
#        for record in records:
#            if record['name'] == name:
#                return jsonify(record)
#        return jsonify({'error': 'data not found'})





@app.route('/updatecode/<user>', methods=['GET'])
def updateUserCode(user):
    if request.method == 'GET':
        #Delete previous code in db
        deleteOldCode(user)
        
        #Create code for gate
        code = code_generator()
        #Inser new code in db
        insertCode(code, user)
        
        #place code in db
        return code
    else:
        abort(400) #BadRequest

@app.route('/usercode/<code>/<user>', methods=['GET'])
def validateUserCode(code, user):
    if request.method == 'GET':
        
        #teste=isCodeExpired(code, user)
        #print(teste)
        return isCodeCorrect(code, user)
    else:
        abort(404)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)