import os
import requests
import subprocess
from ftplib import FTP
from bs4 import BeautifulSoup
import re

FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

def extrair_musicas():
    repertorio = []
    urls = [
        "https://www.clubefm.com.br/o-que-tocou",
        "https://saocarlos.clubefm.com.br/o-que-tocou",
        "https://onlineradiobox.com/br/mega/playlist/"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for url in urls:
        try:
            print(f"📡 Lendo: {url}")
            response = requests.get(url, headers=headers, timeout=20)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if "clubefm" in url:
                # Pega textos de títulos e artistas
                for tag in soup.find_all(['h5', 'p']):
                    txt = tag.get_text().strip()
                    if len(txt) > 8 and " " in txt: # Filtro básico para nomes reais
                        repertorio.append(txt)
            
            elif "onlineradiobox" in url:
                for a in soup.select('tr.playlist_item a'):
                    repertorio.append(a.get_text().strip())
                    
        except Exception as e:
            print(f"⚠️ Erro ao acessar {url}: {e}")

    # Remove duplicatas mantendo a ordem
    musicas_unicas = []
    for m in repertorio:
        # Limpa caracteres especiais que atrapalham a busca
        m_limpa = re.sub(r'[^\w\s-]', '', m)
        if m_limpa not in musicas_unicas and len(m_limpa) > 5:
            musicas_unicas.append(m_limpa)
            
    print(f"🎵 {len(musicas_unicas)} músicas encontradas. Usando as 100 melhores.")
    return musicas_unicas[:100]

def processar():
    musicas = extrair_musicas()
    if not musicas: return

    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    
    pasta_remota = "media/musicas"
    try: ftp.mkd(pasta_remota)
    except: pass
    
    for i, nome in enumerate(musicas):
        try:
            num = i + 1
            arquivo_final = f"musica_{num:03d}.aac"
            
            # 1. Download (limitando a duração para evitar arquivos gigantes, ex: sets de 1h)
            subprocess.run([
                'yt-dlp', '--extract-audio', '--audio-format', 'mp3',
                '--match-filter', 'duration < 600', # Pula vídeos com mais de 10 minutos
                f'ytsearch1:{nome}', '-o', 'temp.mp3'
            ], check=True)

            # 2. Conversão AAC 64k
            subprocess.run([
                'ffmpeg', '-y', '-i', 'temp.mp3', '-c:a', 'aac', '-b:a', '64k', 'final.aac'
            ], check=True)

            # 3. FTP Upload
            ftp.cwd("/")
            ftp.cwd(pasta_remota)
            with open('final.aac', 'rb') as f:
                ftp.storbinary(f"STOR {arquivo_final}", f)
            
            print(f"✅ [{num}/100] {arquivo_final} atualizado.")
            
        except Exception as e:
            print(f"❌ Erro em {nome}: {e}")
        
        # Limpeza
        for f in ['temp.mp3', 'final.aac']:
            if os.path.exists(f): os.remove(f)

    ftp.quit()

if __name__ == "__main__":
    processar()
