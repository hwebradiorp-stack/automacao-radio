import os
import subprocess
import shutil
from ftplib import FTP

# Configurações via Secrets do GitHub
FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

# Seu link específico do Spotify
SPOTIFY_PLAYLIST_URL = "https://open.spotify.com/playlist/0WwOAlgSwurvLcTKyphVVS" 

def processar_spotify():
    print(f"📡 Iniciando processamento da playlist Spotify...")
    
    # Limpa a pasta de downloads se ela já existir de uma rodada anterior
    if os.path.exists("downloads"):
        shutil.rmtree("downloads")
    os.mkdir("downloads")

    print("📥 Baixando músicas da playlist (Aguarde)...")
    try:
        # Removido --max-results (causador do erro)
        # Adicionado --overwrite force para evitar paradas por arquivos existentes
        subprocess.run([
            'spotdl', 'download', SPOTIFY_PLAYLIST_URL,
            '--output', 'downloads/{title} - {artist}.mp3',
            '--format', 'mp3',
            '--bitrate', '128k',
            '--overwrite', 'force'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao baixar playlist: {e}")
        return

    # Lista os arquivos MP3 baixados
    musicas_baixadas = [f for f in os.listdir("downloads") if f.endswith(".mp3")]
    musicas_baixadas.sort() 
    
    total = len(musicas_baixadas)
    if total == 0:
        print("⚠️ Nenhuma música foi baixada. Verifique o link da playlist.")
        return

    print(f"✅ {total} músicas baixadas. Conectando ao FTP...")

    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    
    pasta_remota = "media/musicas"
    
    # Garante estrutura de pastas no FTP
    for pasta in ["media", pasta_remota]:
        try:
            ftp.cwd("/")
            ftp.cwd(pasta)
        except:
            ftp.cwd("/")
            print(f"📁 Criando pasta: {pasta}")
            ftp.mkd(pasta)

    for i, arquivo_mp3 in enumerate(musicas_baixadas):
        try:
            num = i + 1
            arquivo_local = os.path.join("downloads", arquivo_mp3)
            arquivo_final = f"musica_{num:03d}.aac"
            
            print(f"🚀 [{num}/{total}] Convertendo: {arquivo_mp3}")

            # Conversão para AAC 64k Mono (melhor para rádio online)
            subprocess.run([
                'ffmpeg', '-y', '-i', arquivo_local, 
                '-c:a', 'aac', '-b:a', '64k', 
                '-ac', '1', 'temp.aac'
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Envio FTP
            ftp.cwd("/")
            ftp.cwd(pasta_remota)
            with open('temp.aac', 'rb') as f:
                ftp.storbinary(f"STOR {arquivo_final}", f)
            
            if os.path.exists("temp.aac"): 
                os.remove("temp.aac")

        except Exception as e:
            print(f"❌ Erro no processamento de {arquivo_mp3}: {e}")

    ftp.quit()
    print("✨ Sincronização concluída!")

if __name__ == "__main__":
    processar_spotify()
