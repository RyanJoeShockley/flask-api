from flask import request
import dns
import dns.resolver
import dns.name
import dns.message
import dns.query
import json
import re


def GOLIVE(domain):

        tempdomain = domain
        count = len(domain.split('.'))
        NXDOMAIN = False
        CNAME_FLAG = False
        i = 0
        while i <= count:
                try:
                        answers = dns.resolver.query(tempdomain, 'SOA')
                        NXDOMAIN = False
                except dns.resolver.NXDOMAIN:
                        NXDOMAIN = True
                except dns.resolver.NoAnswer:
                        NXDOMAIN = True
                except dns.name.EmptyLabel:
                        NXDOMAIN = True
                except dns.resolver.NoNameservers:
                        NXDOMAIN = True
                finally:
                        if(NXDOMAIN == True):
                                tempdomain = tempdomain.replace((tempdomain.split('.')[0] + '.'),"", 1)
                                i += 1
                        else:
                                if i == count -1:
                                        tempdomain = 'Domain does not exist!'
                                        break
                                break
        answers = []
        regex = '.$'
        rootdomain = tempdomain
        if rootdomain == 'Domain does not exist!':
                answers.append({'useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'error':rootdomain})
                #answers.append(ERROR)
                data = {}
                data['data'] = answers
                json_data = json.dumps(data)
                return json_data

        nameservers = []
        NXDOMAIN = False
        try:
                nsrecords = dns.resolver.query(rootdomain, 'ns')
                NXDOMAIN = False
        except dns.resolver.NXDOMAIN:
                NXDOMAIN = True
        except dns.resolver.NoAnswer:
                NXDOMAIN = True
        except dns.name.EmptyLabel:
                NXDOMAIN = True
        except dns.resolver.NoNameservers:
                NXDOMAIN = True
        finally:
                if(NXDOMAIN == True):
                        answers.append({'useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'error':'Top Level Domain does not exist'})
                        #answers.append(ERROR)
                        data = {}
                        data['data'] = answers
                        json_data = json.dumps(data)
                        return json_data
                else:
                        for record in nsrecords:
                                nsserver = str(record.target)
                                nsserver = re.sub(regex, "", nsserver)
                                nameservers.append(nsserver)

        NS_IPs = []
        NXDOMAIN = False
        for nameserver in nameservers:
                try:
                        answer = dns.resolver.query(nameserver, 'A')
                except dns.resolver.NXDOMAIN:
                        NXDOMAIN = True
                except dns.resolver.NoAnswer:
                        NXDOMAIN = True
                except dns.name.EmptyLabel:
                        NXDOMAIN = True
                except dns.resolver.NoNameservers:
                        NXDOMAIN = True
                finally:
                        for data in answer:
                                NS = nameserver + ':' + str(data.address)
                                NS_IPs.append(NS)
        for NS_IP in NS_IPs:
                resolver = dns.resolver.Resolver(configure=False);
                NS = NS_IP.split(':')[0]
                NSIP = NS_IP.split(':')[1]
                resolver.nameservers = [NSIP]
                try:
                        NXDOMAIN = False
                        answer = resolver.query(domain , "CNAME")
                        CNAME_FLAG = True
                except dns.resolver.NXDOMAIN:
                        NXDOMAIN = True
                except dns.resolver.NoAnswer:
                        NXDOMAIN = True
                except dns.name.EmptyLabel:
                        NXDOMAIN = True
                except dns.resolver.NoNameservers:
                        NXDOMAIN = True
                finally:
                        if(CNAME_FLAG == True):
                                if(NXDOMAIN == True):
                                        DOMAIN = 'Sub-domain does not exist!'
                                        TTL = 'NULL'
                                        TYPE = 'NULL'
                                        IP = 'NULL'
                                        answers.append({'useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'ns_server':NS, 'ns_serverip':NSIP, 'domain':domain, 'error':'Sub-Domain Does not Exist!'})
                                else:
                                        try:
                                                NXDOMAIN = False
                                                VALUE = str(answer.rrset).split(' ')[4]
                                                VALUE = VALUE[:-1]
                                                cnameip = dns.resolver.query(VALUE , "A")
                                                CNAME_FLAG = True
                                        except dns.resolver.NXDOMAIN:
                                                NXDOMAIN = True
                                        except dns.resolver.NoAnswer:
                                                NXDOMAIN = True
                                        except dns.name.EmptyLabel:
                                                NXDOMAIN = True
                                        except dns.resolver.NoNameservers:
                                                NXDOMAIN = True
                                        finally:
                                                if(NXDOMAIN == True):
                                                        CNAMEIP = 'Error'
                                                        TTL = str(answer.rrset).split(' ')[1]
                                                        DOMAIN = str(answer.rrset).split(' ')[0]
                                                        DOMAIN = DOMAIN[:-1]
                                                        TYPE = str(answer.rrset).split(' ')[3]
                                                        VALUE = str(answer.rrset).split(' ')[4]
                                                else:
                                                        CNAMEIP = str(cnameip.rrset).split(' ')[4]
                                                        TTL = str(answer.rrset).split(' ')[1]
                                                        DOMAIN = str(answer.rrset).split(' ')[0]
                                                        DOMAIN = DOMAIN[:-1]
                                                        TYPE = str(answer.rrset).split(' ')[3]
                                                        VALUE = str(answer.rrset).split(' ')[4]
                                #Full_Record = [NS, NSIP, DOMAIN, IP, TYPE, TTL]
                                #answers.append(Full_Record)
                                answers.append({'useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'ns_server':NS, 'ns_serverip':NSIP, 'domain':domain, 'value':VALUE, 'cname_ip':CNAMEIP, 'ttl':TTL, 'type':TYPE})

                        else:
                                try:
                                        NXDOMAIN = False
                                        answer = resolver.query(domain , "A")
                                except dns.resolver.NXDOMAIN:
                                        NXDOMAIN = True
                                except dns.resolver.NoAnswer:
                                        NXDOMAIN = True
                                except dns.name.EmptyLabel:
                                        NXDOMAIN = True
                                except dns.resolver.NoNameservers:
                                        NXDOMAIN = True
                                finally:
                                        if(NXDOMAIN == True):
                                                DOMAIN = 'Sub-domain does not exist!'
                                                TTL = 'NULL'
                                                TYPE = 'NULL'
                                                IP = 'NULL'
                                                answers.append({'useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'ns_server':NS, 'ns_serverip':NSIP, 'domain':domain, 'error':'Sub-Domain Does not Exist!'})
                                        else:
                                                TTL = str(answer.rrset).split(' ')[1]
                                                DOMAIN = str(answer.rrset).split(' ')[0]
                                                DOMAIN = DOMAIN[:-1]
                                                TYPE = str(answer.rrset).split(' ')[3]
                                                IP = str(answer.rrset).split(' ')[4]
                                        #Full_Record = [NS, NSIP, DOMAIN, IP, TYPE, TTL]
                                        answers.append({'useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'ns_server':NS, 'ns_serverip':NSIP, 'domain':DOMAIN, 'value':IP, 'ttl':TTL, 'type':TYPE})
        data = {}
        data['data'] = answers
        return data

def list_golive(domain_name):
        DNS_GOLIVE = GOLIVE(domain_name)
        return DNS_GOLIVE
