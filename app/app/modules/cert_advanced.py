from flask import request
import json
import re
import ssl
import socket
import OpenSSL
#from OpenSSL import SSL, crypto
import hashlib
from datetime import datetime


def convert(data):
    if isinstance(data, bytes):  return data.decode('ascii')
    if isinstance(data, dict):   return dict(map(convert, data.items()))
    if isinstance(data, tuple):  return map(convert, data)
    return data

def CERT_ADVANCED(domain):
	HOST = domain
	context = ssl.create_default_context()

	for i in context.get_ciphers():
		Cipher_Protocol = i['name'] + ',' + i['protocol'] + ',' + i['description']
		cipher = Cipher_Protocol.split(',')[0]
		protocol = Cipher_Protocol.split(',')[1]
		description = Cipher_Protocol.split(',')[2]
		#print(cipher + ',' + protocol + ',' + description)
		if protocol == 'SSLv2':
			connection_protocol = 'PROTOCOL_SSLv2'
			context = ssl.SSLContext(protcol=connection_protocol)
		elif protocol == 'SSLv3':
			connection_protocol = 'PROTOCOL_SSLv3'
			context = ssl.SSLContext(protcol=connection_protocol)
		elif protocol == 'TLSv1.0':
			connection_protocol = 'PROTOCOL_TLSv1'
			context = ssl.SSLContext(protcol=connection_protocol)
		elif protocol == 'TLSv1.1':
			connection_protocol = 'PROTOCOL_TLSv1_1'
			context = ssl.SSLContext(protcol=connection_protocol)
		elif protocol == 'TLSv1.2':
			connection_protocol = 'PROTOCOL_TLSv1_2'
			context = ssl.SSLContext(protcol=connection_protocol)
		else:
			pass

		Protocol_List = ['PROTOCOL_SSLv2']
		#'PROTOCOL_SSLv3', 'PROTOCOL_TLSv1', 'PROTOCOL_TLSv1_1', 'PROTOCOL_TLSv1_2']
		for prot in Protocol_List:
			#context = ssl.SSLContext(protcol=prot)
			context.set_ciphers(cipher)
			conn = socket.create_connection((HOST, 443))

			SSLConn = False
			try:
				sock = context.wrap_socket(conn, server_hostname=HOST)
				print(sock.cipher())
				SSLConn = True
			except:
				pass
			finally:
				if SSLConn == True:
					print('SUCCESS ' + cipher + ',' + protocol + ',' + description)
				if SSLConn == False:
					print('FAILED ' + cipher + ',' + protocol + ',' + description)

	context = ssl.create_default_context()
	conn = socket.create_connection((HOST, 443))
	sock = context.wrap_socket(conn, server_hostname=HOST)
	print(sock.cipher())
	sock.settimeout(10)

	try:
			der_cert = sock.getpeercert(True)
	finally:
			sock.close()

	PEM_cert = ssl.DER_cert_to_PEM_cert(der_cert)

	#Uses OpenSSL from pyopenssl
	x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, PEM_cert)
	
	get_notBefore_str = x509.get_notBefore().decode()
	get_notAfter_str = x509.get_notAfter().decode()
	notBefore = datetime.strptime(get_notBefore_str, '%Y%m%d%H%M%SZ')
	notAfter = datetime.strptime(get_notAfter_str, '%Y%m%d%H%M%SZ')	
	notBefore = notBefore.strftime('%Y/%m/%d')
	notAfter = notAfter.strftime('%Y/%m/%d')
	
	DATENOW = datetime.now()
	DATENOW = DATENOW.strftime('%Y/%m/%d')
	expiredate = datetime.strptime(notAfter, '%Y/%m/%d')
	currentdate = datetime.strptime(DATENOW, '%Y/%m/%d')
	Days_Until_Expire = str((expiredate - currentdate).days)

	GET_SUBJECT = dict(x509.get_subject().get_components())
	GET_SUBJECT = convert(GET_SUBJECT)
	CN = GET_SUBJECT['CN']
	
	SerialNumber = str(x509.get_serial_number())

	GET_ISSUER = dict(x509.get_issuer().get_components())
	GET_ISSUER = convert(GET_ISSUER)
	Issuer = GET_ISSUER['CN']
	
	Version = str(x509.get_version())

	thumb_md5 = hashlib.md5(der_cert).hexdigest()
	thumb_sha1 = hashlib.sha1(der_cert).hexdigest()
	thumb_sha256 = hashlib.sha256(der_cert).hexdigest()
	for i in range(x509.get_extension_count()):
		VALUE = (x509.get_extension(i))
		try:
			VALUE = str(VALUE)
			if re.search('DNS:', VALUE):
				regex = 'DNS:'
				Altname = re.sub(regex, "", str(VALUE))
		except:
			pass
	regex = ', '
	Altnames = re.sub(regex, ",", Altname)
	VALID_HOST = 'False'
	NAMES = Altnames.split(',')
	for NAME in NAMES:
		if NAME[0] == '*':
			NAME = '.' + NAME
		if re.match(NAME, HOST):
			VALID_HOST = 'True'

	
	Dict = {}
	Dict["CN"] = CN
	Dict["notAfter"] = notAfter
	Dict["notBefore"] = notBefore
	Dict["Issuer"] = Issuer
	Dict["Altnames"] = Altnames
	Dict["MD5_Thumb"] = thumb_md5
	Dict["SHA1_Thumb"] = thumb_sha1
	Dict["SHA256_Thumb"] = thumb_sha256
	Dict["Version"] = Version
	Dict["SerialNumber"] = SerialNumber
	Dict["Valid_Host"] = VALID_HOST
	Dict["Days_Until_Expire"] = Days_Until_Expire
	Dict["useragent"] = request.user_agent.string
	Dict["requesting_ip"] = request.remote_addr
	certdata = []
	certdata.append(Dict)	

	data = {}
	data['data'] = certdata
	return data

def list_cert_advanced(domain_name):
	LIST_CERT_ADVANCED = CERT_ADVANCED(domain_name)
	return LIST_CERT_ADVANCED