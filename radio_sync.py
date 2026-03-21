import os, requests, subprocess, re
from ftplib import FTP
from datetime import datetime

FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

hoje_fds = datetime.now().weekday() >= 5

def conectar():
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp

def mapear_pasta_pelo_link(url):
    # Dicionário baseado exatamente no seu print do Centova
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
        linhas = [l.strip() for l in f if l.strip() and "http" in l]

    if not linhas: return
    ftp = conectar()
    
    for linha in linhas:
        try:
            # Se tiver virgula usa o que vc definiu, se não, faz o automático inteligente
            if "," in linha:
                partes = linha.split(',')
                url, pasta_programa, nome_final = partes[0], partes[1], partes[2]
            else:
                url = linha
                pasta_programa = mapear_pasta_pelo_link(url)
                # Pega o nome do arquivo final da URL e troca mp3 por aac
                nome_bruto = url.split('/')[-1].split('&')[0]
                nome_final = nome_bruto.replace('.mp3', '.aac')
                if not nome_final.endswith('.aac'): nome_final += ".aac"

            print(f"🚀 Processando: {pasta_raiz_centova}/{pasta_programa}/{nome_final}")
            
            r = requests.get(url, timeout=60, stream=True)
            if r.status_code == 200:
                with open("t.mp3", 'wb') as fm:
                    for chunk in r.iter_content(8192): fm.write(chunk)
                
                subprocess.run(['ffmpeg', '-y', '-i', "t.mp3", '-c:a', 'aac', '-b:a', '64k', "t.aac"], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                if os.path.exists("t.aac"):
                    ftp.cwd('/')
                    caminho_alvo = f"media/{pasta_raiz_centova}/{pasta_programa}"
                    try:
                        ftp.cwd(caminho_alvo)
                        with open("t.aac", 'rb') as fa:
                            ftp.storbinary(f'STOR {nome_final}', fa)
                        print(f"  ✅ {nome_final} Atualizado!")
                    except:
                        print(f"  ❌ Pasta não existe no Centova: {caminho_alvo}")
            
            if os.path.exists("t.mp3"): os.remove("t.mp3")
            if os.path.exists("t.aac"): os.remove("t.aac")
        except Exception as e:
            print(f"  ⚠️ Erro: {e}")
    ftp.quit()

if __name__ == "__main__":
    if hoje_fds:
        print("📅 GRADE FDS ATIVA")
        processar("links_fds_repetidos.txt", "SEGaSEX")
        processar("links_fds_exclusivo.txt", "FimSemana")
    else:
        print("📅 GRADE SEMANA ATIVA")
        processar("links_segasex.txt", "SEGaSEX")
