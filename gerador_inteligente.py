import os
import subprocess
from ftplib import FTP

# Configurações via Secrets do GitHub
FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

# Seu link específico do Spotify
SPOTIFY_PLAYLIST_URL = "https://open.spotify.com/playlist/0WwOAlgSwurvLcTKyphVVS" 

def processar_spotify():
    print(f"📡 Iniciando processamento da playlist Spotify...")
    
    # Cria pasta temporária para organização
    if not os.path.exists("downloads"): 
        os.mkdir("downloads")

    # Baixa a playlist completa
    # O spotdl busca o áudio no YouTube e baixa em MP3
    print("📥 Baixando músicas da playlist (isso pode demorar)...")
    subprocess.run([
        'spotdl', 'download', SPOTIFY_PLAYLIST_URL,
        '--output', 'downloads/{title} - {artist}.mp3',
        '--max-results', '1'
    ], check=True)

    # Lista os arquivos MP3 baixados
    musicas_baixadas = [f for f in os.listdir("downloads") if f.endswith(".mp3")]
    musicas_baixadas.sort() # Ordena alfabeticamente
    
    total = len(musicas_baixadas)
    print(f"✅ {total} músicas baixadas. Iniciando conversão e envio FTP...")

    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    
    pasta_remota = "media/musicas"
    
    # Garante que a pasta existe no FTP
    try:
        ftp.mkd("media")
    except:
        pass
    try:
        ftp.mkd(pasta_remota)
    except:
        pass

    for i, arquivo_mp3 in enumerate(musicas_baixadas):
        try:
            num = i + 1
            arquivo_local = os.path.join("downloads", arquivo_mp3)
            # Nome padrão: musica_001.aac, musica_002.aac...
            arquivo_final = f"musica_{num:03d}.aac"
            
            print(f"🚀 [{num}/{total}] Convertendo: {arquivo_mp3}")

            # Conversão para AAC 64k
            subprocess.run([
                'ffmpeg', '-y', '-i', arquivo_local, 
                '-c:a', 'aac', '-b:a', '64k', 
                '-ac', '1', 'temp.aac' # -ac 1 converte para mono (melhor qualidade em 64k)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Envio FTP (Sobrescrevendo arquivos com mesmo nome)
            ftp.cwd("/")
            ftp.cwd(pasta_remota)
            with open('temp.aac', 'rb') as f:
                ftp.storbinary(f"STOR {arquivo_final}", f)
            
            # Limpa o arquivo temporário de conversão
            if os.path.exists("temp.aac"): 
                os.remove("temp.aac")

        except Exception as e:
            print(f"❌ Erro no arquivo {arquivo_mp3}: {e}")

    ftp.quit()
    print("✨ Processo concluído com sucesso!")

if __name__ == "__main__":
    processar_spotify()
