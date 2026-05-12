import os
import subprocess
from datetime import datetime

# Configurações do Servidor (Dados fornecidos)
STREAM_FONTE = "https://playerservices.streamtheworld.com/api/livestream-redirect/RT_SP.mp3?dist=SiteTMC"
HOST = "192.99.41.102"
PORTA = "6704"
# No SHOUTcast v1, a senha de transmissão muitas vezes é apenas a senha ou usuario:senha
SENHA = "henridj:1984" 

def transmitir():
    print(f"--- Iniciando Retransmissão Futebol ---")
    print(f"🕒 Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🔗 Fonte: {STREAM_FONTE}")
    print(f"📻 Destino: {HOST}:{PORTA} (AAC 64k)")

    # Comando FFmpeg configurado para SHOUTcast v1 / AAC 64k
    # -re: Lê na velocidade real (essencial para live)
    # -c:a aac -b:a 64k: Converte para AAC 64kbps
    # -f adts: Formato de stream para o SHOUTcast aceitar AAC
    comando = [
        'ffmpeg', '-re', '-i', STREAM_FONTE,
        '-c:a', 'aac', '-b:a', '64k',
        '-f', 'adts', f'icy://{HOST}:{PORTA}'
    ]

    # No SHOUTcast v1, a senha vai no cabeçalho ou via parâmetro de ambiente para o ffmpeg
    # Definindo a senha para o protocolo ICY
    env = os.environ.copy()
    env["ICE_PASS"] = SENHA 

    try:
        # Executa o processo e mostra a saída no terminal do GitHub Actions
        processo = subprocess.run(
            comando, 
            env=env,
            input=f"{SENHA}\n".encode(), # Tenta passar a senha via input se necessário
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na transmissão: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Transmissão interrompida manualmente.")

if __name__ == "__main__":
    transmitir()
