import os
import subprocess
from datetime import datetime

# Configurações do Servidor
STREAM_FONTE = "https://playerservices.streamtheworld.com/api/livestream-redirect/RT_SP.mp3?dist=SiteTMC"
HOST = "192.99.41.102"
PORTA = "6704"
USUARIO = "henridj"
SENHA = "1984"

def transmitir():
    print("--- Iniciando Retransmissão Futebol ---")
    print(f"🕒 Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🔗 Fonte: {STREAM_FONTE}")
    print(f"📻 Destino: {HOST}:{PORTA} (AAC 64k)")

    # Formatação completa com autenticação para SHOUTcast / Icecast
    destino_stream = f"icy://{USUARIO}:{SENHA}@{HOST}:{PORTA}"

    # Comando FFmpeg configurado para retransmissão
    comando = [
        'ffmpeg',
        '-re',
        '-i', STREAM_FONTE,
        '-c:a', 'aac',
        '-b:a', '64k',
        '-f', 'adts',
        destino_stream
    ]

    try:
        subprocess.run(comando, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na transmissão: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Transmissão interrompida manualmente.")

if __name__ == "__main__":
    transmitir()
