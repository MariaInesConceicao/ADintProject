import requests
from os import abort


print("Connecting to Server...")
try:
    requests.get('http://localhost:8000/getcode/1')
    print("Please type the code in the Gate")
except:
    abort("Invalid Link")
