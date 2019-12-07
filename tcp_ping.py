import sys
import time
import socket
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("host", action="store", help="Host to connect to")
parser.add_argument("-port", "-p", type=int, required=True, help="Which port to connect with")
parser.add_argument("-ipv4", "-4", default=True, action="store_true", help="Uses IPv4")
parser.add_argument("-ipv6", "-6", default=False, action="store_true", help="Uses IPv6")

args = parser.parse_args()

def get_ip(host):
	try:
		if args.ipv6:
			return socket.getaddrinfo(host, None, socket.AF_INET6)[0][4][0]
		elif args.ipv4:
			return socket.getaddrinfo(host, None, socket.AF_INET)[0][4][0]
		else:
			return socket.gethostbyname(host)
	except socket.gaierror:
		sys.exit("Hosts IP address was not retrievable.")

host = get_ip(args.host)

while True:
	try:
		if args.ipv6:
			sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			data = (host, args.port, 0, 0)
		elif args.ipv4:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			data = (host, args.port)

		sock.settimeout(3)

		start = time.time() * 1000
		
		resp = sock.connect_ex(data)

		stop = int(time.time() * 1000 - start)

		if resp == 0:
			print("Probing {}:{}/TCP - Port is open | Time={}ms".format(host, args.port, stop))
			time.sleep(1)
		else:
			print("Probing {}:{}/TCP - Port is closed".format(host, args.port))
			time.sleep(3)

		sock.close()
	except socket.error:
		print("Socket failure...")
		time.sleep(3)
	except KeyboardInterrupt:
		break
