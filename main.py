# Here Used Pivotal Cloud Foundry to deploy the changes.

import json # To form a JSON data
from errno import errorcode # To handle Error Code
import mysql.connector # Python - MySQL Connection
import pymongo # Python - MongoDB Connection
from flask import Flask # A simple framework for building complex web applications, Flask is a lightweight WSGI web application framework.
from flask_restful import Resource, Api, reqparse # flask_restful = Simple framework for creating REST APIs
# reqparse = Enables adding and parsing of multiple arguments in the context of a single request.
# api = The main entry point for the application. You need to initialize it with a Flask Application.
import requests # Requests allows you to send HTTP requests.
import time # Used to select time

# Start : Pivotal cloud setup ---------------------
from cfenv import AppEnv # Python wrapper for Cloud Foundry environments, This is a tiny utility that simplifies interactions with Cloud Foundry environment variables.
env = AppEnv() # Setting Cloud Foundry environment.
port = env.port # Setting Cloud Foundry environment port.
# End : Pivotal cloud setup -----------------------

app = Flask(__name__) # Flask app attribute
api = Api(app) # The main entry point for the application. You need to initialize it with a Flask Application.

# Start : Handling cross origin -------------------
from flask_cors import CORS # A Flask extension for handling Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible.
CORS(app) #
# End : Handling cross origin ---------------------

# Start POST(Insert) Service to Consume other service ------------------
class PostConsumeservice(Resource):
    def post(self): # POST is Method
        parser = reqparse.RequestParser() # Enables adding and parsing of multiple arguments in the context of a single request
        parser.add_argument('username', type=str) # add_argument = Adds an argument to be parsed.
        args = parser.parse_args() # Parse all arguments from the provided request and return the results as a Namespace
        username = str(args['username']) # Assign the retrieved value to variable
        print("User name received from Kloudee : ", username)

        t = time.time() # Current Time
        res = consumeservice(username) # call the method which has consumed POST Service
        print("Total Time Taken : ", time.time() - t)

        return res # return value

# Below method is created to consume other service of POST method.
def consumeservice(username):
    try:
        transdata = {'Content-type': 'application/json',"username" : username}
        res = requests.post("botfwurl", params=transdata) # Here we can use GET PUT DELETE
        data_json = json.loads(res.content)

        if res.status_code == 200:
            print("Data retrieved from Framework = ", data_json)
            # When Data Found in Consumed Service proceed for Data Insertion
            retdta = updinfo(username,data_json)
            print(retdta)
            return {"status": 200, "message": "Success Data Found", "data": data_json}
        else:
            print("Data did not retrieve from Framework = ", res.content)
            return {"status": 404, "message": "NO Data Found"}

    except errorcode as e:
        print("Something went wrong")
        return {"message": "Something went wrong %s" % e, "status": 500}

# Below method is created to Insert Data into Mongo Collection
def updinfo(username,data_json):
    try:
        # Connect Host
        client = pymongo.MongoClient("MongoDB Credentails") # Connect MongoDB
        # ticketingUAT = "mongodb://USERNAME:PASSWORD@IP:PORT/?authSource=DATABASE"
        mydb = client["Mongo Database"] # Database is set of Collections
        collectionObject = mydb["Mongo Collection"] # Collection is set of Documents
        # Document is set of Key-Value pairs
        infocnt = collectionObject.find({"username":username.upper()}).count()
        if infocnt != 0:
            collectionObject.update_one({"username": username.upper()}, {"$set": {"complete_name": 'Python Developer'}})
            # disconnect from server
            client.close()
            return {"status": 200, "message": "Success Updated"}
        else:
            data_json["_id"] = username
            collectionObject.insert_one(data_json)
            # disconnect from server
            client.close()
            return {"status": 200, "message": "Success Inserted"}

    # except pymongo.errors.ConnectionFailure as e:
    except pymongo.errors.OperationFailure as e:
        print("Could not connect to Mongo DB")
        return {"displaymessage": "Internal server error due to - %s" % e, "status": 500}
# End POST(Insert) Service to Consume other service ------------------


# Start Rest API using GET Method --------------------------------------
class Restgetservice(Resource):
    def get(self): # here we can use GET method also
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        args = parser.parse_args()
        username = str(args['username'])
        print("User name received from Kloudee : ", username)
        t = time.time()
        username = "OmkarJ"
        res = getinfo(username)
        print("Total Time Taken with List Comprehension : ", time.time() - t)
        return res

def getinfo(username):
    try:
        # Connect Host
        client = pymongo.MongoClient("MongoDB Credentials") # Connect MongoDB
        # ticketingUAT = "mongodb://USERNAME:PASSWORD@IP:PORT/?authSource=DATABASE"
        mydb = client["Mongo Database"] # Database is set of Collections
        collectionObject = mydb["Mongo Collection"] # Collection is set of Documents
        # Document is set of Key-Value pairs
        cinfo = [doc for doc in collectionObject.find({"$or":[{"username":username.upper()},{"emp_id":username}]}, {"allocation_end_date": 1,"allocation_start_date":1,"grade_text":1,"_id":0})]
        data = json.dumps(cinfo, default=str)
        data = json.loads(data)
        # dumps() = encoding to JSON objects
        # dump() = encoded string writing on file
        # loads() = Decode the JSON string
        # load() = Decode while JSON file read

        # disconnect from server
        client.close()
        return data

    # except pymongo.errors.ConnectionFailure as e:
    except pymongo.errors.OperationFailure as e:
        print("Could not connect to Mongo DB")
        return {"displaymessage": "Internal server error due to - %s" % e, "status": 500}
# End Rest API using GET Method ------------------


# Start Rest API using PUT Method MYSQL------------------
class Putsqlservice(Resource):
    def put(self): # here we can use GET method also
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        args = parser.parse_args()
        username = str(args['username'])
        print("User name received from Kloudee : ", username)
        t = time.time()
        username = "OmkarJ"
        res = sqlselupd(username)
        print("Total Time Taken with List Comprehension : ", time.time() - t)
        return res

def sqlselupd(username):
    try:
        db = mysql.connector.connect("MySQL DB Credentials")
        cursor = db.cursor()
        sql = " SELECT * FROM employee_info WHERE username = '%s' " % username.lower()
        cursor.execute(sql)
        row = cursor.fetchall()
        if cursor.rowcount >= 1:
            print(" Data Found")
            for i in row:
                print("Record : ",i)
        else:
            print(" No Data Found")

        sql1 = " UPDATE employee_info SET designation = 'Python Developer' WHERE username = '%s' " % username.lower()
        # Here we can have Insert and Update Query as well.
        cursor.execute(sql1)
        db.commit()
        db.close()
        cursor.close()

        return {"status": 200, "message": "Successss"}

    except mysql.connector.Error as err:
        print("Could not connect to MySQL DB")
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print( "status : 400, message : Something is wrong with your user name or password" )
            return {"status": 400, "message": "Something is wrong with your user name or password"}
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print ("status : 400, message : Database does not exist")
            return {"status": 400, "message": "Database does not exist"}
        else:
            print ("status : 400, message :", err)
            return {"status": 400, "message": err}
# End Rest API using PUT Method MYSQL------------------


api.add_resource(PostConsumeservice, '/postconsumeservice') # Adds a resource to the API with Class, left side element is Class, Right side is Resource.
api.add_resource(Restgetservice, '/restgetservice') # Adds a resource to the API with Class, left side element is Class, Right side is Resource.
api.add_resource(Putsqlservice, '/putsqlservice') # Adds a resource to the API with Class, left side element is Class, Right side is Resource.


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    # if you dont specify port it will take 5000 as default
    # if you dont specify host it will take 127.0.0.1 as default