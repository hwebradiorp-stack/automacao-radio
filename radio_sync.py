import os, requests, subprocess, re
from ftplib import FTP
from datetime import datetime

FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

# Hoje é Sábado, roda a grade de FDS
hoje_fds = datetime.now().weekday() >= 5

def conectar():
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp

def mapear_pasta_pelo_link(url):
    mapa = {
        "Bau_Sertanejo": "Bau_Sertanejo",
        "Manha_Total": "Manha_Total",
        "Show_Da_Tarde": "Show_da_Tarde",
        "Conexao_Sertaneja": "Conexao_Sertaneja",
        "Toca_Tudo": "Toca_Tudo",
        "Falando_De_Amor": "Falando_de_Amor",
        "Insonia": "Insonia",
        "Sampagode": "Sampagode_Atuais",
        "Pista_Maxima": "Pista_Maxima",
        "Super_fa": "Super_FA",
        "As_30_Mais": "As_30_Mais",
        "Domingao_total": "Domingao_Total",
        "Caldeirao_musical": "Caldeirao_Musical",
        "Unidos_pela_fe": "Unidos_Pela_Fe",
        "60_minutos": "60_Minutos",
        "As_15_Mais": "As_15_Mais",
        "Vibe_mix": "Vibe_Mix"
    }
    for chave, pasta_real in mapa.items():
        if chave.lower() in url.lower():
            return pasta_real
    return "Outros"

def processar(arquivo_txt, pasta_raiz_centova):
    if not os.path.exists(arquivo_txt): return
    with open(arquivo_txt, 'r') as f:
        links = [l.strip() for l in f if l.strip() and "http" in l]

    if not links: return
    ftp = conectar()
    
    # Dicionário para contar os blocos de cada programa na hora de salvar
    contador_blocos = {}

    for url in links:
        try:
            pasta_programa = mapear_pasta_pelo_link(url)
            
            # Gerencia a contagem de blocos (01, 02, 03...)
            if pasta_programa not in contador_blocos:
                contador_blocos[pasta_programa] = 1
            else:
                contador_blocos[pasta_programa] += 1
            
            num_bloco = contador_blocos[pasta_programa]
            # Nomenclatura Padronizada: Nome_Programa_blocoXX.aac
            nome_final = f"{pasta_programa}_bloco{num_bloco:02d}.aac"

            print(f"🚀 Enviando: {pasta_raiz_centova}/{pasta_programa}/{nome_final}")
            
            r = requests.get(url, timeout=60, stream=True)
            if r.status_code == 200:
                with open("t.mp3", 'wb') as fm:
                    for chunk in r.iter_content(8192): fm.write(chunk)
                
                # Conversão para o padrão 64k do Centova
                subprocess.run(['ffmpeg', '-y', '-i', "t.mp3", '-c:a', 'aac', '-b:a', '64k', "t.aac"], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                if os.path.exists("t.aac"):
                    ftp.cwd('/')
                    caminho_alvo = f"media/{pasta_raiz_centova}/{pasta_programa}"
                    try:
                        ftp.cwd(caminho_alvo)
                        with open("t.aac", 'rb') as fa:
                            # STOR sobrescreve o áudio mantendo o nome idêntico
                            ftp.storbinary(f'STOR {nome_final}', fa)
                        print(f"  ✅ {nome_final} Atualizado!")
                    except:
                        print(f"  ❌ Pasta não encontrada no Centova: {caminho_alvo}")
            
            if os.path.exists("t.mp3"): os.remove("t.mp3")
            if os.path.exists("t.aac"): os.remove("t.aac")
            
        except Exception as e:
            print(f"  ⚠️ Erro no link {url}: {e}")
    
    ftp.quit()

if __name__ == "__main__":
    if hoje_fds:
        print("📅 GRADE FIM DE SEMANA")
        processar("links_fds_repetidos.txt", "SEGaSEX")
        processar("links_fds_exclusivo.txt", "FimSemana")
    else:
        print("📅 GRADE SEMANA")
        processar("links_segasex.txt", "SEGaSEX")
