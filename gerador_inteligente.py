import os
import subprocess
import requests
import google.generativeai as genai
from ftplib import FTP

# Configurações via Secrets do GitHub
FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def obter_playlist_gemini():
    print("🤖 Gemini gerando repertório das rádios Clube FM e Mega FM...")
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = (
        "Gere uma lista de 100 músicas que são os maiores sucessos atuais nas rádios "
        "Clube FM Ribeirão Preto, Clube FM São Carlos e Mega FM. "
        "Foque em Sertanejo, Pisadinha e Hits do momento. "
        "Retorne APENAS os nomes no formato 'Artista - Música', um por linha, sem números ou explicações."
    )

    try:
        response = model.generate_content(prompt)
        linhas = response.text.strip().split('\n')
        # Filtra linhas vazias ou com lixo
        musicas = [l.strip() for l in linhas if len(l) > 5 and "-" in l]
        print(f"✅ Gemini sugeriu {len(musicas)} músicas.")
        return musicas[:100]
    except Exception as e:
        print(f"❌ Erro no Gemini: {e}")
        return []

def processar():
    musicas = obter_playlist_gemini()
    if not musicas:
        print("⚠️ Lista vazia. Verifique a chave da API.")
        return

    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    
    pasta_remota = "media/musicas"
    try: ftp.mkd(pasta_remota)
    except: pass

    for i, nome in enumerate(musicas):
        try:
            num = i + 1
            arquivo_final = f"musica_{num:03d}.aac"
            print(f"🚀 [{num}/100] Baixando: {nome}")

            # Download via yt-dlp
            # --match-filter garante que não pegue vídeos longos (sets/lives)
            subprocess.run([
                'yt-dlp', '--extract-audio', '--audio-format', 'mp3',
                '--match-filter', 'duration < 600 & !is_live', 
                f'ytsearch1:{nome}', '-o', 'temp.mp3'
            ], check=True)

            # Conversão AAC 64k (Alta compressão para economizar espaço)
            subprocess.run([
                'ffmpeg', '-y', '-i', 'temp.mp3', '-c:a', 'aac', '-b:a', '64k', 'final.aac'
            ], check=True)

            # Envio FTP
            ftp.cwd("/")
            ftp.cwd(pasta_remota)
            with open('final.aac', 'rb') as f:
                ftp.storbinary(f"STOR {arquivo_final}", f)
            
            # Limpeza local imediata
            if os.path.exists("temp.mp3"): os.remove("temp.mp3")
            if os.path.exists("final.aac"): os.remove("final.aac")

        except Exception as e:
            print(f"❌ Falha ao processar {nome}: {e}")

    ftp.quit()

if __name__ == "__main__":
    processar()
