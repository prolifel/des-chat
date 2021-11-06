import socket
import sys
import threading
import os
from des import des

key = "keyyyyyy"
d = des()


def read_msg(sock_cli):
    while True:
        # terima pesan
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break

        decoded_data = data.decode('utf-8')
        username, msg = decoded_data.split("|")
        msg = d.decrypt(key, msg, padding=True)
        print(f"  {username}: {msg}")
        print("Pilih aksi [1: kirim pesan, 2: tambah teman, 3: exit]:")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Expected Username as command line argument')
        exit()

    # buat object socket
    sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect ke server
    sock_cli.connect(("127.0.0.1", 6666))

    # kirim username ke server
    username = sys.argv[1]
    sock_cli.send(bytes(username, "utf-8"))

    # buat thread utk membaca pesan dan jalankan threadnya
    thread_cli = threading.Thread(target=read_msg, args=(sock_cli,))
    thread_cli.start()

    while True:
        act = int(
            input("Pilih aksi [1: kirim pesan, 2: tambah teman, 3: exit]:\n"))
        if act == 1:
            # kirim/terima pesan
            dest = input(
                "Masukkan username tujuan (ketikan bcast untuk broadcast pesan):")
            msg = input("Masukkan pesan untuk {}:".format(dest))
            encrypted = d.encrypt(key, msg, padding=True)
            data = ["chat", username, dest, encrypted]

            print("  <{}>: {}".format(username, msg))
            sock_cli.send(bytes('|'.join(data), 'utf-8'))
        elif act == 2:
            # tambah teman
            dest = input("Masukkan username yang ingin ditambahkan:")
            data = "add|{}|{}".format(username, dest)
            sock_cli.send(bytes(data, 'utf-8'))
        if act == 3:
            # sock_cli.send(bytes('exit', 'utf-8'))
            sock_cli.close()
            break

    exit()
