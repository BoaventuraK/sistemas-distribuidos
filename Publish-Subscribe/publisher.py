import Pyro5.api
import time

if __name__ == "__main__":
    topic = Pyro5.api.Proxy("PYRONAME:pubsub.topic")
    
    contador = 1
    while True:
        mensagem = f"Atualização de sistema nº {contador}"
        print(f"Enviando: {mensagem}")
        
        topic.publish(mensagem)
        
        contador += 1
        time.sleep(.5)  # Publica a cada 2 segundos