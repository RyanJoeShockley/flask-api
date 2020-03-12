from flask import request
from flask import make_response, abort
import dns
import dns.resolver
import dns.name
import dns.message
import dns.query
import json
import re

def A(domain):
 
	staticdomain = domain
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
		answers.append({'root_domain':'NULL', 'useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'ns_server':'NULL', 'ns_serverip':'NULL', 'domain':staticdomain, 'value':'NULL', 'ttl':'NULL', 'type':'NULL', 'Status':'ERROR', 'Message':'Domain does not exist!'})
		data = {}
		data['data'] = answers
		return data	
		
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
			answers.append({'root_domain':rootdomain, 'useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'ns_server':'NULL', 'ns_serverip':'NULL', 'domain':staticdomain, 'value':'NULL', 'ttl':'NULL', 'type':'NULL', 'Status':'ERROR', 'Message':'Top Level Domain does not exist'})
			data = {}
			data['data'] = answers
			return data
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
		resolver = dns.resolver.Resolver(configure=False)
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
					MESSAGE = 'Sub-domain does not exist!'
					STATUS = 'ERROR'
					TTL = 'NULL'
					TYPE = 'NULL'
					IP = 'NULL'
				else:
					MESSAGE = 'OK'
					STATUS = 'SUCCESS'
					TTL = str(answer.rrset).split(' ')[1]
					DOMAIN = str(answer.rrset).split(' ')[0]
					DOMAIN = DOMAIN[:-1]
					TYPE = str(answer.rrset).split(' ')[3]
					IP = str(answer.rrset).split(' ')[4]
				answers.append({'root_domain':rootdomain, 'useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'ns_server':NS, 'ns_serverip':NSIP, 'domain':staticdomain, 'value':IP, 'ttl':TTL, 'type':TYPE, 'Status':STATUS, 'Message':MESSAGE})

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
						MESSAGE = 'Sub-domain does not exist!'
						STATUS = 'ERROR'
						TTL = 'NULL'
						TYPE = 'NULL'
						IP = 'NULL'
					else:
						MESSAGE = 'OK'
						STATUS = 'SUCCESS'
						TTL = str(answer.rrset).split(' ')[1]
						DOMAIN = str(answer.rrset).split(' ')[0]
						DOMAIN = DOMAIN[:-1]
						TYPE = str(answer.rrset).split(' ')[3]
						IP = str(answer.rrset).split(' ')[4]
					answers.append({'root_domain':rootdomain, 'useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'ns_server':NS, 'ns_serverip':NSIP, 'domain':staticdomain, 'value':IP, 'ttl':TTL, 'type':TYPE, 'Status':STATUS, 'Message':MESSAGE})		
	data = {}
	data['data'] = answers
	return data

def list_A(domain_name):
	DNS_A = A(domain_name)
	return DNS_A