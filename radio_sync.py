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
    url_limpa = url.lower()
    # Mapeamento reforçado baseado no seu print do Centova
    # Se o link tiver QUALQUER uma dessas palavras, ele joga na pasta certa
    if "falando" in url_limpa: return "Falando_de_Amor"
    if "15" in url_limpa and "mais" in url_limpa: return "As_15_Mais"
    if "bau" in url_limpa: return "Bau_Sertanejo"
    if "manha" in url_limpa: return "Manha_Total"
    if "show" in url_limpa and "tarde" in url_limpa: return "Show_da_Tarde"
    if "conexao" in url_limpa: return "Conexao_Sertaneja"
    if "toca" in url_limpa: return "Toca_Tudo"
    if "insonia" in url_limpa: return "Insonia"
    if "sampagode" in url_limpa: return "Sampagode_Atuais"
    if "pista" in url_limpa: return "Pista_Maxima"
    if "super" in url_limpa and "fa" in url_limpa: return "Super_FA"
    if "30" in url_limpa and "mais" in url_limpa: return "As_30_Mais"
    if "domingao" in url_limpa: return "Domingao_Total"
    if "caldeirao" in url_limpa: return "Caldeirao_Musical"
    if "unidos" in url_limpa: return "Unidos_Pela_Fe"
    if "60" in url_limpa: return "60_Minutos"
    if "vibe" in url_limpa: return "Vibe_Mix"
    
    return "Outros"

def processar(arquivo_txt, pasta_raiz_centova):
    if not os.path.exists(arquivo_txt): return
    with open(arquivo_txt, 'r') as f:
        links = [l.strip() for l in f if l.strip() and "http" in l]

    if not links: return
    ftp = conectar()
    
    contador_blocos = {}

    for url in links:
        try:
            pasta_programa = mapear_pasta_pelo_link(url)
            
            # Se caiu em "Outros", o script avisa qual link falhou para a gente corrigir
            if pasta_programa == "Outros":
                print(f"⚠️ Link não reconhecido (Pasta Outros): {url}")
                continue

            if pasta_programa not in contador_blocos:
                contador_blocos[pasta_programa] = 1
            else:
                contador_blocos[pasta_programa] += 1
            
            num_bloco = contador_blocos[pasta_programa]
            nome_final = f"{pasta_programa}_bloco{num_bloco:02d}.aac"

            print(f"🚀 Enviando: {pasta_raiz_centova}/{pasta_programa}/{nome_final}")
            
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
                            ftp.storbinary(f'STOR {nome_final}', fa)
                        print(f"  ✅ {nome_final} Atualizado!")
                    except:
                        print(f"  ❌ Pasta não existe no Centova: {caminho_alvo}")
            
            if os.path.exists("t.mp3"): os.remove(t_mp3 if 't_mp3' in locals() else "t.mp3")
            if os.path.exists("t.aac"): os.remove(t_aac if 't_aac' in locals() else "t.aac")
            
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
