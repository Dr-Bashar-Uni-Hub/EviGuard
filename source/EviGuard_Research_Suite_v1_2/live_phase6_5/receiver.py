import json, socket, sys, time
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('10.77.0.1', 9900))
with open(sys.argv[1], 'w', buffering=1) as f:
    while True:
        data, addr = sock.recvfrom(4096)
        f.write(json.dumps({'time_ns': time.time_ns(), 'source': addr[0], 'message': data.decode(errors='replace')})+'\n')
