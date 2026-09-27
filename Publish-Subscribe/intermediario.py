import Pyro5.api

@Pyro5.api.expose
class Intermediario:
    def __init__(self):
        self.subscribers = set()

    def subscribe(self, subscriber_uri):
        self.subscribers.add(subscriber_uri)
        print(f"Novo subscriber registrado: {subscriber_uri}")

    def publish(self, message):
        print(f"Publicando mensagem para {len(self.subscribers)} assinante(s)...")
        
        # Itera sobre os assinantes e envia a mensagem
        for uri in self.subscribers.copy():
            try:
                with Pyro5.api.Proxy(uri) as sub:
                    sub.receive_message(message)
            except Exception:
                print(f"Falha de conexão com {uri}. Removendo assinante.")
                self.subscribers.discard(uri)

def main():
    print("Iniciando o Broker...")
    topic_name = "pubsub.topic"
    topic = {Intermediario(): topic_name}
    ns_ = True
    daemon = Pyro5.api.Daemon

    daemon.serveSimple(topic, ns=ns_)

if __name__ == "__main__":
    main()