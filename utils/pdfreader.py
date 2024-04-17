import fitz
import re
import os

def upload_pdf(folder):
    data_from_pdf = {}

    for filename in os.listdir(folder):
        if filename.endswith('.pdf'):
            pdf_file = os.path.join(folder, filename)
            data_pdf = extract_data(pdf_file)
            
            if data_pdf:
                siniestro_vehiculo = data_pdf['SINIESTRO VEHICULO']
                data_from_pdf[siniestro_vehiculo] = data_pdf
    return data_from_pdf

def extract_data(pdf_file):
    print("Extracting data from PDF...", pdf_file)
    data = {}
    doc = fitz.open(pdf_file)
    
    # ITERAMOS SOBRE LAS PAGINAS DEL PDF
    for page_number in range(len(doc)):
        # OBTENEMOS EL TEXTO DE LA PAGINA
        page = doc[page_number]
        text = page.get_text()
        lines = text.split('\n')
        
        # INICIALIZAMOS LAS VARIABLES DE RESOLUCION Y DESCRIPCION
        resolucion_text = ""
        descripcion_text = ""
        
        # IETRAMOS SOBRE LAS LINEAS DEL PDF PARA EXTRAER LOS DATOS
        for line in lines:
            if line.startswith('Informe final, solicitud'):
                data['CASO'] = line.split(' ')[-1]
            elif line.startswith('Siniestro N°'):
                data['SINIESTRO VEHICULO'] = line.split(' ')[-1]
            elif line.startswith('Resolucion'):
                resolucion_text = ' '.join(lines[lines.index(line):])
            elif line.startswith('Descripcion'):
                descripcion_text = ' '.join(lines[lines.index(line):])
        
        # CREAMOS UN DICCIONARIO PARA ALMACENAR LOS DATOS DE LA RESOLUCION
        resolucion = {}
        
        # EXTRAEMOS LOS DATOS DE LA RESOLUCION METODO 1
        pattern = r'(ACORDADO CON)\s_+([\w\s]+)[\s_]*(CUIL|CUIT)\s*[(_]*([\d]+)[)_]*\s*MEDIANTE TRANSFERENCIA BANCARIA EN\s*\$?[\s_]*([\d.,]+)\s*-?\.?'
        match_gen = re.search(pattern, resolucion_text, re.IGNORECASE)
        if match_gen:
            resolucion['ACORDADO CON'] = match_gen.group(2).strip()
            resolucion['CUIL/CUIT'] = match_gen.group(4).strip()
            resolucion['MONTO ACORDADO'] = match_gen.group(5).strip().replace(',', '')
        
        # SI EL METODO 1 NO FUNCIONA PROBAMOS CON EL METODO 2
        if match_gen is None:
            pattern = (r'ACORDADO CON\s*([A-Z\s,]+)\s*(CUIL|CUIT)\s*(\d+[\d\-]*)')
            match_gen2 = re.search(pattern, resolucion_text, re.IGNORECASE)
            if match_gen2:
                resolucion['ACORDADO CON'] = match_gen2.group(1).strip()
                resolucion['CUIL/CUIT'] = match_gen2.group(3).strip()
            match2 = re.search(r'MEDIANTE TRANSFERENCIA BANCARIA EN\s*\$([\d\.,]+)', resolucion_text)
            if match2:
                resolucion['MEDIANTE TRANSFERENCIA BANCARIA EN'] = match2.group(1).strip()
        
        # EXTRAEMOS LOS DATOS DE LOS HONORARIOS METODO 1
        pattern = r'(HONORARIOS ACORDADOS CON)\s*([\w\s-]+)(_|\s)*([CUI|CUIT])\s*(_|\s)*([\d]+)(_|\s)*MEDIANTE TRANSFERENCIA BANCARIA EN\s*\$?[\s_]*([\d.,]+)\s*-?\.?'
        match_honorarios = re.search(pattern, descripcion_text, re.IGNORECASE)
        if match_honorarios:
            resolucion['CUIL/CUIT HONORARIOS'] = match_honorarios.group(6)
            resolucion['MONTO HONORARIOS'] = match_honorarios.group(8)

        # SI RESOLUCION ES TRUE AGREGAMOS LOS DATOS A DATA
        if resolucion:
            data['Resolucion'] = resolucion
        
        # SI YA TENEMOS LOS DATOS NECESARIOS SALIMOS DEL LOOP
        if all(key in data for key in ['CASO', 'SINIESTRO VEHICULO', 'Resolucion']):
            break
        
    doc.close()
    return data


folders_pdf = './pdf'
data = upload_pdf(folders_pdf)

for siniestro_vehiculo, data_pdf in data.items():
    print(f'Datos para siniestros {siniestro_vehiculo}:')
    print(data_pdf)