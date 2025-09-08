"""Script to download the official PDF of Chilean Law 19886 on Public Procurement."""
import requests
from pathlib import Path


def download_ley_19886_oficial():
    """Download the official PDF of Law 19886 from ChileCompra."""
    
    # Official PDF URL found from ChileCompra
    pdf_url = "https://capacitacion.chilecompra.cl/pluginfile.php/166214/mod_folder/content/0/LEY-19886_30-JUL-2003%20(1).pdf"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print("🏛️  Descargando LEY 19886 oficial desde ChileCompra...")
        print(f"URL: {pdf_url}")
        
        response = requests.get(pdf_url, headers=headers, timeout=60)
        response.raise_for_status()
        
        # Check if it's actually a PDF
        content_type = response.headers.get('content-type', '')
        if 'pdf' not in content_type.lower():
            print(f"⚠️  Advertencia: Content-Type es '{content_type}', puede no ser un PDF")
        
        # Save the PDF
        pdf_file = Path("LEY_19886_Compras_Publicas_Chile_OFICIAL.pdf")
        
        with open(pdf_file, 'wb') as f:
            f.write(response.content)
        
        file_size = pdf_file.stat().st_size
        
        print(f"✅ PDF descargado exitosamente!")
        print(f"📄 Archivo: {pdf_file}")
        print(f"📊 Tamaño: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Verify it's a valid PDF by checking magic bytes
        with open(pdf_file, 'rb') as f:
            magic = f.read(4)
            if magic == b'%PDF':
                print("✅ Archivo PDF válido confirmado")
            else:
                print("⚠️  Advertencia: El archivo no parece ser un PDF válido")
        
        return pdf_file
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error descargando el PDF: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None


def download_additional_resources():
    """Download additional public procurement resources."""
    
    additional_urls = [
        {
            'url': 'https://www.chilecompra.cl/wp-content/uploads/2025/01/ppt-compradores-reglamento.pdf',
            'filename': 'Nuevo_Reglamento_Compras_Publicas_2024.pdf',
            'description': 'Nuevo Reglamento de Compras Públicas 2024'
        },
        {
            'url': 'https://capacitacion.chilecompra.cl/pluginfile.php/209045/mod_folder/content/0/PPT. Nuevo Reglamento de Compras Públicas.pdf',
            'filename': 'PPT_Nuevo_Reglamento_Compras_Publicas.pdf',
            'description': 'Presentación del Nuevo Reglamento'
        }
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    downloaded_files = []
    
    for resource in additional_urls:
        try:
            print(f"\n📥 Descargando: {resource['description']}")
            
            response = requests.get(resource['url'], headers=headers, timeout=60)
            response.raise_for_status()
            
            filename = Path(resource['filename'])
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            file_size = filename.stat().st_size
            print(f"✅ Descargado: {filename} ({file_size:,} bytes)")
            downloaded_files.append(filename)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error descargando {resource['description']}: {e}")
        except Exception as e:
            print(f"❌ Error inesperado con {resource['description']}: {e}")
    
    return downloaded_files


if __name__ == "__main__":
    print("🏛️  DESCARGADOR OFICIAL DE LEY DE COMPRAS PÚBLICAS DE CHILE")
    print("=" * 70)
    
    # Download main law
    main_pdf = download_ley_19886_oficial()
    
    if main_pdf:
        print(f"\n✨ LEY 19886 descargada exitosamente: {main_pdf}")
        
        # Download additional resources automatically
        print("\n📚 Descargando recursos adicionales...")
        additional_files = download_additional_resources()
        
        print(f"\n🎉 DESCARGA COMPLETA!")
        print(f"📄 Archivo principal: {main_pdf}")
        if additional_files:
            print("📄 Archivos adicionales:")
            for file in additional_files:
                print(f"   - {file}")
        else:
            print("⚠️  No se pudieron descargar recursos adicionales")
    else:
        print("\n❌ No se pudo descargar la ley principal")
        print("💡 Intenta verificar tu conexión a internet o acceder manualmente a:")
        print("   https://www.chilecompra.cl/normativa/")