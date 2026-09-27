#Kauan Boaventura e Lucas Oliveira

import socket
import threading

clientes = []


class ClientThread(threading.Thread):

    def __init__(self, client_socket, address):
        super().__init__()

        self.client_socket = client_socket
        self.address = address

        clientes.append(self.client_socket)

        print(f"[INFO] Conectado a {address}")

    def run(self):

        try:
            while True:

                data = self.client_socket.recv(1024)

                if not data:
                    print(f"[INFO] Cliente {self.address} desconectou.")
                    break
                
                mensagem = data.decode()
                print(mensagem)

                # Envia para todos os clientes
                for cliente in clientes:
                    try:
                        cliente.sendall(mensagem.encode())
                    except Exception as e:
                        print(f"[ERRO] Não foi possível enviar: {e}")

        except Exception as e:
            print(f"[ERRO] {e}")

        finally:

            if self.client_socket in clientes:
                clientes.remove(self.client_socket)

            self.client_socket.close()

            print(f"[INFO] Conexão com {self.address} encerrada.")


def start_server():

    server_port = 8000

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.bind(("localhost", server_port))
    server_socket.listen()

    print(f"[INFO] Servidor escutando na porta {server_port}...")

    while True:

        client_socket, addr = server_socket.accept()

        thread = ClientThread(client_socket, addr)

        thread.start()


if __name__ == "__main__":
    start_server()