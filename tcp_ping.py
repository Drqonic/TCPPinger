import sys
import time
import socket
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("host", action="store", help="Host to connect to")
parser.add_argument("-port", "-p", type=int, required=True, help="Which port to connect with")
parser.add_argument("-num", "-n", type=int, default=4, help="Amount of times to probe the host")
parser.add_argument("-timeout", "-t", type=int, default=3, help="How long we should try to connect until it returns an error")
parser.add_argument("-sleep", "-s", type=int, default=1, help="Delay until next TCP request")
parser.add_argument("-loop", "-l", default=False, action="store_true", help="Constantly pinging the host (Even if number specified)")
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
		sys.exit("Host's IP address was not retrievable.")

host = get_ip(args.host)

def create_sock():
	if args.ipv6:
		sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		data = (host, args.port, 0, 0)
	elif args.ipv4:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		data = (host, args.port)

	return sock, data

i = 0

if args.host != host:
	print("Starting to probe {} ({}) on port {}".format(args.host, host, args.port))
else:
	print("Starting to probe {} on port {}".format(args.host, args.port))

while i < args.num:
	try:
		if not args.loop: i += 1

		sock, data = create_sock()

		sock.settimeout(args.timeout)

		start = time.time() * 1000
		
		resp = sock.connect_ex(data)

		stop = int(time.time() * 1000 - start)

		if resp == 0:
			print("Probing {}:{}/TCP - Port is open | Time={}ms".format(host, args.port, stop))
			if i == args.num: break
			time.sleep(args.sleep)
		else:
			print("Probing {}:{}/TCP - Port is closed".format(host, args.port))
			if i == args.num: break
			time.sleep(args.sleep)

		sock.close()
	except socket.error:
		print("Socket failure...")
		time.sleep(args.sleep)
	except KeyboardInterrupt:
		break
