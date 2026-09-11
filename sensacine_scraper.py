import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def ejecutar_scraper():
    url = "https://www.sensacine.com.mx/cines/cine/X0V75/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Error HTTP:", response.status_code)
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    peliculas = []

    for card in soup.find_all(['article', 'div'], class_=re.compile(r'card|entity|theater')):
        titulo_elem = card.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'meta-title|title|link'))
        if not titulo_elem:
            continue
            
        titulo = titulo_elem.get_text(strip=True).replace("Compra tu entrada", "").strip()
        
        meta_elem = card.find(['div', 'p', 'span'], class_=re.compile(r'meta|info|sub'))
        detalles_raw = meta_elem.get_text(" | ", strip=True) if meta_elem else "Sin detalles"
        detalles_limpios = detalles_raw.replace("Compra tu entrada", "").strip()
        detalles_final = f"{titulo} | {detalles_limpios}"
        
        horarios_elems = card.find_all(['span', 'a'], class_=re.compile(r'hours|showtime|time|session'))
        horarios = []
        for h in horarios_elems:
            texto_h = h.get_text(strip=True)
            if re.search(r'\d{1,2}:\d{2}', texto_h):
                hora_limpia = re.sub(r'Compra\s*tu\s*entrada', '', texto_h, flags=re.IGNORECASE).strip()
                if hora_limpia and hora_limpia not in horarios:
                    horarios.append(hora_limpia)
        
        if titulo and not any(p['Titulo'] == titulo for p in peliculas):
            peliculas.append({
                "Titulo": titulo,
                "Detalles_Genero_Duracion": detalles_final,
                "Horarios_Funciones": ", ".join(horarios) if horarios else "Sin horarios"
            })

    df = pd.DataFrame(peliculas)
    df.to_csv("cartelera_sensacine.csv", index=False, encoding="utf-8-sig")
    print(f"Scraper finalizado. Peliculas guardadas: {len(df)}")

if __name__ == "__main__":
    ejecutar_scraper()