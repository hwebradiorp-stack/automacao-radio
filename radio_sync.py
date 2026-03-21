import os
import requests
import subprocess
from ftplib import FTP
import shutil

# Pega as senhas das Secrets que você já criou
FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

# --- SEUS PROGRAMAS ---
PROGRAMAS_SEG_A_SEX = {
    "Bau_Sertanejo": [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Bau_Sertanejo_FimSemana/Bau_sertanejo_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)],
    "Manha_Total": [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Manha_Total_FimSemana/Manha_total_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)],
    "Show_da_Tarde": [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Show_Da_Tarde_V2_FimSemana_FimSemana/Show_da_tarde_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 9)],
    "Conexao_Sertaneja": [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Conexao_Sertaneja_FimSemana/Conexao_sertaneja_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)],
    "Toca_Tudo": [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Toca_Tudo_FimSemana/Toca_tudo_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)],
    "Falando_de_Amor": [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Falando_De_Amor_FimSemana/Falando_de_amor_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)],
    "Sampagode_Atuais": [f"https://Stm30.srvstm.com:1443/play.php?porta=19480&musica=NOVO_Sampagode_Atuais_FimSemana/NOVO_Sampagode_Atuais_bloco{i}.mp3&tipo=programas" for i in range(1, 5)]
}

PROGRAMAS_FIM_SEMANA = {
    "Super_FA": [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Super_FA_FimSemana/Super_fa_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 4)],
    "As_30_Mais": [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=As_30_Mais_FimSemana/As_30_mais_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)],
    "Domingao_Total": [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Domingao_Total_FimSemana/Domingao_total_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)],
    "Caldeirao_Musical": [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Caldeirao_Musical_FimSemana/Caldeirao_musical_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 5)],
    "Unidos_Pela_Fe": ["https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Unidos_Pela_Fe_FimSemana/Unidos_pela_fe_bloco01.mp3&tipo=programa&hash=20260228020036"],
    "60_Minutos": ["https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=60_Minutos_FimSemana/60_minutos_bloco01.mp3&tipo=programa&hash=20260228020036"],
    "Pista_Maxima": [f"https://Stm30.srvstm.com:1443/play.php?porta=19480&musica=NOVO_Pista_Maxima_FimSemana/NOVO_Pista_Maxima_bloco{i}&tipo=programas" for i in range(1, 5)]
}

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

def executar_processo(dicionario_programas, pasta_base_ftp):
    for nome_programa, urls in dicionario_programas.items():
        print(f"\n>>> Processando: {nome_programa}")
        shutil.rmtree(nome_programa, ignore_errors=True)
        os.makedirs(nome_programa, exist_ok=True)

        try:
            ftp = conectar_ftp()
            caminho_ftp = f"media/{pasta_base_ftp}/{nome_programa}"
            garantir_pasta_ftp(ftp, caminho_ftp)
        except Exception as e:
            print(f"Erro FTP: {e}")
            continue

        for i, url in enumerate(urls, 1):
            nome_base = f"{nome_programa}_bloco{i:02d}"
            arquivo_mp3 = f"{nome_programa}/{nome_base}.mp3"
            arquivo_aac = f"{nome_programa}/{nome_base}.aac"
            nome_remoto = f"{nome_base}.aac"

            try:
                r = requests.get(url, timeout=120, stream=True)
                if r.status_code == 200:
                    with open(arquivo_mp3, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    subprocess.run(['ffmpeg', '-y', '-i', arquivo_mp3, '-c:a', 'aac', '-b:a', '64k', arquivo_aac], 
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    if os.path.exists(arquivo_aac):
                        with open(arquivo_aac, 'rb') as f:
                            ftp.storbinary(f'STOR {nome_remoto}', f)
                        print(f"  {nome_base} Enviado")
                else:
                    print(f"  Erro link {i}: {r.status_code}")
            except Exception as e:
                print(f"  Falha no {nome_base}: {e}")
            
            if os.path.exists(arquivo_mp3): os.remove(arquivo_mp3)
            if os.path.exists(arquivo_aac): os.remove(arquivo_aac)

        ftp.quit()
        shutil.rmtree(nome_programa, ignore_errors=True)

if __name__ == "__main__":
    executar_processo(PROGRAMAS_SEG_A_SEX, "SEGaSEX")
    executar_processo(PROGRAMAS_FIM_SEMANA, "FimSemana")
