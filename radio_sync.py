import os
import requests
import subprocess
from ftplib import FTP
import shutil

# Configurações de FTP (GitHub Secrets)
FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

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

def processar_programa(ftp, nome_programa, urls, pasta_destino):
    print(f"\n📢 ATUALIZANDO: {nome_programa} -> Pasta Centova: {pasta_destino}")
    shutil.rmtree(nome_programa, ignore_errors=True)
    os.makedirs(nome_programa, exist_ok=True)
    
    caminho_remoto = f"media/{pasta_destino}/{nome_programa}"
    garantir_pasta_ftp(ftp, caminho_remoto)
    
    for i, url in enumerate(urls, 1):
        # Nomeia os arquivos em sequência para não sobrescrever (bloco 01, 02, 03...)
        nome_arquivo = f"{nome_programa}_bloco{i:02d}.aac"
        arquivo_mp3 = f"{nome_programa}/temp_{i}.mp3"
        arquivo_aac = f"{nome_programa}/{nome_arquivo}"
        
        print(f"  ⬇️ Baixando bloco {i}...")
        try:
            r = requests.get(url, timeout=120, stream=True)
            if r.status_code == 200:
                with open(arquivo_mp3, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Conversão para o padrão Centova (AAC 64k)
                subprocess.run(['ffmpeg', '-y', '-i', arquivo_mp3, '-c:a', 'aac', '-b:a', '64k', arquivo_aac], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                if os.path.exists(arquivo_aac):
                    with open(arquivo_aac, 'rb') as f:
                        ftp.storbinary(f'STOR {nome_arquivo}', f)
                    print(f"  ✅ {nome_arquivo} ENVIADO!")
            else:
                print(f"  ❌ Erro link {i} (Status {r.status_code})")
        except Exception as e:
            print(f"  ⚠️ Falha: {e}")
            
        if os.path.exists(arquivo_mp3): os.remove(arquivo_mp3)
        if os.path.exists(arquivo_aac): os.remove(arquivo_aac)
    
    shutil.rmtree(nome_programa, ignore_errors=True)

if __name__ == "__main__":
    ftp_conn = conectar_ftp()
    
    # --- 1. PROGRAMAS QUE REPETEM (VÃO TODOS PARA 'SEGaSEX') ---

    # Bau Sertanejo
    bau = [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Bau_Sertanejo_SEGaSEX/Bau_sertanejo_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)] + \
          [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Bau_Sertanejo_FimSemana/Bau_sertanejo_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)]
    processar_programa(ftp_conn, "Bau_Sertanejo", bau, "SEGaSEX")

    # Manha Total
    manha = [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Manha_Total_SEGaSEX/Manha_total_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)] + \
            [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Manha_Total_FimSemana/Manha_total_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)]
    processar_programa(ftp_conn, "Manha_Total", manha, "SEGaSEX")

    # Show da Tarde
    show = [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Show_Da_Tarde_V2_SEGaSEX/Show_da_tarde_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 9)] + \
           [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Show_Da_Tarde_V2_FimSemana/Show_da_tarde_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 9)]
    processar_programa(ftp_conn, "Show_da_Tarde", show, "SEGaSEX")

    # Conexao Sertaneja
    conexao = [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Conexao_Sertaneja_SEGaSEX/Conexao_sertaneja_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)] + \
              [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Conexao_Sertaneja_FimSemana/Conexao_sertaneja_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)]
    processar_programa(ftp_conn, "Conexao_Sertaneja", conexao, "SEGaSEX")

    # Toca Tudo
    toca = [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Toca_Tudo_SEGaSEX/Toca_tudo_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)] + \
           [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Toca_Tudo_FimSemana/Toca_tudo_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)]
    processar_programa(ftp_conn, "Toca_Tudo", toca, "SEGaSEX")

    # Falando de Amor
    falando = [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Falando_De_Amor_SEGaSEX/Falando_de_amor_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)] + \
              [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Falando_De_Amor_FimSemana/Falando_de_amor_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)]
    processar_programa(ftp_conn, "Falando_de_Amor", falando, "SEGaSEX")

    # Insonia, Sampagode e As 15 Mais (Tambem para SEGaSEX)
    processar_programa(ftp_conn, "Insonia", [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Insonia_SEGaSEX/Insonia_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)], "SEGaSEX")
    
    sampagode = [f"https://Stm30.srvstm.com:1443/play.php?porta=19480&musica=NOVO_Sampagode_Atuais_SEGaSEX/NOVO_Sampagode_Atuais_bloco{i}.mp3&tipo=programas" for i in range(1, 5)] + \
                [f"https://Stm30.srvstm.com:1443/play.php?porta=19480&musica=NOVO_Sampagode_Atuais_FimSemana/NOVO_Sampagode_Atuais_bloco{i}.mp3&tipo=programas" for i in range(1, 5)]
    processar_programa(ftp_conn, "Sampagode_Atuais", sampagode, "SEGaSEX")

    as15 = [f"https://Stm30.srvstm.com:1443/play.php?porta=19480&musica=As_15_Mais_SEGaSEX/As_15_Mais_bloco{i}.mp3&tipo=programas" for i in range(1, 3)] + \
           [f"https://Stm30.srvstm.com:1443/play.php?porta=19480&musica=As_15_Mais_FimSemana/As_15_Mais_bloco{i}.mp3&tipo=programas" for i in range(1, 3)]
    processar_programa(ftp_conn, "As_15_Mais", as15, "SEGaSEX")

    # --- 2. PROGRAMAS EXCLUSIVOS (VÃO PARA 'FimSemana') ---
    
    processar_programa(ftp_conn, "Pista_Maxima", [f"https://Stm30.srvstm.com:1443/play.php?porta=19480&musica=NOVO_Pista_Maxima_FimSemana/NOVO_Pista_Maxima_bloco{i}.mp3&tipo=programas" for i in range(1, 5)], "FimSemana")
    processar_programa(ftp_conn, "Super_FA", [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Super_FA_FimSemana/Super_fa_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)], "FimSemana")
    processar_programa(ftp_conn, "As_30_Mais", [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=As_30_Mais_FimSemana/As_30_Mais_Bloco_0{i}.mp3&tipo=programa&hash=20260321042210" for i in range(1, 7)], "FimSemana")
    processar_programa(ftp_conn, "Domingao_Total", [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Domingao_Total_FimSemana/Domingao_total_bloco0{i}.mp3&tipo=programa&hash=20260228020036" for i in range(1, 7)], "FimSemana")
    processar_programa(ftp_conn, "Caldeirao_Musical", [f"https://s03.svrdedicado.org:1443/play.php?porta=7520&musica=Caldeirao_musical_FimSemana/Caldeirao_musical_bloco0{i}.mp3&tipo=programa&hash=20260321043748" for i in range(1, 7)], "FimSemana")
    processar_programa(ftp_conn, "Unidos_Pela_Fe", [f"https://stm30.srvstm.com:1443/play.php?porta=19480&musica=GOSPEL_Unidos_Pela_Fe_FimSemana%2FGOSPEL_Unidos_Pela_Fe_bloco{i}.mp3&tipo=programas" for i in range(1, 7)], "FimSemana")

    ftp_conn.quit()
    print("\n--- 🏁 TUDO SINCRONIZADO ---")
