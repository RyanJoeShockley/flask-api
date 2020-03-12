from flask import request
from elasticsearch import Elasticsearch
from ssl import create_default_context
import json
import pytz
from datetime import datetime


def EMAIL_SUB(address, num):

        EMAILDATA = '*' + address + '*'
        EMAILCOUNT = num

        CONTEXT = create_default_context(cafile="certs/certs.pem")
        INDEX = 'processed_maillogs*'

        CONN = Elasticsearch(
		['elastic-api.esolutionsgroup.ca'],
                http_auth=('Admin', 'Systemsteam'),
                scheme="https",
                port=8999,
                ssl_context=CONTEXT,
                timeout=60,
        )

        def searchid(QUERY, INDEX):
                es = CONN
                MATCHES = es.search(index=INDEX, body=QUERY)
                HITS = MATCHES['hits']['hits']
                for HIT in HITS:
                        yield (HIT['_source'])

        QUERY = {
                "size" : EMAILCOUNT,
                        "query":
                        {
                                "bool":
                                        {
                                                "must":
                                                {
                                                        "wildcard":
                                                        {
                                                                "subject": EMAILDATA
                                                        }
                                                },
                                                "must_not":
                                                {
                                                        "term":
                                                        {
                                                                "relay_source": "nagios1"
                                                        }
                                                }
                                        }
                        },
                                "sort" :
                                        [
                                                { "timestamp" : {"order" : "desc"}}
                                        ]
                }

        LIST = []
        results = searchid(QUERY,INDEX)
        for r in results:
                TIMESTAMP = r['timestamp']
                TIMESTAMP = datetime.strptime(TIMESTAMP,"%Y-%m-%d %H:%M:%S.%f")
                TIMESTAMP = TIMESTAMP.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/Toronto"))
                TIMESTAMP = str(TIMESTAMP.replace(tzinfo=None))

                FROM = r['from']
                TO = r['to']
                SUBJECT = r['subject']
                STATUS = r['status']
                CLIENT_HOSTNAME = r['client_hostname']
                CLIENT_IP = r['client_ip']
                STATUS = r['status']
                DELAY_BEFORE_QUEUE = r['delay_before_queue']
                DELAY_IN_QUEUE = r['delay_in_queue']
                DELAY_CONN_SETUP = r['delay_conn_setup']
                DELAY_TRANSMISSION = r['delay_transmission']
                DELAY_TOTAL = r['delay_total']
                RESPONSE = r['response']
                SIZE = r['size']
                RELAY_HOSTNAME = r['relay_hostname']
                RELAY_IP = r['relay_ip']
                RELAY_SOURCE = r['relay_source']
                DSN = r['dsn']
                NRCPT = r['nrcpt']
                MESSAGEID = r['messageid']
                QUEUEID = r['queueid']
                SOURCE = r['relay_source']
	
                LIST.append({'useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'date':TIMESTAMP, 'from':FROM, 'to':TO, 'subject':SUBJECT, 'status':STATUS, 'sending_relay':RELAY_SOURCE, 'receiving_relay_hostname':RELAY_HOSTNAME, 'receiving_relay_ip':RELAY_IP, 'size':SIZE, 'response':RESPONSE, 'delay_before_queue':DELAY_BEFORE_QUEUE, 'delay_in_queue':DELAY_IN_QUEUE, 'delay_conn_setup':DELAY_CONN_SETUP, 'delay_transmission':DELAY_TRANSMISSION, 'delay_total':DELAY_TOTAL, 'dsn_code':DSN, 'nrcpt':NRCPT, 'messageid':MESSAGEID, 'queueid':QUEUEID, 'relay_source':SOURCE, 'client_hostname':CLIENT_HOSTNAME, 'client_ip':CLIENT_IP})

        data = {}
        data['data'] = LIST
        return data

def list_email_subject(address, num):
        EMAIL_S = EMAIL_SUB(address, num)
        return EMAIL_S