#!/usr/bin/python
'''
Created on 2012-4-17

@author: DenoFiend
'''
import httplib
import simplejson as json
import sys 
RETURN_SUCCESS_CODE = 1
ERROR_LEV1 = 1
SYSTEM_ERROR = 300
OK = 0

httplib.socket.setdefaulttimeout(5)

def doRequest(host, url, httpMethod, body, headers) :
    try:
        conn = httplib.HTTPConnection(host)
        conn.request(httpMethod, url, body, headers)
        response = conn.getresponse()
    #    print response.status, response.reason
    #    print response.msg
        data = response.read()
      
        response.close();
        conn.close()
    except httplib.socket.error:
        errno, errstr = sys.exc_info()[:2]
        print errno
        print errstr
        sys.exit(2)
    return data

def checkResponse(responseBody):
    #print ">>> parseResponse " + response
    jsonData = json.loads(responseBody)
    #print data["code"]
    if jsonData["code"] == SYSTEM_ERROR:
        print jsonData
        sys.exit (ERROR_LEV1)
        
#select
def select():
	url = "/v1/center/message/select"
	#body = "{\"account\":\"denofiend@gmail.com\", \"nickname\": \"denofiend\", \"password\":\"ee79976c9380d5e337fc1c095ece8c8f22f91f306ceeb161fa51fecede2c4ba1\"}"
	httpMethod = "GET"
	headers = {"Content-type": "application/json"}
	host = "center.db.maxthon.cn:3307"

	return doRequest(host, url, httpMethod, None, headers)

#update
def update_status(id, status):
	url = "/v1/center/message/status/update?id="+str(id) +"&status="+str(status)

	httpMethod = "GET"
	headers = {"Content-type": "application/json"}
	host = "center.db.maxthon.cn:3307"
	return doRequest(host, url, httpMethod, None, headers)


def local_sync(body, host):
	url = "/v1/local/sync"
	httpMethod = "POST"
	headers = {"Content-type": "application/json"}

	return doRequest(host, url, httpMethod, body, headers)


# main function
def main():

	if len(sys.argv) != 5:
		print "Usage:python user_api.queue.py cn_host cn_port com_host com_port"
		sys.exit(-2)

	cn_host = sys.argv[1]
	cn_port = sys.argv[2]
	cn_host = cn_host + ":" + cn_port

	com_host = sys.argv[3]
	com_port = sys.argv[4]
	com_host = com_host + ":" + com_port

	#get one from quqeue
	body =  select()
	print body
	jsonData = json.loads(body)

	if len(jsonData) == 0:
		print 'queue is empty'
		return

	json_json = json.loads(jsonData[0]['json'])
	json_json['status'] = jsonData[0]['status']
	json_json['region_id'] = jsonData[0]['region_id']
	json_json['type'] = jsonData[0]['type']
	json_json['user_id'] = jsonData[0]['user_id']

	#set this message status to 1
	update_status(jsonData[0]['id'], 1);

	print json_json


	#sync this message to com 
	sync_body =  local_sync(json.dumps(json_json), com_host)
	sync_json = json.loads(sync_body)
	print sync_json

	if sync_json['code'] == 1:
		#sync to cn
		sync_body =  local_sync(json.dumps(json_json), cn_host)
		sync_json = json.loads(sync_body)
		print sync_json

		#set this message status to 2
		update_status(jsonData[0]['id'], 2);

main()


   








    
