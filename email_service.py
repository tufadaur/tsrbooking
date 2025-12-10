import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import EMAIL_SENDER, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT
from database import get_booking_by_id, get_event_by_id

def send_booking_confirmation_with_pdf(booking_id):
    """Invia email di conferma con testo e logo - senza PDF"""
    booking = get_booking_by_id(booking_id)
    if not booking:
        return "Prenotazione non trovata"
    
    event = get_event_by_id(booking['event_id'])
    if not event:
        return "Evento non trovato"
    
    event_title = event['title']
    event_date = event['date']
    event_time = event['time']
    seats = booking['seats']
    to_email = booking['email']
    name = booking['name']

    subject = f'Biglietto - {event_title}'

    # HTML con logo e dettagli acquisto
    html_body = f"""
    <div style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;'>
        <div style='text-align:center;margin-bottom:30px;'>
            <img src='cid:logo' alt='Teatro San Raffaele' style='max-width:60px;height:auto;'>
        </div>
        
        <h2 style='color:#2d3748;text-align:center;border-bottom:2px solid #744210;padding-bottom:15px;'>
            Conferma Acquisto
        </h2>
        
        <p>Gentile <strong>{name}</strong>,</p>
        
        <p>Ecco i dettagli del suo acquisto:</p>
        
        <div style='background:#f8f9fa;padding:20px;border-radius:8px;margin:20px 0;border-left:4px solid #744210;'>
            <h3 style='color:#744210;margin:0 0 15px 0;font-size:18px;'>{event_title}</h3>
            
            <table style='width:100%;'>
                <tr>
                    <td style='padding:8px 0;font-weight:bold;width:40%;'>Data Spettacolo:</td>
                    <td style='padding:8px 0;color:#2d3748;'>{event_date}</td>
                </tr>
                <tr style='background:#ffffff;'>
                    <td style='padding:8px 0;font-weight:bold;'>Orario:</td>
                    <td style='padding:8px 0;color:#2d3748;'>{event_time}</td>
                </tr>
                <tr>
                    <td style='padding:8px 0;font-weight:bold;'>Posti Riservati:</td>
                    <td style='padding:8px 0;color:#2d3748;'>{seats}</td>
                </tr>
                <tr style='background:#ffffff;'>
                    <td style='padding:8px 0;font-weight:bold;'>Codice Acquisto:</td>
                    <td style='padding:8px 0;color:#744210;font-weight:bold;'>#{booking_id:05d}</td>
                </tr>
            </table>
        </div>
        
        <div style='background:#fff3cd;padding:15px;border-radius:8px;margin:20px 0;border-left:4px solid #ff6b00;'>
            <p style='margin:0;color:#663c00;font-weight:bold;'>⚠️ Istruzioni Importanti:</p>
            <ul style='margin:10px 0 0 20px;color:#663c00;'>
                <li>Presentare il codice acquisto all'ingresso</li>
                <li>Arrivare almeno 10 minuti prima dello spettacolo</li>
                <li>Per informazioni contattare: ilcilindroteatro@yahoo.it</li>
            </ul>
        </div>
        
        <p style='color:#666;margin-top:30px;'>
            Cordiali saluti,<br>
            <strong>Teatro San Raffaele</strong>
        </p>
        
        <div style='background:#f8f9fa;padding:15px;margin-top:30px;border-top:1px solid #e0e0e0;font-size:12px;color:#999;text-align:center;'>
            Questa è un'email automatica, non è necessario rispondere.
        </div>
    </div>
    """

    # Prepara email multipart
    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email

    # Aggiungi testo HTML
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    # Aggiungi logo come immagine inline se esiste
    try:
        import os
        logo_paths = [
            os.path.join(os.path.dirname(__file__), 'static', 'img', 'logo.png'),
            os.path.join(os.getcwd(), 'static', 'img', 'logo.png'),
            'static/img/logo.png'
        ]
        
        logo_found = False
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as attachment:
                    from email.mime.image import MIMEImage
                    img = MIMEImage(attachment.read())
                    img.add_header('Content-ID', '<logo>')
                    img.add_header('Content-Disposition', 'inline', filename='logo.png')
                    msg.attach(img)
                    logo_found = True
                    break
        
        if not logo_found:
            print("Warning: Logo non trovato")
    except Exception as e:
        print(f"Avviso: Impossibile aggiungere logo: {e}")

    # Invia email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        return "Email inviata con successo!"
    except Exception as e:
        return f"Errore invio email: {e}"
