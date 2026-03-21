import os
import requests
import subprocess
from ftplib import FTP
import shutil
from datetime import datetime

FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

hoje_fds = datetime.now().weekday() >= 5

def conectar_ftp():
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp

def processar_lista(arquivo_txt, pasta_raiz_centova):
    if not os.path.exists(arquivo_txt):
        print(f"⚠️ {arquivo_txt} nao encontrado.")
        return

    with open(arquivo_txt, 'r') as f:
        linhas = [l.strip() for l in f if l.strip() and "http" in l]

    if not linhas: return

    ftp = conectar_ftp()
    
    for linha in linhas:
        # Divide o link do nome do arquivo (Link,Nome_do_Arquivo.aac)
        if "," in linha:
            url, nome_final = linha.split(',')
        else:
            # Se você esquecer a vírgula, ele tenta pegar o final da URL
            url = linha
            nome_final = url.split('/')[-1].split('&')[0].replace('.mp3', '.aac')
        
        # O script vai extrair o nome da pasta PAI pelo nome do arquivo
        # Ex: Bau_sertanejo_bloco01.aac -> pasta Bau_Sertanejo
        nome_programa = nome_final.split('_bloco')[0] if '_bloco' in nome_final else "Outros"

        print(f"🚀 Enviando {nome_final} para media/{pasta_raiz_centova}/{nome_programa}")
        
        os.makedirs("temp", exist_ok=True)
        t_mp3, t_aac = "temp/t.mp3", f"temp/{nome_final}"

        try:
            r = requests.get(url, timeout=120, stream=True)
            if r.status_code == 200:
                with open(t_mp3, 'wb') as fm:
                    for c in r.iter_content(8192): fm.write(c)
                
                subprocess.run(['ffmpeg', '-y', '-i', t_mp3, '-c:a', 'aac', '-b:a', '64k', t_aac], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                if os.path.exists(t_aac):
                    # Navega direto para a pasta que já existe
                    caminho_remoto = f"media/{pasta_raiz_centova}/{nome_programa}"
                    try:
                        ftp.cwd('/')
                        ftp.cwd(caminho_remoto)
                        with open(t_aac, 'rb') as fa:
                            ftp.storbinary(f'STOR {nome_final}', fa)
                        print(f"  ✅ Substituido!")
                    except:
                        print(f"  ❌ Pasta {caminho_remoto} nao existe no Centova!")
            else:
                print(f"  ❌ Link OFF: {url}")
        except Exception as e:
            print(f"  ⚠️ Erro: {e}")

        if os.path.exists(t_mp3): os.remove(t_mp3)
        if os.path.exists(t_aac): os.remove(t_aac)
    
    ftp.quit()

if __name__ == "__main__":
    if hoje_fds:
        processar_lista("links_fds_repetidos.txt", "SEGaSEX")
        processar_lista("links_fds_exclusivo.txt", "FimSemana")
    else:
        processar_lista("links_segasex.txt", "SEGaSEX")
