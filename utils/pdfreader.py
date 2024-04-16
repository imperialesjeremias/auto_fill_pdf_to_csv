import fitz
import re

pdf_file = './pdf/5.pdf'

def extract_data(pdf_file):
    print("Extracting data from PDF...", pdf_file)
    data = {}
    
    doc = fitz.open(pdf_file)

    # datos a extraer
    # solicitud 84920
    # Siniestro N°
    # Resolucion = [ACORDADO CON, CUIT/CUIL, MONTO ACORDADO]
    
    for page_number in range(len(doc)):
        
        page = doc[page_number]
        text = page.get_text()
        lines = text.split('\n')
        
        resolucion_text = ""
        descripcion_text = ""
        
        for line in lines:
            if line.startswith('Informe final, solicitud'):
                data['CASO'] = line.split(' ')[-1]
                
            elif line.startswith('Siniestro N°'):
                data['SINIESTRO VEHICULO'] = line.split(' ')[-1]
                
            elif line.startswith('Resolucion'):
                resolucion_text = ' '.join(lines[lines.index(line):])
                
            elif line.startswith('Descripcion'):
                descripcion_text = ' '.join(lines[lines.index(line):])

        # Combine resolucion_text and descripcion_text for searching
        combined_text = resolucion_text + " " + descripcion_text
        combined_text = combined_text[:combined_text.find('FECHA DE PAGO')]

        # Extract information
        resolucion = {}
        
        match = re.search(r'ACORDADO CON\s*([A-Z\s,]+)\s*(CUIL|CUIT)\s*(\d+[\d\-]*)', combined_text, re.IGNORECASE)
        if match:
            resolucion['ACORDADO CON'] = match.group(1).strip()
            resolucion['CUIL/CUIT'] = match.group(3).strip()
        
        match = re.search(r'MEDIANTE TRANSFERENCIA BANCARIA EN\s*\$([\d\.,]+)', combined_text)
        if match:
            resolucion['MEDIANTE TRANSFERENCIA BANCARIA EN'] = match.group(1).strip()

        if resolucion:
            data['RESOLUCION'] = resolucion
        
        if all(key in data for key in ['CASO', 'SINIESTRO VEHICULO', 'RESOLUCION']):
            break

    doc.close()
    return data

# Procesar el PDF y extraer los datos
pdf_file = './pdf/5.pdf'
data_extracted = extract_data(pdf_file)
print(data_extracted)
# for key, value in data_extracted.items():
#     print(f"{key}: {value}")
    