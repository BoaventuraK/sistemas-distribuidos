import Pyro5.api

@Pyro5.api.expose
class Subscriber:
    def receive_message(self, message):
        print(f"[Mensagem Recebida] {message}")

if __name__ == "__main__":
    # Inicia o daemon do subscriber para que ele possa receber chamadas
    daemon = Pyro5.api.Daemon()
    
    # Registra o subscriber e obtém seu endereço de rede (URI)
    uri = daemon.register(Subscriber())
    
    # Conecta ao Broker e envia o URI
    topic = Pyro5.api.Proxy("PYRONAME:pubsub.topic")
    topic.subscribe(uri)
    
    print("Subscriber registrado. Aguardando mensagens...")
    daemon.requestLoop()