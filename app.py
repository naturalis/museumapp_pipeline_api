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
available_languages = [ 'nl', 'en' ] 

queries = {
    "all" : '{{ "query": {{ "term" : {{ "language" : "{}" }}  }} }}',
    "key" : '{{ "query": {{ "term" : {{ "_key" : "{}" }}  }} }}',
    "favourites" : '{{ "query": {{ "exists": {{ "field": "favourites_rank" }} }} }}',
    "last_modified" : '{{ "query": {{ "term" : {{ "language" : "{}" }} }}, "size": 1, "sort": [ {{ "last_modified": {{ "order": "desc" }} }} ] }}',
    "rooms" : '{{ "size":"0", "aggs" : {{ "museum_rooms" : {{ "terms" : {{ "field" : "objects.location.keyword" }} }} }} }}',
    "by_room" : '{{ "query" : {{ "bool" : {{ "must": [{{ "match": {{ "objects.location.keyword": "{}" }} }}] }} }} }}'
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

        # es = Elasticsearch([{'host': os.getenv('ES_HOST'), 'port': os.getenv('ES_PORT')}],timeout=5)
        # es.info()
    except Exception as e:
        logger.error("missing elasticsearch variables: {}".format(str(e)))
        set_service_available(False)


def get_elasticsearch_pulse():
    global logger, es
    try:
        es = Elasticsearch([{'host': os.getenv('ES_HOST'), 'port': os.getenv('ES_PORT')}])
        es.info()
        set_service_available(True)
    except Exception as e:
        logger.error("elasticsearch unreachable: {}".format(str(e)))
        set_service_available(False)


def set_service_available(state):
   global service_available
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


class GetLastUpdated(Resource):
    @jwt_required()
    def get(self):
        global queries, available_languages
        try:
            query = ""

            args = parser.parse_args()
            language = args['language']
            if not language:
                language='nl'

            if not language in available_languages:
                raise ValueError("unknown language '{}'".format(language))

            query = queries["last_modified"].format(language)

            response = run_elastic_query(query,size=1,_source_includes="last_modified")
            reduced = process_response(response)
            log_usage(language=language)
            return { "last_update_date" : reduced["items"][0]["last_modified"] }
        except Exception as e:
            log_request_error(str(e))
            return { "error": str(e) }


class GetDocuments(Resource):
    @jwt_required()
    def get(self):
        global queries, available_languages
        try:
            args = parser.parse_args()
            key = args['key']
            language = args['language']
            room = args['room']

            if not language:
                language='nl'

            if not language in available_languages:
                raise ValueError("unknown language '{}'".format(language))

            query = ""

            if not key==None and not len(key)==0:
                query = queries["key"].format(key)
            elif not room==None and not len(room)==0:
                if room=="-":
                    room=""
                query = queries["by_room"].format(room)
            else:
                query = queries["all"].format(language)

            response = run_elastic_query(query,size=9999)
            reduced = process_response(response)
            log_usage(language=language,key=key,room=room,hits=len(reduced["items"]))
            return reduced
        except Exception as e:
            log_request_error(str(e),query)
            return {"error": str(e) }


class GetFavourites(Resource):
    @jwt_required()
    def get(self):
        global queries
        try:
            query = queries["favourites"].format()
            response = run_elastic_query(query,size=100,_source_includes="_key,favourites_rank")
            reduced = process_favourites_response(response)
            log_usage(hits=len(response))
            return reduced
        except Exception as e:
            log_request_error(str(e))
            return {"error": str(e) }


class GetRooms(Resource):
    @jwt_required()
    def get(self):
        global queries
        try:
            query = queries["rooms"].format()
            response = run_elastic_query(query)
            reduced = process_rooms_response(response)
            return reduced
        except Exception as e:
            log_request_error(str(e))
            return {"error": str(e) }


def run_elastic_query(query,**kwargs):
    global es, ES_INDEX
    return es.search(index=ES_INDEX,body=query,request_timeout=5,**kwargs)


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


def process_favourites_response(response):
    items=[]
    for item in response["hits"]["hits"]:
        items.append(item["_source"])

    return items


def process_rooms_response(response):
    items = {
        "items" : response["aggregations"]["museum_rooms"]["buckets"],
        "note" : "take note: 'doc_count' is the number of species with an object in the corresponding room, not the actual number of objects"
        }
    return items


def log_usage(language="",key="",room="",hits=""):
    global logger
    endpoint=request.path
    remote_addr=request.remote_addr
    logger.info("{remote_addr} - {endpoint} - {params} - {hits}"
        .format(remote_addr=remote_addr,endpoint=endpoint,params=json.dumps({"language":language,"key":key,"room":room}),hits=hits))


def log_request_error(error="unknown error"):
    global logger
    endpoint=request.path
    remote_addr=request.remote_addr
    logger.error("{remote_addr} - {endpoint} - {error}".format(remote_addr=remote_addr,endpoint=endpoint,error=error))


@app.before_request
def PreRequestHandler():
    get_elasticsearch_pulse()

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
parser.add_argument('key')
parser.add_argument('language')
parser.add_argument('room')

api.add_resource(RootRequest, '/')
api.add_resource(GetLastUpdated, '/last-updated')
api.add_resource(GetDocuments, '/documents')
api.add_resource(GetFavourites, '/favourites')
api.add_resource(GetRooms, '/rooms')


initialize(app)

if __name__ == '__main__':
    app.run(debug=(os.getenv('FLASK_DEBUG')=="1"),host='0.0.0.0')
