import os, json, sys, logging, datetime
from elasticsearch import Elasticsearch

class elasticsearch_access:
    es_host = None
    es_port = None
    es = None
    index_name = None
    logfile_path = None
    logger = None

    def initialize(self):

        if (os.getenv('ES_HOST')==None):
            raise ValueError('ES_HOST not set in ENV')
        else:
            self.es_host=os.getenv('ES_HOST')

        if (os.getenv('ES_PORT')==None):
            raise ValueError('ES_PORT not set in ENV')
        else:
            self.es_port=os.getenv('ES_PORT')

        if (os.getenv('LOGFILE_PATH')==None):
            raise ValueError('LOGFILE_PATH not set in ENV')
        else:
            self.logfile_path=os.getenv('LOGFILE_PATH')

        self.es = Elasticsearch([{'host': self.es_host, 'port': self.es_port}])


    def initialize_logger(self,log_dir="./",log_level=logging.INFO,log_to_stdout=True):
        self.logger=logging.getLogger("loader")
        self.logger.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        fh = logging.FileHandler(self.logfile_path)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        if log_to_stdout:
            ch = logging.StreamHandler()
            ch.setLevel(log_level)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

 
    def set_index_name(self,name):
        self.index_name = name

 
    def check_availability(self):
        try:
            self.es.info()
            self.logger.info("elasticsearch available")
        except:
            self.logger.error("elasticsearch unavailable")

 
    def delete_index(self):
        try:
            result = self.es.indices.delete(index=self.index_name)
            self.logger.info(json.dumps(result))
        except Exception as e:
            self.logger.error(e)


    def create_index_from_file(self,mapping_file):
        try:
            with open(mapping_file, 'r') as file:
                body = file.read().replace('\n', ' ')

            result = self.es.indices.create(index=self.index_name,body=body)
            self.logger.info(json.dumps(result))
        except Exception as e:
            self.logger.error(e)


    def load_documents_from_folder(self,folder):
        loaded = 0
        failed = 0
        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                f = open(os.path.join(folder,filename))
                doc = json.loads(f.read())
                try:
                    result = self.es.index(index=self.index_name, id=doc["id"], body=doc, op_type='create')
                    self.logger.info("loaded {}".format(filename))
                    loaded += 1
                except Exception as e:
                    self.logger.error("error loading {}: {})".format(filename,e))
                    failed += 1


    def delete_document_by_id(self,doc_id):
        result = self.es.delete(index=self.index_name, id=doc_id, refresh=True)
        self.logger.info(json.dumps(result))


    def delete_documents_by_query(self,query='{"query":{"match_all": {} } }'):
        result = self.es.delete_by_query(index=self.index_name, body=query, refresh=True)
        self.logger.info(json.dumps(result))


    def set_documents_status(self,state):
        doc = '{{  "status": "{}", "created":  "{}" }}'

        if state in [ "busy", "ready" ]:
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query = doc.format(state, date)
            result = self.es.index(index=self.index_name, id="1", body=query)
            self.logger.info("set documents state '{}'".format(state))


if __name__ == '__main__':
    e = elasticsearch_access()
    e.initialize()
    e.initialize_logger()
    
    if (os.getenv('ES_INDEX')==None):
        e.logger.error("ES_INDEX missing from ENV")
    else:
        e.set_index_name(os.getenv('ES_INDEX'))

    e.check_availability()

    if not os.getenv('ES_CONTROL_COMMAND')==None:
        ES_CONTROL_COMMAND=os.getenv('ES_CONTROL_COMMAND')
    else:
        ES_CONTROL_COMMAND=None

    if not os.getenv('ES_CONTROL_ARGUMENT')==None:
        ES_CONTROL_ARGUMENT=os.getenv('ES_CONTROL_ARGUMENT')
    else:
        ES_CONTROL_ARGUMENT=None

    if ES_CONTROL_COMMAND=='create_index' and not ES_CONTROL_ARGUMENT==None:
        e.create_index_from_file(ES_CONTROL_ARGUMENT)
    elif ES_CONTROL_COMMAND=='delete_index':
        e.delete_index()
    elif ES_CONTROL_COMMAND=='load_documents' and not ES_CONTROL_ARGUMENT==None:
        e.load_documents_from_folder(ES_CONTROL_ARGUMENT)
    elif ES_CONTROL_COMMAND=='delete_document' and not ES_CONTROL_ARGUMENT==None:
        e.delete_document_by_id(ES_CONTROL_ARGUMENT)
    elif ES_CONTROL_COMMAND=='delete_documents':
        e.delete_documents_by_query()
    elif ES_CONTROL_COMMAND=='set_documents_status' and not ES_CONTROL_ARGUMENT==None:
        if (os.getenv('ES_CONTROL_INDEX')==None):
            e.logger.error("ES_CONTROL_INDEX missing from ENV")
        else:
            e.set_index_name(os.getenv('ES_CONTROL_INDEX'))
            e.set_documents_status(ES_CONTROL_ARGUMENT)
