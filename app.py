from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse, request
from flask_jwt import JWT, jwt_required
from datetime import datetime
from elasticsearch import Elasticsearch
import logging, os, json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_KEY')
app.config['PROPAGATE_EXCEPTIONS'] = True
api = Api(app, prefix="/api")

USERS = []
ES_INDEX = None
ES_CONTROL_INDEX = None

service_available = True
logger = None

queries = {
    "all" : '{}',
    "date_range" : '{{ "query": {{ "range" : {{ "created" : {{ "gte" : "{}" }} }} }} }}',
    "doc_id" : '{{ "query": {{ "match" : {{ "id" : {} }} }} }}'
}

def initialize(app):
    initialize_logger()
    initialize_users()
    initialize_elasticsearch()

def initialize_logger(log_level=logging.INFO):
    global logger

    if os.getenv('DEBUGGING')=="1":
        log_level=logging.DEBUG

    logger=logging.getLogger("API")
    logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler(os.getenv('LOGFILE_PATH'))
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    if os.getenv('DEBUGGING')=="1":
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

def initialize_users():
    global USERS, logger

    for item in [ 'API_USER', 'API_PASS', 'API_USERID' ]:
        if (os.getenv(item)==None):
            logger.error("{} missing from ENV".format(item))
            set_service_available(False)

    if get_service_available() == True:
        USERS.append({
            "username" : os.getenv('API_USER'),
            "password" : os.getenv('API_PASS'),
            "userid" : os.getenv('API_USERID')
        })


def initialize_elasticsearch():
    global logger, es, ES_INDEX, ES_CONTROL_INDEX
    try:
        for item in [ 'ES_PORT', 'ES_HOST', 'ES_INDEX', 'ES_CONTROL_INDEX' ]:
            if (os.getenv(item)==None):
                logger.error("{} missing from ENV".format(item))
                set_service_available(False)

        if get_service_available() == True:
            ES_INDEX = os.getenv('ES_INDEX')
            ES_CONTROL_INDEX = os.getenv('ES_CONTROL_INDEX')

        es = Elasticsearch([{'host': os.getenv('ES_HOST'), 'port': os.getenv('ES_PORT')}])
        es.info()
    except Exception as e:
        logger.error("elasticsearch unreachable: {}".format(str(e)))
        set_service_available(False)



def set_service_available(state):
   global service_available
   if service_available == True:
        service_available = state

def get_service_available():
   global service_available
   return service_available



class User(object):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "User(id='%s')" % self.id

def verify(username, password):
    global USERS

    if not (username and password):
        return False

    for index, user in enumerate(USERS):
        if user['username'] == username and user['password'] == password:
            return User(id=user['userid'])

def identity(payload):
    user_id = payload['identity']
    return {"user_id": user_id}



class RootRequest(Resource):
    def get(self):
        return { "naturalis museumapp pipeline api" : "v1.0" }


@consumes('application/json', 'text/html')
class GetDocumentIds(Resource):
    @jwt_required()
    def get(self):
        global queries
        try:
            args = parser.parse_args()
            date = args['from']
            if date==None:
                query = queries["all"]
            else:
                datetime_object = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                query = queries["date_range"].format(datetime_object)
            response = run_elastic_query(query,_source_includes="id,created")
            reduced = process_response(response)
            log_usage(query=query,hits=len(reduced))
            return reduced
        except Exception as e:
            log_request_error(str(e))
            return {"error": str(e) }


class GetDocuments(Resource):
    @jwt_required()
    def get(self):
        global queries
        try:
            args = parser.parse_args()
            date = args['from']
            doc_id = args['id']

            if not doc_id==None and not len(doc_id)==0:
                doc_id = json.dumps(doc_id)
                query = queries["doc_id"].format(doc_id)
            elif date==None:
                query = queries["all"]
            else:
                datetime_object = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                query = queries["date_range"].format(datetime_object)

            response = run_elastic_query(query)
            reduced = process_response(response)
            log_usage(query=query,hits=len(reduced))
            return reduced
        except Exception as e:
            log_request_error(str(e))
            return {"error": str(e) }


def run_elastic_query(query,**kwargs):
    global es, ES_INDEX
    return es.search(index=ES_INDEX,body=query,**kwargs)


def get_documents_status():
    global es, ES_CONTROL_INDEX
    response = es.search(index=ES_CONTROL_INDEX,body='{}')
    try:
        documents_status=response["hits"]["hits"][0]["_source"]["status"]
    except Exception as e:
        log_request_error("document status unavailable (defaulting to 'ready')")
        documents_status="ready"
    return documents_status


def process_response(response):
    items=[]
    for item in response["hits"]["hits"]:
        items.append(item["_source"])

    return { "size" : len(items), "items" : items }


def log_usage(query,hits):
    global logger
    endpoint=request.path
    logger.info(json.dumps({ "endpoint" : endpoint, "query" : query, "hits" : hits }))

def log_request_error(error):
    global logger
    endpoint=request.path
    logger.error(json.dumps({ "endpoint" : endpoint, "error" : error }))


@app.before_request
def PreRequestHandler():
    if not get_documents_status() == "ready":
        return jsonify({ "error": "document store busy" })

    if get_service_available() == False:
        log_request_error("service unavailable")
        return jsonify({ "error": "service unavailable" })


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({ "error" : e.description }), 404


jwt = JWT(app, verify, identity)

@jwt.jwt_error_handler
def customized_error_handler(e):
    # print(e.error)
    # print(e.description)
    # print(e.status_code)
    return jsonify({ "error" : e.error }), e.status_code


parser = reqparse.RequestParser()
parser.add_argument('from')
parser.add_argument('id')

api.add_resource(RootRequest, '/')
api.add_resource(GetDocumentIds, '/ids')
api.add_resource(GetDocuments, '/documents')

initialize(app)

if __name__ == '__main__':
    app.run(debug=(os.getenv('FLASK_DEBUG')=="1"),host='0.0.0.0')
