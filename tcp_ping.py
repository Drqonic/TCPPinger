import sys
import time
import socket

if len(sys.argv) < 3:
	sys.exit("Usage: python {} [Host] [Port]".format(sys.argv[0]))

def get_ip(host):
	try:
		return socket.gethostbyname(host)
	except socket.gaierror:
		sys.exit("Unknown host. Couldn't retreive IP")

host = get_ip(sys.argv[1])
port = int(sys.argv[2])

while True:
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(3)
		start = time.time() * 1000
		sock.connect((host, port))
		stop = int(time.time() * 1000 - start)
		print("Probing {}:{}/TCP - Port is open | Time={}ms".format(host, port, stop))
		sock.close()
		time.sleep(1)
	except socket.error:
		print("Probing {}:{}/TCP - Port is closed".format(host, port))
		time.sleep(1)
	except KeyboardInterrupt:
		break
