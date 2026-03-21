import os
import requests
import subprocess
from ftplib import FTP
import shutil
import re
from datetime import datetime

FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

# Verifica se hoje é Sábado (5) ou Domingo (6)
hoje_fds = datetime.now().weekday() >= 5

def conectar_ftp():
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp

def garantir_pasta_ftp(ftp, caminho_total):
    pastas = caminho_total.split('/')
    ftp.cwd('/')
    for pasta in pastas:
        if not pasta: continue
        try:
            ftp.cwd(pasta)
        except:
            ftp.mkd(pasta)
            ftp.cwd(pasta)

def extrair_nome_programa(url):
    # Pega o nome do programa para a pasta
    match = re.search(r'musica=([a-zA-Z0-9_]+?)(?:_|/|%2F)', url)
    return match.group(1) if match else "Outros"

def extrair_nome_bloco_original(url):
    # Pega o nome do bloco original da URL (ex: Bau_sertanejo_bloco01)
    # Isso garante que o nome seja SEMPRE o mesmo para substituir no Centova
    nome_arquivo = url.split('/')[-1].split('&')[0]
    return nome_arquivo.replace('.mp3', '.aac')

def processar_lista(arquivo_txt, pasta_destino_centova):
    if not os.path.exists(arquivo_txt):
        print(f"⚠️ {arquivo_txt} não encontrado.")
        return

    with open(arquivo_txt, 'r') as f:
        links = [l.strip() for l in f if l.strip() and "http" in l]

    if not links: return

    ftp = conectar_ftp()
    
    for url in links:
        nome_prog = extrair_nome_programa(url)
        # NOME CRÍTICO: Tem que ser igual ao que está na playlist do Centova
        nome_final = extrair_nome_bloco_original(url)
        
        print(f"⬇️ Baixando e Substituindo: {nome_final} em {pasta_destino_centova}")
        
        os.makedirs("temp", exist_ok=True)
        t_mp3, t_aac = "temp/t.mp3", f"temp/{nome_final}"

        try:
            r = requests.get(url, timeout=120, stream=True)
            if r.status_code == 200:
                with open(t_mp3, 'wb') as fm:
                    for c in r.iter_content(8192): fm.write(c)
                
                # Conversão para AAC 64k
                subprocess.run(['ffmpeg', '-y', '-i', t_mp3, '-c:a', 'aac', '-b:a', '64k', t_aac], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                if os.path.exists(t_aac):
                    garantir_pasta_ftp(ftp, f"media/{pasta_destino_centova}/{nome_prog}")
                    # O comando 'STOR' sobrescreve o arquivo se o nome for igual
                    with open(t_aac, 'rb') as fa:
                        ftp.storbinary(f'STOR {nome_final}', fa)
                    print(f"  ✅ {nome_final} substituído com sucesso!")
            else:
                print(f"  ❌ Erro link: {url}")
        except Exception as e:
            print(f"  ⚠️ Falha: {e}")

        if os.path.exists(t_mp3): os.remove(t_mp3)
        if os.path.exists(t_aac): os.remove(t_aac)
    
    ftp.quit()

if __name__ == "__main__":
    if hoje_fds:
        print("📅 PROCESSANDO FINAL DE SEMANA")
        # FDS repetidos -> Pasta SEGaSEX (Substitui o áudio da semana pelo de FDS)
        processar_lista("links_fds_repetidos.txt", "SEGaSEX")
        # FDS exclusivos -> Pasta FimSemana
        processar_lista("links_fds_exclusivo.txt", "FimSemana")
    else:
        print("📅 PROCESSANDO DIA DE SEMANA")
        processar_lista("links_segasex.txt", "SEGaSEX")

    print("\n--- 🏁 SUBSTITUIÇÃO CONCLUÍDA ---")
