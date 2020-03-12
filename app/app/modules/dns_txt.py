from flask import request
import dns
import dns.resolver
import dns.name
import dns.message
import dns.query
import json
import re

def TXT(domain):

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
		ERROR = [rootdomain, 'NULL', 'NULL', 'NULL', 'NULL', 'NULL']
		answers.append(ERROR)
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
			ERROR = ['Top Level Domain does not exist', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL']
			answers.append(ERROR)
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
		resolver = dns.resolver.Resolver(configure=False)
		NS = NS_IP.split(':')[0]
		NSIP = NS_IP.split(':')[1]
		resolver.nameservers = [NSIP]
		try:
			answer = resolver.query(domain , "TXT")
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
				VALUE = 'No Record'
				TYPE = 'NULL'
				TTL = 'NULL'
				DOMAIN = 'NULL'
				
			else:
				Records = str(answer.rrset)
				Records = Records.splitlines()
				for Record in Records:
					DOMAIN = Record.split(' ')[0]
					regex = '.$'
					DOMAIN = re.sub(regex, "", DOMAIN)
					TTL = Record.split(' ')[1]
					TYPE = Record.split(' ')[3]
					VALUE = Record.split('"')[1]
					Full_Record = [NS, NSIP, DOMAIN, VALUE, TYPE, TTL]
					#answers.append(Full_Record)
					answers.append({'useragent':request.user_agent.string, 'requesting_ip':request.remote_addr, 'ns_server':NS, 'ns_serverip':NSIP, 'domain':DOMAIN, 'value':VALUE, 'ttl':TTL, 'type':TYPE})
	data = {}
	data['data'] = answers
	return data

def list_txt(domain_name):
	DNS_TXT = TXT(domain_name)
	return DNS_TXT