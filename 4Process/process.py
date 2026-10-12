import sys
import time
import random
import threading
import Pyro5.api

NUM_PROCESSES = 4
RUN_TIME_SECONDS = 30  # Tempo de execução estipulado

@Pyro5.api.expose
class ProcessNode:
    def __init__(self, process_id):
        self.process_id = process_id  # Exemplo: 0 para P1, 1 para P2...
        self.num_processes = NUM_PROCESSES
        
        # Inicializa o relógio vetorial com zeros: [0, 0, 0, 0]
        self.vector_clock = [0] * self.num_processes
        self.event_counter = 0
        self.lock = threading.Lock()
        
    def log(self, action_type, detail, sender_clock=None):
        """Registra e exibe os logs com a evolução do relógio vetorial."""
        timestamp = time.strftime("%H:%M:%S")
        process_name = f"P{self.process_id + 1}"
        
        log_msg = f"[{timestamp}] [{process_name}] {action_type} | Detalhes: {detail} | Relógio Vetorial Local: {self.vector_clock}"
        if sender_clock:
            log_msg += f" | Relógio Recebido: {sender_clock}"
        print(log_msg)

    def receive_message(self, sender_id, event_num, sender_clock):
        """Trata o recebimento de mensagens e atualiza o relógio vetorial."""
        with self.lock:
            # Regra do Relógio Vetorial na recepção:
            # 1. V_i[k] = max(V_i[k], V_msg[k]) para todos os elementos
            # 2. V_i[i] = V_i[i] + 1 (incrementa o evento local de recepção)
            for k in range(self.num_processes):
                self.vector_clock[k] = max(self.vector_clock[k], sender_clock[k])
            
            self.vector_clock[self.process_id] += 1
            
            self.log(
                action_type="[RECEBIMENTO]",
                detail=f"Mensagem de P{sender_id + 1} (Evento #{event_num})",
                sender_clock=sender_clock
            )

    def generate_events(self, ns):
        """Thread responsável por gerar eventos locais e disseminá-los."""
        start_time = time.time()
        
        while time.time() - start_time < RUN_TIME_SECONDS:
            # Aguarda um intervalo aleatório antes de gerar o próximo evento
            time.sleep(random.uniform(1.5, 4.0))
            
            with self.lock:
                # Regra de evento local: incrementa a própria posição do relógio vetorial
                self.vector_clock[self.process_id] += 1
                self.event_counter += 1
                
                current_event = self.event_counter
                clock_snapshot = list(self.vector_clock)
                
                self.log(
                    action_type="[GERAÇÃO EVENTO]",
                    detail=f"Evento Local #{current_event}"
                )

            # Dissemina o evento aos demais processos em segundo plano
            threading.Thread(
                target=self.broadcast_event,
                args=(ns, current_event, clock_snapshot)
            ).start()

    def broadcast_event(self, ns, event_num, clock_snapshot):
        """Envia mensagens para os outros processos com atrasos aleatórios."""
        targets = [i for i in range(self.num_processes) if i != self.process_id]
        random.shuffle(targets)  # Garante ordens de envio variadas

        for target_id in targets:
            # Simula atraso/defasagem aleatória de rede para causar entregas fora de ordem
            delay = random.uniform(0.5, 3.0)
            time.sleep(delay)
            
            try:
                # Localiza a URI do processo destino no Pyro NameServer
                uri = ns.lookup(f"process.P{target_id + 1}")
                target_proxy = Pyro5.api.Proxy(uri)
                
                # Chamada remota para entrega da mensagem
                target_proxy.receive_message(self.process_id, event_num, clock_snapshot)
                target_proxy._pyroRelease()
            except Exception as e:
                print(f"[ERRO] Falha ao enviar de P{self.process_id + 1} para P{target_id + 1}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python process.py <ID_DO_PROCESSO (1 a 4)>")
        sys.exit(1)

    p_num = int(sys.argv[1])
    if p_num < 1 or p_num > NUM_PROCESSES:
        print(f"O ID do processo deve estar entre 1 e {NUM_PROCESSES}.")
        sys.exit(1)

    process_id = p_num - 1

    # Inicializa o Daemon Pyro5[cite: 1]
    daemon = Pyro5.api.Daemon()
    ns = Pyro5.api.locate_ns()  # Conecta ao Pyro Name Server[cite: 1]

    # Instancia o objeto do processo e registra no Pyro[cite: 1]
    node = ProcessNode(process_id)
    uri = daemon.register(node)
    
    # Registra o nome do processo no Name Server (ex: process.P1)[cite: 1]
    process_name = f"process.P{p_num}"
    ns.register(process_name, uri)

    print(f"--- Processo P{p_num} iniciado e registrado como {process_name} ---")

    # Inicia o daemon do Pyro em uma thread para escutar chamadas RPC
    daemon_thread = threading.Thread(target=daemon.requestLoop, daemon=True)
    daemon_thread.start()

    print("Aguardando inicialização de todos os processos (aguardando 5s)...")
    time.sleep(5)

    # Inicia a geração automatizada de eventos[cite: 1, 3]
    print(f"--- Iniciando simulação por {RUN_TIME_SECONDS} segundos ---")
    node.generate_events(ns)

    print(f"--- Fim do tempo estipulado ({RUN_TIME_SECONDS}s) em P{p_num}. Finalizando... ---")
    daemon.shutdown()

if __name__ == "__main__":
    main()