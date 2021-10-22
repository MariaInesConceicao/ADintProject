import requests
from os import abort


print("Connecting to Server...")
try:
    r=requests.get('http://localhost:8000/getcode/1')
    try:
        text = r.json()
    except:
        abort(400)
    print("Code received")
    print("<<<", text, ">>>")
    print("Please type the code in the Gate")
except:
    abort("Invalid Link")
