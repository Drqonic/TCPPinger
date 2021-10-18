import argparse
import random
import socket
import sys
import threading
import time


def get_ip(host, family=socket.AF_INET):
	try:
		if family == socket.AF_INET6:
			return socket.getaddrinfo(host, None, socket.AF_INET6)[0][4][0]

		if family == socket.AF_INET:
			return socket.getaddrinfo(host, None, socket.AF_INET)[0][4][0]

		return socket.gethostbyname(host)
	except socket.gaierror:
		sys.exit("Host's IP address was not retrievable.")


class TCPPinger(threading.Thread):
	def __init__(self, host, port, quantity=4, timeout=3000, sleep=1000, family=socket.AF_INET):
		threading.Thread.__init__(self)

		self.host = host
		self.port = port
		self.quantity = quantity
		self.timeout = timeout / 1000
		self.sleep = sleep / 1000
		self.family = family

	def run(self):
		amount_looped = 0

		while amount_looped < self.quantity or self.quantity == -1:
			try:
				addr = (get_ip(self.host), self.port)
				
				if self.family == socket.AF_INET6:
					addr += (0, 0)

				sock = socket.socket(self.family, socket.SOCK_STREAM)
				sock.settimeout(self.timeout)

				start = time.time() * 1000

				if sock.connect_ex(addr) == 0:
					now = int(time.time() * 1000 - start)

					print("Probing {}:{}/TCP - Port is open | Time={}ms".format(self.host, self.port, now))
				else:
					print("Probing {}:{}/TCP - Port is closed".format(self.host, self.port))

				sock.close()
			except socket.error:
				print("Socket failure...")
			finally:
				amount_looped += 1
				time.sleep(self.sleep)
				

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("host", action="store", help="Host to connect to")
	parser.add_argument("-port", "-p", type=int, required=True, help="Which port to connect with")
	parser.add_argument("-num", "-n", type=int, default=4, help="Amount of times to probe the host")
	parser.add_argument("-timeout", "-t", type=int, default=3000, help="How long we should try to connect for until it returns an error (MS)")
	parser.add_argument("-sleep", "-s", type=int, default=1000, help="Delay until next TCP request (MS)")
	parser.add_argument("-loop", "-l", default=False, action="store_true", help="Constantly pinging the host (Even if number specified)")
	parser.add_argument("-ipv4", "-4", default=True, action="store_true", help="Uses IPv4")
	parser.add_argument("-ipv6", "-6", default=False, action="store_true", help="Uses IPv6")

	args = parser.parse_args()

	if args.ipv6 is True:
		family = socket.AF_INET6

	if args.ipv4 is True:
		family = socket.AF_INET

	if args.loop is True:
		args.num = -1

	host = get_ip(args.host, family)

	if args.host != host:
		print("Starting to probe {} ({}) on port {}".format(args.host, host, args.port))
	else:
		print("Starting to probe {} on port {}".format(args.host, args.port))

	pinger = TCPPinger(host, args.port, args.num, args.timeout, args.sleep, family)
	pinger.start()
