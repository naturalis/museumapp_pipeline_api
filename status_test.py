import urllib.request
import json

fp = urllib.request.urlopen("http://elastic:9200/api_control/_search")
mybytes = fp.read()

mystr = mybytes.decode("utf8")
fp.close()

print(json.loads(mystr)["hits"]["hits"][0]["_source"]["status"])
