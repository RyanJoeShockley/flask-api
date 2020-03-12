from flask import request
from elasticsearch import Elasticsearch
from ssl import create_default_context
import json
import pytz
from datetime import datetime


def WEB_RESPONSECODE_SERVER(servername, response, num, startingdate):

        WEBSERVER = servername
        WEBCODE = response
        WEBNUM = num
        WEBDATE = startingdate
        WEBDATE = WEBDATE.split('.')[0]
        WEBDATE = WEBDATE + '.000'

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
            HITS = MATCHES['aggregations']['value_count']['value']
            return(HITS)

        def searchid(QUERY, INDEX):
                es = CONN
                MATCHES = es.search(index=INDEX, body=QUERY)
                HITS = MATCHES['hits']['hits']
                for HIT in HITS:
                        yield (HIT['_source'])

        QUERY = {
                "size" : WEBNUM,
                "sort" : [{"timestamp" : {"order" : "desc"}}],
                        "query":
                        {
                            "bool":
                            {
                                "must":
                                [
                                    {
                                        "term": 
                                        {
                                            "servername": WEBSERVER
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
        results = searchid(QUERY,INDEX)
        for r in results:
                print(r)
                TIMESTAMP = r['timestamp']
                TIMESTAMP = datetime.strptime(TIMESTAMP,"%Y-%m-%d %H:%M:%S.%f")
                TIMESTAMP = TIMESTAMP.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/Toronto"))
                TIMESTAMP = str(TIMESTAMP.replace(tzinfo=None))

                log_timestamp = r['log_timestamp']
                protocolversion = r['protocolversion']
                referer = r['referer']
                #clientip_country_code = r['clientip_country_code']
                #clientip_city_name = r['clientip_city_name']
                #clientip_geolocation = r['clientip_geolocation']
                clientip = r['clientip']
                Server_Siteid = r['Server_Siteid']
                source = r['source']
                #siteip_country_code = r['siteip_country_code']
                #siteip_city_name = r['siteip_city_name']
                #siteip_geolocation = r['siteip_geolocation']
                siteip = r['siteip']
                Host = r['host']
                siteid = r['siteid']
                cookie = r['cookie']
                method = r['method']
                querystring = r['querystring']
                icreate_username = r['icreate_username']
                port = r['port']
                subresponse = r['subresponse']
                name = r['name']
                IP_Agent = r['IP_Agent']
                useragent = r['useragent']
                bytes_recieved = r['bytes_recieved']
                bytes_sent = r['bytes_sent']
                File = r['file']
                timetaken = r['timetaken']
                timestamp = r['timestamp']
                url = r['url']
                response = r['response']
                sc32status = r['sc32status']
                servername = r['servername']
                facility = r['facility']
                username = r['username']
                #'clientip_country_code':clientip_country_code, 'clientip_city_name':clientip_city_name, 'clientip_geolocation':clientip_geolocation, 
                #'siteip_country_code':siteip_country_code, 'siteip_city_name':siteip_city_name, 'siteip_geolocation':siteip_geolocation, 
                
                LIST.append({'requesting_useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'log_timestamp':log_timestamp, 'protocolversion':protocolversion, 'referer':referer, 'clientip':clientip, 'Server_Siteid':Server_Siteid, 'source':source, 'siteip':siteip, 'host':Host, 'siteid':siteid, 'cookie':cookie, 'method':method, 'querystring':querystring, 'icreate_username':icreate_username, 'port':port, 'subresponse':subresponse, 'name':name, 'IP_Agent':IP_Agent, 'useragent':useragent, 'bytes_recieved':bytes_recieved, 'bytes_sent':bytes_sent, 'file':File, 'timetaken':timetaken, 'timestamp':timestamp, 'url':url, 'response':response, 'sc32status':sc32status, 'servername':servername, 'facility':facility, 'username':username})

        data = {}
        data['data'] = LIST
        return data

def list_web_responsecode_server(servername, response, num, startingdate):
        WEB_R = WEB_RESPONSECODE_SERVER(servername, response, num, startingdate)
        return WEB_R