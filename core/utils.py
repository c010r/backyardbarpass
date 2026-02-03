import qrcode
import os
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage

def generar_qr_entrada(entrada_id):
    """
    Genera una imagen QR para una entrada específica y devuelve un ContentFile.
    El QR contiene el UUID de la entrada.
    """
    # Creamos el objeto QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # El contenido del QR es el ID único de la entrada
    qr.add_data(str(entrada_id))
    qr.make(fit=True)

    # Creamos la imagen (usando Pillow)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardamos en un buffer de memoria
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    filename = f"qr_{entrada_id}.png"
    
    return ContentFile(buffer.getvalue(), name=filename)

def enviar_email_entradas(orden):
    """
    Envía un correo electrónico HTML al cliente con sus entradas embebidas como CID.
    """
    cliente = orden.cliente
    evento = orden.evento
    entradas = orden.entradas.all()
    
    subject = f"🎟️ Tus entradas para {evento.titulo} - Backyard Bar"
    
    # Preparamos los datos de las entradas con CID para el template
    entradas_con_cid = []
    for i, entrada in enumerate(entradas):
        cid = f"qr_entrada_{entrada.id}_{i}"
        entradas_con_cid.append({
            'cid': cid,
            'id_resumido': str(entrada.id)[:8].upper(),
            'entrada_obj': entrada
        })
    
    # Contexto para el template
    context = {
        'cliente': cliente,
        'evento': evento,
        'orden': orden,
        'entradas_con_cid': entradas_con_cid,
        'frontend_url': settings.FRONTEND_URL
    }
    
    # Renderizar el HTML
    html_content = render_to_string('emails/confirmacion_entrada.html', context)
    text_content = strip_tags(html_content) # Versión en texto plano
    
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [cliente.email],
    )
    email.attach_alternative(html_content, "text/html")
    
    # Adjuntar y enlazar cada QR como CID
    for item in entradas_con_cid:
        entrada = item['entrada_obj']
        if entrada.imagen_qr:
            try:
                # Leer el contenido del archivo QR
                entrada.imagen_qr.open('rb')
                img_data = entrada.imagen_qr.read()
                entrada.imagen_qr.close()
                
                # Crear el objeto MIMEImage
                img = MIMEImage(img_data)
                img.add_header('Content-ID', f'<{item["cid"]}>')
                img.add_header('Content-Disposition', 'inline', filename=f"qr_{entrada.id}.png")
                
                # Adjuntar al email
                email.attach(img)
                
            except Exception as e:
                print(f"No se pudo embeber el QR {entrada.id}: {e}")
            
    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Error enviando email: {str(e)}")
        return False
