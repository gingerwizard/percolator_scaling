__author__ = 'dale'
from elasticsearch import Elasticsearch,helpers
import json
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-x", "--batch_size", dest="batch_size",
                  help="index batch size",default=10000)
parser.add_option("-n", "--number_docs",
                    dest="number_docs", help="number of docs to index")
(options, args) = parser.parse_args()
number_docs=int(options.number_docs)
batch_size=int(options.batch_size)
input_file = "./best_buy/queries.csv"
settings_path="./best_buy/settings.json"
index="best_buy"
es=Elasticsearch("localhost:9200",timeout=600)
with open(settings_path,"r") as settings_file:
    settings = json.loads(settings_file.read())
es.indices.delete(index=index, ignore=[400, 404])
es.indices.create(index=index, body=settings)

docs=[]
queries = open(input_file,"r");
query = queries.readline()
total=0
while query:
    docs.append(json.loads(query))
    total=total+1
    if len(docs) == batch_size or total == number_docs:
        print "Indexing %s batch for total of %s"%(batch_size,total)
        helpers.bulk(es, docs)
        docs=[]
        if total == number_docs:
            break;
    query = queries.readline()
if (len(docs) > 0):
    print "Indexing %s batch for total of %s"%(len(docs),total)
    helpers.bulk(es, docs)
queries.close()
es.indices.flush(index="_all")
es.indices.optimize(index=index,max_num_segments=1,wait_for_merge=True)
print "Indexed %s"%total
