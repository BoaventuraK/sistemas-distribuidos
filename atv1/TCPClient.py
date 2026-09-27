#Kauan Boaventura e Lucas Oliveira

import socket
import threading

def receber_mensagens(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)

            if not data:
                print("[INFO] Servidor encerrou a conexão.")
                break

            mensagem = data.decode()

            print(f"Recebido: {mensagem}")

        except Exception as e:
            print(f"[ERRO] {e}")
            break

# Função principal do cliente
def start_client():
    server_address = '127.0.0.1'
    server_port = 8000

    # Criação do socket TCP e conexão com o servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_address, server_port))
        print("[INFO] Conectado ao servidor.")

        name = input("Digite seu nome: ")

        thread = threading.Thread(
            target=receber_mensagens,
            args=(client_socket,)
        )

        thread.daemon = True
        thread.start()
        # Envia 10 mensagens para o servidor
        while True:
            message = input()
            message = f"{name}: {message}"
            client_socket.send(message.encode())
            
            # Aguarda resposta do servidor
            # data = client_socket.recv(40).decode()
            # print(f"Recebido: {data}")
            

# Início da execução
if __name__ == "__main__":
    start_client()
