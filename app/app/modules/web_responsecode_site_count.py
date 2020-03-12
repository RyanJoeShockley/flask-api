from flask import request
from elasticsearch import Elasticsearch
from ssl import create_default_context
import json
import pytz
from datetime import datetime


def WEB_RESPONSECODE_SITE_COUNT(host, response, startingdate):

        WEBHOST = host
        WEBCODE = response
        WEBDATE = startingdate
        WEBDATE = WEBDATE.split('.')[0]
        WEBDATE = WEBDATE + '.000'
        print(host)

        CONTEXT = create_default_context(cafile="certs/certs.pem")
        INDEX = 'web-iis-*'

        CONN = Elasticsearch(
		        ['elastic-api.esolutionsgroup.ca'],
                http_auth=('Admin', 'Systemsteam'),
                scheme="https",
                port=8999,
                ssl_context=CONTEXT,
                timeout=60,
        )

        def searchagg(QUERY, INDEX):
            es = CONN
            MATCHES = es.search(index=INDEX, body=QUERY)
            print(MATCHES)
            #HITS = MATCHES['aggregations']['value_count']['value']
            print(HITS)
            #return(HITS)

        def searchid(QUERY, INDEX):
                es = CONN
                MATCHES = es.search(index=INDEX, body=QUERY)
                HITS = MATCHES['hits']['hits']
                for HIT in HITS:
                        yield (HIT['_source'])

        QUERY = {
                        "query":
                        {
                            "bool":
                            {
                                "must":
                                [
                                    {
                                        "term": 
                                        {
                                            "host": WEBHOST
                                        }
                                    },
                                    { 
                                        "term": 
                                        { 
                                            "response": WEBCODE
                                        }
                                    }
                                ],
                                "filter": 
                                {
                                    "range": 
                                    { 
                                        "timestamp": 
                                        { 
                                            "gte": WEBDATE
								        }
			                        }
		                        }
	                        } 
	                    }
                    }
        LIST = []
        count = CONN.count(index=INDEX, body=QUERY)
        COUNT = count['count']
        LIST.append({'requesting_useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'count':COUNT})
        
        data = {}
        data['data'] = LIST
        return data

def list_web_responsecode_site_count(host, response, startingdate):
        WEB_R = WEB_RESPONSECODE_SITE_COUNT(host, response, startingdate)
        return WEB_R