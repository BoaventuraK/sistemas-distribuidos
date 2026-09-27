import Pyro5.api

@Pyro5.api.expose
class Intermediario:
    def __init__(self):
        # Mapeia id_subscriber -> URI (ou Proxy) para permitir o encaminhamento
        self.subscribers = {} 
        # Mapeia nome_do_topico -> set de id_subscribers inscritos
        self.topicos = {} 

    def criar_topico(self, nome):
        if nome not in self.topicos:
            self.topicos[nome] = set()
            print(f"[Tópico Criado] '{nome}'")
            return True
        print(f"[Aviso] Tópico '{nome}' já existe.")
        return False

    def registrar_subscriber(self, id_subscriber, uri=None):
        self.subscribers[id_subscriber] = uri or id_subscriber
        print(f"[Subscriber Registrado] ID: {id_subscriber}")
        return True

    def inscrever(self, id_subscriber, topico):
        if topico not in self.topicos:
            print(f"[Erro] Tópico '{topico}' não existe.")
            return False
            
        if id_subscriber not in self.subscribers:
            print(f"[Erro] Subscriber '{id_subscriber}' não está registrado.")
            return False

        self.topicos[topico].add(id_subscriber)
        print(f"[Inscrição] Subscriber '{id_subscriber}' inscrito no tópico '{topico}'.")
        return True

    def publicar(self, id_publisher, topico, mensagem):
        if topico not in self.topicos:
            print(f"[Erro] Tópico '{topico}' não existe.")
            return False

        assinantes_do_topico = self.topicos[topico].copy()
        print(f"[Publicação] '{id_publisher}' enviou mensagem no tópico '{topico}' para {len(assinantes_do_topico)} assinante(s).")

        # Encaminha a mensagem recebida aos subscribers interessados
        for sub_id in assinantes_do_topico:
            uri = self.subscribers.get(sub_id)
            if not uri:
                continue

            try:
                with Pyro5.api.Proxy(uri) as sub:
                    sub.receive_message(topico, mensagem)
            except Exception:
                print(f"[Falha] Erro de conexão com '{sub_id}' ({uri}). Removendo das inscrições.")
                self.topicos[topico].discard(sub_id)

        return True

def main():
    print("Iniciando o Broker/Intermediário...")
    intermediario = Intermediario()
    
    # Registra o intermediário no serviço de nomes do Pyro5
    daemon = Pyro5.api.Daemon()
    ns = Pyro5.api.locate_ns()
    uri = daemon.register(intermediario)
    ns.register("intermediario.pubsub", uri)

    print("Intermediário pronto e aguardando chamadas.")
    daemon.requestLoop()

if __name__ == "__main__":
    main()