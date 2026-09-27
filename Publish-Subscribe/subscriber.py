import Pyro5.api
import threading
import time

@Pyro5.api.expose
class Subscriber:
    def receive_message(self, topico, message):
        print(f"[Mensagem Recebida] Tópico: {topico} | Mensagem: {message}")

def main():
    # 1. Configura o Daemon para que este subscriber receba callbacks remotos
    daemon = Pyro5.api.Daemon()
    subscriber_obj = Subscriber()
    uri = daemon.register(subscriber_obj)

    # Inicia o loop do daemon em uma thread em segundo plano
    daemon_thread = threading.Thread(target=daemon.requestLoop, daemon=True)
    daemon_thread.start()

    # 2. Conecta ao Intermediário via Name Server
    intermediario = Pyro5.api.Proxy("PYRONAME:intermediario.pubsub")

    # Identificador do Subscriber e tópicos de interesse
    ID_SUBSCRIBER = "S1"
    TOPICOS = ["noticias", "avisos"]

    # 3. Registra o Subscriber passando o ID e a URI remota para callback
    print(f"Registrando subscriber '{ID_SUBSCRIBER}' no Intermediário...")
    intermediario.registrar_subscriber(ID_SUBSCRIBER, uri)

    # 4. Inscreve-se nos tópicos desejados
    for topico in TOPICOS:
        # Garante que o tópico exista no intermediário antes de se inscrever
        intermediario.criar_topico(topico)
        
        Sucesso = intermediario.inscrever(ID_SUBSCRIBER, topico)
        if Sucesso:
            print(f"Inscrito com sucesso no tópico: '{topico}'")

    print("\nSubscriber ativo e aguardando mensagens. Pressione Ctrl+C para sair.\n")
    
    # Mantém a thread principal rodando
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando Subscriber...")

if __name__ == "__main__":
    main()