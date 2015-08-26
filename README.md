# percolator_scaling

The following provides scripts and test files for performance testing Elasticsearch Percolator using a public Best Buy dataset and complements the blog post:  

[reference]

It is intended to assist with replication of tests and to demonstrate Percolator scaling properties only.  Queries have not been optimised and relevancy/recall of documents against queries not considered.  

Any use case here is hypothetical. It is assumed each Percolate query represents a users registered interest in a product category, with a set of search terms provided.  Documents are assumed to be new products being listed.  Documents are percolated against the queries thus indicating which users would theoretically be alerted about the product.  No alerting is performed by the tests, which simply percolate the documents sequentially using JMeter.

### Data Set and Scripts

Dataset can be downloaded from 

https://www.kaggle.com/c/acm-sf-chapter-hackathon-big/data

One file is utilised for Percolator testing:

- A training csv file (train.csv) containing approximately 1.8 million entries. Each line represents a user clicking on an item.  The information captured includes the item selected, its category and the search term used to locate the item.  

The above file can be converted into Percolator queries using the python (v2.7.x) script createQueries.py

python createQueries.py

This produces a file queries.csv. Optional parameter -n allows the number of queries output to be controlled e.g.

python createQueries.py -n 10000

###Percolator Queries

Example Percolator Query:
```
{
  "_index": "best_buy",
  "_type": ".percolator",
  "_id": "AU9lnTnrPssfQ9IP0sO2",
  "_score": 1,
  "_source": {
     "query": {
        "filtered": {
           "filter": {
              "bool": {
                 "must": [
                    {
                       "term": {
                          "category_id": "abcat0101001"
                       }
                    }
                 ]
              }
           },
           "query": {
              "multi_match": {
                 "query": "Televisiones Panasonic  50 pulgadas",
                 "fields": [
                    "description",
                    "name",
                    "search_terms"
                 ]
              }
           }
        }
     },
     "category_id": "abcat0101001",
     "user": "000000df17"
  }
```
The above query would be for user "000000df17", matching on any products in category "abcat0101001" with terms "Televisiones Panasonic  50 pulgadas".

###Indexing Percolator queries

indexQueries.py provided to assist indexing of Percolator queries.  This:

1. Creates an index "best_buy".  Caution: If the index already exists as it is deleted and re-added.
2. Applies the appropriate schema provided through settings.json. This allows you to the number of primary shards/replicas here through settings.json.
3. Indexes N queries from the file queries.csv in batches of X (default 10000).  Assumes Elasticsearch is running on localhost:9200.  Easily modified in script.
4. Performs a flush on completion of indexing and forces optimisation to a single shard.

Execute as follows:

python indexQueries.py -x <batch_size> -n <number_of_docs>

###Percolator Documents

Documents for percolation have been generated from the products.tar provided by Best Buy.  The following files provide documents for sample percolation, with each line representing a product:

1. docs_500.txt - 500 sample docs, with no filters.
2. docs_500_filtered.txt - 500 sample docs, with no filters.
3. docs_1000.txt - 1000 sample docs, with no filters.
4. docs_1000_filtered.txt - 500 sample docs, with no filters.

Example doc (without filter):

```
{
  "doc": {
    "description": "Compatible with select 1998-2008 Ford vehicles; connects an aftermarket radio to a vehicle's harness",
    "category_id": [
      "cat00000",
      "abcat0300000",
      "pcmcat165900050023",
      "pcmcat165900050031",
      "pcmcat165900050034"
    ],
    "search_terms": [
      "harness",
      "wiring",
      "ford",
      "radio"
    ],
    "name": "Metra - Wiring Harness for Select 1998-2008 Ford Vehicles - Multicolored",
    "id": "347137"
  },
  "size": 10
}

```

Example doc (with filter):

```
{
  "filter": {
    "bool": {
      "must": [
        {
          "terms": {
            "category_id": [
              "cat00000",
              "abcat0300000",
              "pcmcat165900050023",
              "pcmcat165900050031",
              "pcmcat165900050034"
            ]
          }
        }
      ]
    }
  },
  "doc": {
    "description": "Compatible with select 1998-2008 Ford vehicles; connects an aftermarket radio to a vehicle's harness",
    "category_id": [
      "cat00000",
      "abcat0300000",
      "pcmcat165900050023",
      "pcmcat165900050031",
      "pcmcat165900050034"
    ],
    "search_terms": [
      "harness",
      "wiring",
      "ford",
      "radio"
    ],
    "name": "Metra - Wiring Harness for Select 1998-2008 Ford Vehicles - Multicolored",
    "id": "347137"
  },
  "size": 10
}

```

Documents were selected from the first N products provided by Best Buy.  No attempt has been made to clean or optimise keywords/terms.  

For each percolated doc:

1. 10 matches are requested
2. search_terms have been added.  These represent the top 10 terms used to find the product by users and have been obtained from a terms agg on the indexed queries.  These have been added to ensure every document matches a percolation query.

###Running Tests with JMeter

For the purposes of testing performance, Documents can be percolated using the simple provided Jmeter test 'PercolatorTest.jmx'.  This simple test executes queries sequentially in a single thread with no delay.  No attempt is made to verify responses are correct, although users can view results through the "View Results in Tree" component.  A Summary Report allows users to view statistics e.g. avg response time.

####Settings

1. Docs to be used for percolate tests.  Assumes structure of one percolate doc per line in the format highlighted above.  The file read can be changed through the CSV datasource "PercolateQueriesReader" i.e.

![Changing Percolate Document File](link)

2. Percolate endpoint. Assumed to be /best_buy/.percolator/_percolate.  If you have you used the indexing script this shouldn't need changing.  If required change via the HTTP request:

![Changing Percolate Endpoint](link)

3. Host and port.  Assumed to be localhost:9200. Changed via the HTTP request

![Changing Percolate Host:Port](https://raw.githubusercontent.com/gingerwizard/percolator_scaling/master/Setting_Host_Port.png)

4. Changing Number of Percolate Samples.  Set to 500 by default. Consider changing if using the larger 1000 sample files. Changed via the Percolate Thread Group:

![Changing Percolate Thread Group](link)

###Blog Tests

All of above was used for the purposes of testing the scaling properties of Percolator. Details can be found:

[reference]

The following was repeated for the docs_500.txt and docs_500_filtered.txt. Initially, N was set to 100,000.

1. Indexing N documents using the indexQueries.py script provided. 
2. 500 queries replayed against the index and statistics recorded e.g. avg query response time.
3. Increase N by 100,000 and repeat.

The above was repeated 10 times for a maxumum test size of 1 million queries.

Further details on the test environment:

1. 10 matches per document percolation requested. This still requires complete evaluation of all documents on each shard to provide a total hits count.  However, results are not skewed by increased response sizes.
2. MacBook Pro, 3.0GHz Dual Core i7, 16GB RAM, 500GB Solid State Drive
3. 8GB heap space for Elasticsearch i.e. -Xmx12g -Xms12g
4. mlock enabled
5. 500 documents replayed sequentially using Jmeter. Single thread with no delay.  JMeter v 1.0. File provided above.
6. Between each test the index was deleted via the indexQueries.py script, thus clearing in memory percolator cache correctly.
7. Force an optimise to a single segment after indexing each batch.




