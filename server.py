import socket
import threading
import os
from des import des

key = "keyyyyyy"
d = des()


def read_msg(clients, sock_cli, addr_cli, username_cli):
    while True:
        # terima pesan
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break

        # parsing pesannya
        act = data.decode("utf - 8").split("|")[0]

        if act == 'get_user':
            send_user_list(sock_cli)
        elif act == 'add':
            _, user_1, user_2 = data.decode("utf - 8").split("|")
            if user_2 in clients:
                add_friend(user_1, user_2)
                msg = "[added as friend]"
            else:
                msg = "[error not found]"
            encrypted = d.encrypt(key, msg, padding=True)
            send_msg(sock_cli, f'{user_2}|{encrypted}')

        elif act == 'chat':
            act, sender, dest, msg = data.decode("utf - 8").split("|")
            msg = "<{}>|{}".format(username_cli, msg)

            # terusankan psan ke semua klien
            if dest == "bcast":
                send_broadcast(clients, '[bcast] ' + msg, addr_cli, sender)
            else:
                if dest in clients:
                    if dest in friends[sender]:
                        dest_sock_cli = clients[dest][0]
                        send_msg(dest_sock_cli, msg)
                    else:
                        send_msg(
                            sock_cli, '{} is not a friend yet'.format(dest))
                else:
                    send_broadcast(clients, '[bcast] ' + msg, addr_cli, sender)
            print(data)
    sock_cli.close()
    print("Connection closed", addr_cli)

# kirim ke semua klien


def send_broadcast(clients, data, sender_addr_cli, sender_uname):
    for uname in friends[sender_uname]:
        sock_cli, addr_cli, _ = clients[uname]
        if not (sender_addr_cli[0] == addr_cli[0] and sender_addr_cli[1] == addr_cli[1]):
            send_msg(sock_cli, data)


def send_msg(sock_cli, data):
    sock_cli.send(bytes(data, "utf-8"))


def send_user_list(sock_cli):
    send_msg(sock_cli, ', '.join(clients.keys()))


def add_friend(username_cli, username_friend):
    friends[username_cli].append(username_friend)


if __name__ == '__main__':
    # buat object socket server
    sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # buat object socket server
    sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # binding object socket ke alamat IP dan port tertentu
    sock_server.bind(("0.0.0.0", 6666))

    # listen for an incoming connection
    sock_server.listen(5)

    # buat dictionary utk menyimpan informasi ttg klien
    clients = {}
    friends = {}

    while True:
        # accept connection dari klien
        sock_cli, addr_cli = sock_server.accept()

        # baca username klien
        username_cli = sock_cli.recv(65535).decode("utf-8")
        print(username_cli, " joined")

        # buat thread baru untuk membaca pesan dan jalankan threadnya
        thread_cli = threading.Thread(target=read_msg, args=(
            clients, sock_cli, addr_cli, username_cli))
        thread_cli.start()

        # simpan informasi ttg klien ke dictionary
        clients[username_cli] = (sock_cli, addr_cli, thread_cli)
        friends[username_cli] = []
