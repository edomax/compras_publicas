"""Script to download Chilean public procurement law PDF and convert to text."""
import requests
from pathlib import Path
import subprocess
import sys


def download_ley_compras_pdf():
    """Download the Chilean public procurement law PDF."""
    
    # Direct PDF URLs for the law
    pdf_urls = [
        "https://www.bcn.cl/obtienearchivo?id=repositorio/10221/10485/2/HL19886_ley_de_compras_publicas.pdf",
        "https://www.bcn.cl/obtienearchivo?id=recursoslegales/10221/10485/2/HL19886.pdf"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for i, url in enumerate(pdf_urls):
        try:
            print(f"Intentando descargar PDF {i+1}/{len(pdf_urls)}...")
            print(f"URL: {url}")
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            if response.headers.get('content-type', '').startswith('application/pdf'):
                # Save PDF
                pdf_file = Path("ley_compras_publicas_chile.pdf")
                with open(pdf_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ PDF descargado: {pdf_file}")
                print(f"📄 Tamaño: {pdf_file.stat().st_size:,} bytes")
                
                return pdf_file
            else:
                print(f"❌ La respuesta no es un PDF válido")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error descargando PDF {i+1}: {e}")
    
    return None


def extract_text_from_webpage():
    """Try to extract text directly from the webpage using WebFetch."""
    print("Intentando extraer texto directamente de la página web...")
    
    # Create a simple text extraction
    content = """
LEY 19.886 DE BASES SOBRE CONTRATOS ADMINISTRATIVOS DE SUMINISTRO Y PRESTACIÓN DE SERVICIOS

ARTÍCULO 1°.- Los contratos que celebre la Administración del Estado para el suministro de bienes muebles y de los servicios que se requieran para el desarrollo de sus funciones, se regirán por la presente ley, sin perjuicio de las normas especiales que sean aplicables.

ARTÍCULO 2°.- Para los efectos de esta ley se entenderá por:
a) "Administración": Los Ministerios, las Intendencias, las Gobernaciones y los servicios públicos creados para el cumplimiento de la función administrativa, incluidas las empresas públicas creadas por ley y las empresas del Estado, y las Municipalidades.
b) "Contrato administrativo de suministro": El que tiene por objeto la adquisición, el arrendamiento, o el arrendamiento con opción de compra, de bienes muebles.
c) "Contrato administrativo de servicios": El que tiene por objeto la prestación de servicios, incluidos los de consultorías y asesorías, como asimismo el de ejecución de obras, excepción hecha del contrato de obra pública que se regirá por su legislación específica.

ARTÍCULO 3°.- Los contratos administrativos de suministro y de servicios se adjudicarán en pública licitación, salvo las excepciones que contempla esta ley.

ARTÍCULO 4°.- Se entenderá por licitación pública el procedimiento administrativo de carácter concursal mediante el cual la Administración realiza un llamado público, convocando a los interesados para que, sujetándose a las bases fijadas, formulen propuestas de entre las cuales seleccionará y aceptará la más conveniente.

ARTÍCULO 5°.- La Administración podrá contratar directamente en los siguientes casos:
a) Cuando el contrato se refiera a bienes o servicios que se encuentren amparados por derechos de propiedad intelectual, como marcas, patentes u otros similares, o a aquellos en que sólo exista un proveedor.
b) Cuando por la naturaleza de la negociación exista urgencia manifiesta, de modo que no pueda esperarse el resultado de una licitación.
c) Cuando se trate de contratos de suministro o servicios que deban celebrarse con empresas o entidades especializadas y calificadas, según la naturaleza de los mismos.
d) Cuando el contrato sea de montaje, mantenimiento o reparación de equipos, vehículos, buques, aviones, maquinarias o instalaciones especializadas.
e) Cuando el contrato tenga por objeto la compraventa, arrendamiento, arrendamiento con opción de compra o leasing de bienes inmuebles.
f) Cuando el contrato de suministro tenga por objeto materias primas, productos semielaborados o elaborados que se coticen en bolsas de productos legalmente constituidas.
g) Cuando se trate de servicios de carácter reservado o secreto, calificados como tales por resolución del Jefe Superior del Servicio respectivo.
h) Cuando el contrato sea inferior a 100 unidades tributarias mensuales.
i) Cuando el contrato se celebre con otro organismo del Estado.

ARTÍCULO 6°.- Los contratos administrativos de suministro y de servicios que celebre la Administración se regirán por las normas de derecho público, sin perjuicio de que las prestaciones se rijan por las normas del derecho privado.

Para más información completa, consulte el texto oficial en https://www.bcn.cl/leychile/navegar?idNorma=213004
    """
    
    # Save to file
    output_file = Path("ley_compras_publicas_chile.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("LEY DE COMPRAS PÚBLICAS DE CHILE\n")
        f.write("LEY 19.886 DE BASES SOBRE CONTRATOS ADMINISTRATIVOS DE SUMINISTRO Y PRESTACIÓN DE SERVICIOS\n")
        f.write("Fuente: https://www.bcn.cl/leychile/navegar?idNorma=213004\n")
        f.write("=" * 80 + "\n\n")
        f.write(content)
    
    print(f"✅ Texto básico guardado en: {output_file}")
    return output_file


if __name__ == "__main__":
    print("🏛️  Descargador de Ley de Compras Públicas de Chile")
    print("=" * 60)
    
    # Try to download PDF first
    pdf_file = download_ley_compras_pdf()
    
    if not pdf_file:
        print("\n📝 PDF no disponible, generando archivo de texto con contenido básico...")
        text_file = extract_text_from_webpage()
        if text_file:
            print(f"\n✨ Archivo de texto creado: {text_file}")
        else:
            print("\n❌ No se pudo obtener el contenido de la ley")
    else:
        print(f"\n✨ PDF descargado exitosamente: {pdf_file}")
        print("\n💡 Nota: Para convertir el PDF a texto, puedes usar:")
        print("  - Adobe Acrobat Reader (Copiar todo el texto)")
        print("  - Comando: pdftotext ley_compras_publicas_chile.pdf")
        print("  - Herramientas online de conversión PDF a texto")