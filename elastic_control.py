import os, json, sys, logging, datetime
from elasticsearch import Elasticsearch

class elasticsearch_control:

    debug = False
    es_host = None
    es_port = None
    es = None
    index_name = None
    control_index_name = None
    logfile_path = None
    logger = None
    control_command = None
    control_argument = None

    def initialize(self):
        self.set_debug(os.getenv('DEBUGGING')=="1")

        for item in [ "ES_INDEX", "ES_CONTROL_INDEX", "ES_HOST", "ES_PORT", "LOGFILE_PATH" ]:
            if (os.getenv(item)==None):
                raise ValueError("'{}' not set in ENV".format(item))

        self.initialize_logger(log_level=logging.DEBUG if self.get_debug() else logging.INFO)
        self.initialize_elastic()


    def initialize_logger(self,log_level=logging.INFO):
        self.logger=logging.getLogger("loader")
        self.logger.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        fh = logging.FileHandler(os.getenv('LOGFILE_PATH'))
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        if self.get_debug():
            ch = logging.StreamHandler()
            ch.setLevel(log_level)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
 

    def initialize_elastic(self):
        self.es_host=os.getenv('ES_HOST')
        self.es_port=os.getenv('ES_PORT')
        self.index_name = os.getenv('ES_INDEX')
        self.control_index_name = os.getenv('ES_CONTROL_INDEX')
        self.es = Elasticsearch([{'host': self.es_host, 'port': self.es_port}])

        self.logger.debug("elastic host: {}".format(self.es_host))
        self.logger.debug("elastic port: {}".format(self.es_port))
        self.logger.debug("elastic index: {}".format(self.index_name))
        self.logger.debug("elastic control index: {}".format(self.control_index_name))
 

    def set_debug(self,state):
        self.debug=state


    def get_debug(self):
        return self.debug


    def check_availability(self):
        try:
            self.es.info()
            self.logger.info("elasticsearch available")
        except:
            self.logger.error("elasticsearch unavailable")


    def delete_index(self,index):
        try:
            result = self.es.indices.delete(index=index)
            self.logger.info(json.dumps(result))
        except Exception as e:
            self.logger.error(e)


    def create_index_from_file(self,mapping_file,index):
        try:
            with open(mapping_file, 'r') as file:
                # doc = file.read().replace('\n', ' ')
                doc = json.loads(file.read())

            result = self.es.indices.create(index=index, body=doc)
            self.logger.info(json.dumps(result))
        except Exception as e:
            self.logger.error(e)


    def load_documents_from_folder(self,folder):
        loaded = 0
        failed = 0
        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                file = open(os.path.join(folder,filename))
                doc = json.loads(file.read())
                try:
                    result = self.es.index(index=self.index_name, id=doc["id"], body=doc, op_type='create')
                    self.logger.info("loaded: {}".format(filename))
                    loaded += 1
                except Exception as e:
                    self.logger.error("error loading: {} ({})".format(filename,e))
                    failed += 1

        self.logger.info("finished loading: {}; successful {}, failed {}".format(folder,loaded,failed))


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
            result = self.es.index(index=self.control_index_name, id="1", body=query)
            self.logger.info("set documents state: {}".format(state))
        else:
            self.logger.warning("unknown state: {}".format(state))


    def set_control_command(self,command):
        if command == None:
            return

        if command in [ "create_index", "delete_index", "create_control_index", "delete_control_index", "load_documents", 
                        "delete_document", "delete_documents", "set_documents_status" ]:
            self.control_command = command
        else:
            self.logger.warning("unknown control command: {}".format(command))


    def set_control_argument(self,argument):
        self.control_argument = argument


    def run_control_command(self):
        if self.control_command=='create_index' and not self.control_argument==None:
            if not os.path.exists(self.control_argument):
                self.logger.warning("file doesn't exist: {}".format(self.control_argument))
            else:
                self.logger.info("creating index from file: {}".format(self.control_argument))
                self.create_index_from_file(self.control_argument,index=self.index_name)
            return

        if self.control_command=='delete_index':
            self.logger.info("deleting index")
            self.delete_index(index=self.index_name)
            return

        if self.control_command=='create_control_index' and not self.control_argument==None:
            if not os.path.exists(self.control_argument):
                self.logger.warning("file doesn't exist: {}".format(self.control_argument))
            else:
                self.logger.info("creating control index from file: {}".format(self.control_argument))
                self.create_index_from_file(self.control_argument,index=self.control_index_name)
            return

        if self.control_command=='delete_control_index':
            self.logger.info("deleting control index")
            self.delete_index(index=self.control_index_name)
            return

        if self.control_command=='load_documents' and not self.control_argument==None:
            if not os.path.exists(self.control_argument):
                self.logger.warning("folder doesn't exist: {}".format(self.control_argument))
            else:
                self.logger.info("loading documents from folder: {}".format(self.control_argument))
                self.load_documents_from_folder(self.control_argument)
            return

        if self.control_command=='delete_documents':
            self.logger.info("deleting all documents")
            self.delete_documents_by_query()
            return

        if self.control_command=='delete_document' and not self.control_argument==None:
            self.logger.info("delete document by id: {}".format(self.control_argument))
            self.delete_document_by_id(self.control_argument)
            return

        if self.control_command=='set_documents_status' and not self.control_argument==None:
            self.set_documents_status(self.control_argument)
            return


if __name__ == '__main__':

    e = elasticsearch_control()
    e.initialize()
    e.check_availability()
    e.set_control_command(os.getenv('ES_CONTROL_COMMAND') if not os.getenv('ES_CONTROL_COMMAND')==None else None)
    e.set_control_argument(os.getenv('ES_CONTROL_ARGUMENT') if not os.getenv('ES_CONTROL_ARGUMENT')==None else None)
    e.run_control_command()
