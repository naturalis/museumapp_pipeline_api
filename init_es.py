import os, json
from elasticsearch import Elasticsearch

class elasticsearch_init:
    es_host = None
    es_port = None
    es = None
    index_name = None

    def init(self):
        if (os.getenv('ES_HOST')==None):
            raise ValueError('ES_HOST not set in ENV')
        else:
            self.es_host=os.getenv('ES_HOST')

        if (os.getenv('ES_PORT')==None):
            raise ValueError('ES_PORT not set in ENV')
        else:
            self.es_port=os.getenv('ES_PORT')

        self.es = Elasticsearch([{'host': self.es_host, 'port': self.es_port}])
        print("initialized")

 
    def set_index_name(self,name):
        self.index_name = name

 
    def check_availability(self):
        self.es.info()
        print("elasticsearch available")

 
    def delete_index(self):
        result = self.es.indices.delete(index=self.index_name)
        print(result)
        print("index deleted")


    def create_index_from_file(self, mapping_file):
        print("creating index")
        try:
            with open(mapping_file, 'r') as file:
                body = file.read().replace('\n', ' ')

            result = self.es.indices.create(index=self.index_name,body=body)
            print(result)
            print("index created")
        except Exception as e:
            print(e)


    def load_documents_from_folder(self, folder):
        loaded = 0
        failed = 0
        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                print("loading {}".format(filename))
                f = open(os.path.join(folder,filename))
                doc = json.loads(f.read())
                result = self.es.index(index=self.index_name, id=doc["id"], body=doc, op_type='create')
                print(result)
                # d = json.loads(result)


if __name__ == '__main__':
    e = elasticsearch_init()
    e.init()
    e.set_index_name('museumapp')
    e.check_availability()
    e.delete_index()
    e.create_index_from_file('es_mapping.json')
    e.load_documents_from_folder('./documents')

