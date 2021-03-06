import requests
import json
import sys

MY_SERVER_ADDR = '127.0.0.1'
MY_SERVER_PORT = '8083'

def info_agent(hostname, ip, api_key):
	payload = {'hostname': hostname, 'apikey': api_key}
	payload_encode_json = json.dumps(payload)

	print(f' - debug {payload_encode_json}')

	headers = {
	  'Content-Type': 'application/json'
	}

	URL = 'http://'+MY_SERVER_ADDR+':'+MY_SERVER_PORT+'/new'
	response = requests.request("POST", URL, headers=headers, data=payload_encode_json)
	print(f'\n [*] [Server Response]\n\t{response.text}')

if __name__ == '__main__':
	if len(sys.argv) >= 3:
		try:
			info_agent(sys.argv[1], sys.argv[2])
		except Exception as e:
			print(e)
	else:
		print('usage: ' + sys.argv[0] + ' hostname api-key')