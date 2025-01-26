from flask import Flask, render_template, request, send_file
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from PyPDF2 import PdfReader, PdfWriter
import io
from datetime import datetime
import locale

app = Flask(__name__)

# Función para convertir la fecha.
def formatear_fecha(fecha_str):
    # Establecer en español.
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    # Convertir la cadena de fecha en un objeto datetime.
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
    # Formatear la fecha 
    fecha_formateada = fecha.strftime('%d de %B del %Y')
    return fecha_formateada

# Función para generar el PDF con el texto sobre un PDF base
def generar_pdf(nombre, fecha):
    # Convertir la fecha al formato deseado
    fecha_formateada = formatear_fecha(fecha)

    # Crear un archivo PDF en memoria
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=landscape(A4))  # A4 horizontal

    # Registrar las fuentes personalizadas
    fuente_nombre_path = os.path.join(os.path.dirname(__file__), 'amsterdamtwottf-ovmee.ttf')  # Fuente para el nombre
    fuente_fecha_path = os.path.join(os.path.dirname(__file__), 'Montserrat-Black.ttf')  # Fuente para la fecha
    
    # Registrar las fuentes
    pdfmetrics.registerFont(TTFont('Amsterdam', fuente_nombre_path))
    pdfmetrics.registerFont(TTFont('MontserratBlack', fuente_fecha_path))

    # Establecer la fuente para el nombre
    can.setFont("Amsterdam", 60)  
    x_nombre = 179.58  # X en puntos.
    y_nombre = 300  # Y en puntos.
    can.drawString(x_nombre, y_nombre, f"{nombre}")

    # Establecer la fuente para la fecha en negrita
    can.setFont("MontserratBlack", 16) 
    x_fecha = 200  # X en puntos.
    y_fecha = 110  # Y en puntos.

    # Dibujar el texto de la fecha
    can.drawString(x_fecha, y_fecha, f"{fecha_formateada}")

    can.save()

    # Leer el PDF de fondo
    base_pdf_path = os.path.join(os.path.dirname(__file__), 'diploma_base.pdf')  # Asegúrate de que este PDF base esté en la carpeta
    reader = PdfReader(base_pdf_path)
    writer = PdfWriter()

    # Agregar la página base del PDF
    base_page = reader.pages[0]

    # Crear un nuevo PDF con la página base y el texto sobrepuesto
    packet.seek(0)
    overlay_pdf = PdfReader(packet)
    overlay_page = overlay_pdf.pages[0]

    # Crear la página combinada (superponer)
    base_page.merge_page(overlay_page)

    # Agregar la página combinada al escritor PDF
    writer.add_page(base_page)

    # Guardar el resultado en un archivo en memoria
    output_pdf = io.BytesIO()
    writer.write(output_pdf)
    output_pdf.seek(0)

    return output_pdf

@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/generar_diploma', methods=['POST'])
def generar_diploma():
    nombre = request.form['nombre']
    fecha = request.form['fecha']

    if not nombre or not fecha:
        return "Faltan datos", 400

    pdf = generar_pdf(nombre, fecha)

    # Crear una respuesta para el archivo PDF
    return send_file(pdf, as_attachment=True, download_name=f"diploma_{nombre.replace(' ', '_')}.pdf", mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)
