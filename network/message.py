import struct
import socket
import sys

# Taken from
# https://stackoverflow.com/a/17668009

def send_msg(sock, msg):
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock):
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]

    return recvall(sock, msglen)

def recvall(sock, n):
    data = b''
    while len(data) < n:
        try:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        except (socket.timeout, BlockingIOError):
            return None
    return data
