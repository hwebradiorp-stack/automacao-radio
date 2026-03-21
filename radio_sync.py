import os, requests, subprocess
from ftplib import FTP
from datetime import datetime

FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

# Hoje é Sábado (21/03/2026), o script vai rodar os de FDS
hoje_fds = datetime.now().weekday() >= 5

def conectar():
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp

def processar(arquivo_txt, pasta_raiz_centova):
    if not os.path.exists(arquivo_txt): 
        print(f"⚠️ Arquivo {arquivo_txt} nao encontrado.")
        return
    
    with open(arquivo_txt, 'r') as f:
        linhas = [l.strip() for l in f if l.strip() and "http" in l]

    if not linhas: return
    
    ftp = conectar()
    
    for linha in linhas:
        try:
            # Divide: LINK, PASTA_DO_PROGRAMA, NOME_FINAL
            partes = linha.split(',')
            if len(partes) < 3:
                print(f"❌ Linha errada no txt: {linha}. Use: LINK,PASTA,NOME.aac")
                continue
                
            url = partes[0]
            pasta_programa = partes[1] # Ex: Bau_Sertanejo
            nome_final = partes[2]      # Ex: Bau_Sertanejo_bloco01.aac
            
            print(f"🚀 Alvo: {pasta_raiz_centova}/{pasta_programa}/{nome_final}")
            
            # Download rápido
            r = requests.get(url, timeout=60, stream=True)
            if r.status_code == 200:
                with open("t.mp3", 'wb') as fm:
                    for chunk in r.iter_content(8192): fm.write(chunk)
                
                # Conversão AAC 64k
                subprocess.run(['ffmpeg', '-y', '-i', "t.mp3", '-c:a', 'aac', '-b:a', '64k', "t.aac"], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                if os.path.exists("t.aac"):
                    ftp.cwd('/')
                    caminho_alvo = f"media/{pasta_raiz_centova}/{pasta_programa}"
                    
                    try:
                        ftp.cwd(caminho_alvo)
                        with open("t.aac", 'rb') as fa:
                            # STOR substitui o áudio sem deletar o arquivo da playlist
                            ftp.storbinary(f'STOR {nome_final}', fa)
                        print("  ✅ Áudio Substituído!")
                    except:
                        print(f"  ❌ PASTA NÃO EXISTE: {caminho_alvo}")
            
            # Limpa temporários para não gastar espaço do GitHub
            if os.path.exists("t.mp3"): os.remove("t.mp3")
            if os.path.exists("t.aac"): os.remove("t.aac")
            
        except Exception as e:
            print(f"  ⚠️ Erro: {e}")

    ftp.quit()

if __name__ == "__main__":
    if hoje_fds:
        print("📅 RODANDO GRADE DE FIM DE SEMANA")
        # Baixa os de FDS e joga na pasta SEGaSEX (para os repetidos)
        processar("links_fds_repetidos.txt", "SEGaSEX")
        # Baixa os exclusivos e joga na pasta FimSemana
        processar("links_fds_exclusivo.txt", "FimSemana")
    else:
        print("📅 RODANDO GRADE DE SEMANA")
        processar("links_segasex.txt", "SEGaSEX")
