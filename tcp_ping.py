import argparse
import socket
import sys
import threading
import time


def get_ip(host, family=socket.AF_INET):
	"""
	A method used to obtain the IP address from the domain name.

	Parameters
	----------
	host : str
		The host that should be converted to its IP address.
	family : AddressFamily, optional
		Determines the format of the address structure to be used on the socket.

	Returns
	-------
	str
		The IP address of the converted domain name.
	"""

	try:
		if family == socket.AF_INET6:
			return socket.getaddrinfo(host, None, socket.AF_INET6)[0][4][0]
		elif family == socket.AF_INET:
			return socket.getaddrinfo(host, None, socket.AF_INET)[0][4][0]
		else:
			return socket.gethostbyname(host)
	except socket.gaierror:
		sys.exit("The host's IP address was not retrievable.")


class TCPPinger(threading.Thread):
	"""
	A class used to probe the connectivity and response time of a specified
	host.

	Attributes
	----------
	host : str
		Host to connect to.
	port : int
		Which port to connect with.
	quantity : int
		Amount of times to probe the host (-1 for infinitely).
	timeout : int
		How long we should try to connect for until it returns an error (MS).
	sleep : int
		Delay until next TCP request (MS).
	family : AddressFamily
		Determines the format of the address structure to be used on the socket.

	Methods
	-------
	run()
		Probes the host using all the necessary attributes while sharing the
		response time.
	"""

	def __init__(
		self, host, port, 
		quantity=4, timeout=3000, sleep=1000, 
		family=socket.AF_INET
	):
		"""
		Parameters
		----------
		host : str
			Host to connect to.
		port : int
			Which port to connect with.
		quantity : int
			Amount of times to probe the host (-1 for infinitely).
		timeout : int
			How long we should try to connect for until it returns an error (MS).
		sleep : int
			Delay until next TCP request (MS).
		family : AddressFamily
			Determines the format of the address structure to be used on the socket.
		"""
		
		threading.Thread.__init__(self)

		self.host = get_ip(host)
		self.port = port
		self.quantity = quantity
		self.timeout = timeout / 1000
		self.sleep = sleep / 1000
		self.family = family

		self.finished = False
		
		self.amount_looped = 0
		self.successful_pings = 0
		self.failed_pings = 0

	def run(self):
		"""
		This is the main method that is used for pinging the host.
		"""

		while (self.amount_looped < self.quantity or self.quantity == -1) and self.finished is False:
			try:
				addr = (self.host, self.port)
				
				if self.family == socket.AF_INET6:
					addr += (0, 0)

				sock = socket.socket(self.family, socket.SOCK_STREAM)
				sock.settimeout(self.timeout)

				start = time.time() * 1000

				if sock.connect_ex(addr) == 0:
					self.successful_pings += 1

					now = int(time.time() * 1000 - start)

					print("Probing {}:{}/TCP - Port is open | Time={}ms".format(
						self.host, self.port, now
					))
				else:
					self.failed_pings += 1

					print("Probing {}:{}/TCP - Port is closed".format(
						self.host, self.port
					))

				sock.close()
			except socket.error:
				self.failed_pings += 1

				print("Socket failure...")
			finally:
				self.amount_looped += 1

				if self.amount_looped != self.quantity:
					time.sleep(self.sleep)

	def stop(self):
		self.finished = True

	def ping_stats(self):
		return {
			"total": self.amount_looped, 
			"successful": self.successful_pings, 
			"failed": self.failed_pings
		}


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"host", 
		action="store", 
		help="Host to connect to"
	)
	parser.add_argument(
		"-port", 
		"-p", 
		type=int, 
		required=True, 
		help="Which port to connect with"
	)
	parser.add_argument(
		"-num", 
		"-n", 
		type=int, 
		default=4, 
		help="Amount of times to probe the host"
	)
	parser.add_argument(
		"-timeout", 
		"-t", 
		type=int, 
		default=3000, 
		help="How long we should try to connect for until it returns an error (MS)"
	)
	parser.add_argument(
		"-sleep", 
		"-s", 
		type=int, 
		default=1000, 
		help="Delay until next TCP request (MS)"
	)
	parser.add_argument(
		"-loop", 
		"-l", 
		default=False, 
		action="store_true", 
		help="Constantly pinging the host (Even if number specified)"
	)
	parser.add_argument(
		"-ipv4", 
		"-4", 
		default=True, 
		action="store_true", 
		help="Uses IPv4"
	)
	parser.add_argument(
		"-ipv6", 
		"-6", 
		default=False, 
		action="store_true", 
		help="Uses IPv6"
	)

	args = parser.parse_args()

	if args.ipv6 is True:
		family = socket.AF_INET6
	elif args.ipv4 is True:
		family = socket.AF_INET
	else:
		sys.exit("An unknown error has occurred.")

	if args.loop is True:
		args.num = -1

	host = get_ip(args.host, family)

	if args.host != host:
		print("Starting to probe {} ({}) on port {}".format(
			args.host, host, args.port
		))
	else:
		print("Starting to probe {} on port {}".format(args.host, args.port))

	pinger = TCPPinger(
		host, args.port, 
		args.num, args.timeout, args.sleep, 
		family
	)
	pinger.start()

	input()

	pinger.stop()

	print(pinger.ping_stats())
