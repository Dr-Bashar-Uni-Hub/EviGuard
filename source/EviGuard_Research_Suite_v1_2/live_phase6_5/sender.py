import socket, sys, time
label, host, port = sys.argv[1], sys.argv[2], int(sys.argv[3])
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for i in range(10):
    sock.sendto(f'{label}:{i}'.encode(), (host, port))
    time.sleep(.01)
print('sent', label, 10)
