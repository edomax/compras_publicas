"""Script to download Chilean public procurement law from BCN website."""
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
import time
import urllib.parse


def clean_text(text):
    """Clean and format text content."""
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters that might cause issues
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
    return text.strip()


def download_ley_compras_publicas():
    """Download the Chilean public procurement law from BCN."""
    # Try different URLs for the same law
    urls = [
        "https://www.bcn.cl/leychile/navegar?idNorma=213004",
        "https://www.bcn.cl/leychile/navegar?idNorma=213004&idVersion=2023-12-29",
        "https://bcn.cl/2f6wx"  # Short URL that might work better
    ]
    
    session = requests.Session()
    
    # Enhanced headers to look more like a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'es-CL,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    session.headers.update(headers)
    
    for i, url in enumerate(urls):
        try:
            print(f"Intentando URL {i+1}/{len(urls)}: {url}")
            
            # Add a small delay to avoid being flagged as bot
            if i > 0:
                time.sleep(2)
            
            response = session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # Check if we got blocked
            if "demora demasiado" in response.text or "conexin est muy lenta" in response.text:
                print(f"❌ URL {i+1} está bloqueada o requiere JavaScript")
                continue
            
            print(f"✅ URL {i+1} funcionó! Status Code: {response.status_code}")
            break
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error con URL {i+1}: {e}")
            if i == len(urls) - 1:  # Last URL
                raise
    
    response.encoding = 'utf-8'
        
        print(f"Status Code: {response.status_code}")
        print("Procesando contenido HTML...")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the main content
        content_parts = []
        
        # Try to find the law title
        title = soup.find('title')
        if title:
            content_parts.append(f"TÍTULO: {clean_text(title.get_text())}")
            content_parts.append("=" * 80)
            content_parts.append("")
        
        # Look for main content areas
        main_content = soup.find('div', {'id': 'contenido'}) or soup.find('div', {'class': 'contenido'})
        
        if not main_content:
            # Try to find other common content containers
            main_content = soup.find('article') or soup.find('main') or soup.find('body')
        
        if main_content:
            # Extract all text content, preserving some structure
            for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'li', 'td']):
                text = clean_text(element.get_text())
                if text and len(text) > 10:  # Only include meaningful text
                    # Add formatting for headers
                    if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        content_parts.append("")
                        content_parts.append(text.upper())
                        content_parts.append("-" * len(text))
                        content_parts.append("")
                    else:
                        content_parts.append(text)
                        content_parts.append("")
        
        if not content_parts:
            # Fallback: extract all text
            content_parts.append("CONTENIDO EXTRAÍDO (TEXTO COMPLETO):")
            content_parts.append("=" * 50)
            content_parts.append("")
            content_parts.append(clean_text(soup.get_text()))
        
        # Join all content
        full_content = "\n".join(content_parts)
        
        # Save to file
        output_file = Path("ley_compras_publicas_chile.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"LEY DE COMPRAS PÚBLICAS DE CHILE\n")
            f.write(f"Fuente: {url}\n")
            f.write(f"Descargado: {requests.utils.default_headers()}\n")
            f.write("=" * 80 + "\n\n")
            f.write(full_content)
        
        print(f"✅ Ley descargada exitosamente en: {output_file}")
        print(f"📄 Tamaño del archivo: {output_file.stat().st_size:,} bytes")
        
        # Show first few lines as preview
        lines = full_content.split('\n')[:10]
        print("\n📖 Vista previa del contenido:")
        print("-" * 50)
        for line in lines:
            if line.strip():
                print(line[:100] + ("..." if len(line) > 100 else ""))
        
        return output_file
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al descargar la página: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None


if __name__ == "__main__":
    print("🏛️  Descargador de Ley de Compras Públicas de Chile")
    print("=" * 60)
    
    result = download_ley_compras_publicas()
    
    if result:
        print(f"\n✨ Proceso completado. Archivo guardado como: {result}")
    else:
        print("\n❌ No se pudo completar la descarga.")