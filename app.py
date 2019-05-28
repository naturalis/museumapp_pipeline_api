from flask import Flask
from flask_restful import Resource, Api, reqparse, request
from flask_jwt import JWT, jwt_required
import logging, os, json
from datetime import datetime
from elasticsearch import Elasticsearch

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_KEY')
api = Api(app, prefix="/api")

USERS = []
ES_INDEX = None

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

def initialize_logger(log_dir="./",log_level=logging.INFO,log_to_stdout=True):
    global logger
    logger=logging.getLogger("MuseumApp API")
    logger.setLevel(log_level)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler(os.getenv('LOGFILE_PATH'))
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    if log_to_stdout:
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

def initialize_users():
    global USERS, logger
    if (os.getenv('API_USER')==None):
        logger.error("API_USER missing from ENV")
        set_service_available(False)
    if (os.getenv('API_PASS')==None):
        logger.error("API_PASS missing from ENV")
        set_service_available(False)
    if (os.getenv('API_USERID')==None):
        logger.error("API_USERID missing from ENV")
        set_service_available(False)
    else:
        USERS.append({ "username" : os.getenv('API_USER'), "password" : os.getenv('API_PASS'), "userid" : os.getenv('API_USERID')})

def initialize_elasticsearch():
    global es, ES_INDEX, logger
    try:
        if (os.getenv('ES_PORT')==None):
            logger.error("ES_PORT missing from ENV")
            set_service_available(False)
        if (os.getenv('ES_HOST')==None):
            logger.error("ES_HOST missing from ENV")
            set_service_available(False)
        if (os.getenv('ES_INDEX')==None):
            logger.error("ES_INDEX missing from ENV")
            set_service_available(False)
        else:
            ES_INDEX = os.getenv('ES_INDEX')

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
        return { "you've stumbled upon" : "naturalis museumapp pipeline api" }


class GetUnitIds(Resource):
#    @jwt_required()
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
#    @jwt_required()
    def get(self):
        global queries
        try:
            args = parser.parse_args()
            date = args['from']
            doc_id = args['id']

            if not doc_id==None:
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


def process_response(response):
    hits=[]
    for item in response["hits"]["hits"]:
        hits.append(item["_source"])
    return hits


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
    if get_service_available() == False:
        log_request_error("service unavailable")
        return '{ "error": "service unavailable" }'


@app.errorhandler(404)
def page_not_found(e):
    return '{{ "error": "{}" }}'.format(e), 404


jwt = JWT(app, verify, identity)

parser = reqparse.RequestParser()
parser.add_argument('from')
parser.add_argument('id')

api.add_resource(RootRequest, '/')
api.add_resource(GetUnitIds, '/ids')
api.add_resource(GetDocuments, '/documents')

initialize(app)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')


# TODO
# - error handlers for codes other than 404

