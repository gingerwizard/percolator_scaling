__author__ = 'dale'
import csv
import json
from optparse import OptionParser
output = open('queries.csv','w')
parser = OptionParser()
parser.add_option("-n", "--docs", dest="number_docs",help="number of documents")
(options, args) = parser.parse_args()
print "Converting %s"%options.number_docs
max_count=int(options.number_docs)
doc_count = 0
index="best_buy"
with open('train.csv', 'rb') as csvfile:
    train_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in train_reader:
        query = {"_type": ".percolator", "_index": index, "_op_type": "index", "_source": {"user": row[0], "category_id": row[2], "query": { "filtered": { "filter": {"bool": { "must": [{"term": {"category_id": row[2]}}]}},"query": {"multi_match": {"query": row[3],"fields": ["description", "name", "search_terms"]}}}}}}
        doc_count+=1
        if doc_count >1:
            output.write(json.dumps(query)+"\n")
        if doc_count == max_count:
            break;
output.close()
print "%s documents"%doc_count