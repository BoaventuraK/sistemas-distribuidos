import Pyro5.api
import time

if __name__ == "__main__":
    # Conecta-se ao Intermediário registrado no Name Server
    intermediario = Pyro5.api.Proxy("PYRONAME:intermediario.pubsub")
    
    # Definições do Publisher
    ID_PUBLISHER = "P1"
    TOPICO = "noticias"
    
    # Garante que o tópico exista no Intermediário
    intermediario.criar_topico(TOPICO)
    
    contador = 1
    while True:
        mensagem = f"Atualização de sistema nº {contador}"
        print(f"[{ID_PUBLISHER}] Publicando no tópico '{TOPICO}': {mensagem}")
        
        # Publica enviando (id_publisher, topico, mensagem)
        intermediario.publicar(ID_PUBLISHER, TOPICO, mensagem)
        
        contador += 1
        time.sleep(2)  # Publica a cada 2 segundos