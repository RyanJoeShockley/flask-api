from flask import request
import re
import requests
import sys

def REQ(protocol, url):

    regex = '%2F'
    url  = re.sub(regex, "/", url)
    URL = protocol + '://' + url
    print(URL, file=sys.stdout)
    print(URL, file=sys.stderr)
    SUCCESS = False
    REDIRECTED = False
    LIST = []
    Redirect_List = []
    Headers_List = []
    Redirect_Dict = {}
    Headers_Dict = {}
    try:
        response = requests.get(URL)
        SUCCESS = True
        print(SUCCESS)
    except requests.exceptions.Timeout:
        MESSAGE = 'Time Out'
    except requests.exceptions.TooManyRedirects:
        MESSAGE = 'Redirect Loop'
    except requests.exceptions.SSLError:
        MESSAGE = 'SSL Error'
    except requests.exceptions.RequestException:
        MESSAGE = 'Connection Error'
    finally:
        if SUCCESS == True:
            MESSAGE = 'OK'
            if response.history:
                REDIRECTED = True
                for resp in response.history:
                    Redirect_Dict = {'response_code': resp.status_code, 'response': resp.url}
                    Redirect_List.append(dict(Redirect_Dict))
            else:
                REDIRECTED = False
                Redirect_Dict = {'response_code': 'Null', 'response': 'Null'}
                Redirect_List.append(dict(Redirect_Dict))
            Final_Destination_Url = response.url
            Final_Destination_Status_code = response.status_code
            if REDIRECTED == True:
                Redirect_Dict1 = {'response_code': Final_Destination_Status_code, 'response':Final_Destination_Url}
                Redirect_List.append(dict(Redirect_Dict1))
            Protocol = Final_Destination_Url.split(':')[0]
            if Protocol == 'https':
                SSL_Redirect = True
            elif Protocol == 'http':
                SSL_Redirect = False
            else:
                SSL_Redirect = 'Unknown'
            if response.headers:
                Headers_List.append(dict(response.headers))
            else:
                Headers_Dict = {'Null': 'Null'}
                Headers_List.append(dict(Headers_Dict))
        else:
            Redirect_Dict = {'response_code': 'Null', 'response': 'Null'}
            Redirect_List.append(dict(Redirect_Dict))
            SSL_Redirect = 'Null'
            Final_Destination_Url = 'Null'
            Final_Destination_Status_code = 'Null'
            Headers_Dict = {'Null': 'Null'}
            Headers_List.append(dict(Headers_Dict))

    LIST.append({'requesting_useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'message':MESSAGE, 'redirected':REDIRECTED, 'redirects':Redirect_List, 'final_destination_url':Final_Destination_Url, 'final_destination_status_code':Final_Destination_Status_code, 'final_destination_ssl': SSL_Redirect, 'requested_url': URL, 'response_headers':Headers_List})
    data = {}
    data['data'] = LIST
    return data

def get_request(protocol, url):
	HTTP_REQ = REQ(protocol, url)
	return HTTP_REQ

#P = 'http'
#U = 'lakecountry.ic10.esolg.ca%2Fen%2FResourcesGeneral%2Ftest.jpg'
#a = get_request(P, U)
#print(a)