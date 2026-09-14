import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid, parseaddr

from flask import current_app

# Paleta - mismos tokens que ya usa el resto del proyecto (Tailwind
# emerald/slate, decision 2/9), reutilizados tal cual del correo de
# recuperacion de contrasena (decision 54, el primer correo real del
# sistema y punto de referencia visual de este shell).
EMERALD = '#047857'
EMERALD_DARK = '#065f46'
SLATE = '#475569'
SLATE_LIGHT = '#94a3b8'


def format_cop(amount):
    """Mismo formato de pesos colombianos ya usado en el resto del backend
    (ej. notifications/routes.py): separador de miles con punto, sin
    decimales."""
    return f'$ {float(amount):,.0f}'.replace(',', '.')


_MONTHS_ES = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
]


def format_date_es(d):
    return f'{d.day} de {_MONTHS_ES[d.month - 1]} de {d.year}'


def format_datetime_es(dt):
    hour = dt.hour % 12 or 12
    suffix = 'a. m.' if dt.hour < 12 else 'p. m.'
    return f'{format_date_es(dt)}, {hour}:{dt.minute:02d} {suffix}'


def frontend_url(path):
    """Arma un deep-link al frontend (ej. /mis-pedidos/12) para los botones
    "Ver mi pedido/cita" de los correos - FRONTEND_URL nunca fue necesario
    antes (decision 40 lo quito al pasar a codigo de 6 digitos), se
    reintroduce solo para esto."""
    return current_app.config['FRONTEND_URL'].rstrip('/') + path


def render_shell(heading, intro_html, content_html, cta_label=None, cta_url=None):
    """Membrete + tarjeta blanca compartidos por todos los correos
    transaccionales del sistema - cada tipo de correo solo arma su propio
    `content_html` (una tabla, una caja con fecha/hora, etc.), sin repetir
    el HTML del encabezado/pie en cada uno."""
    cta_html = ''
    if cta_label and cta_url:
        cta_html = f"""
          <table role="presentation" cellpadding="0" cellspacing="0" style="margin-top:24px;">
            <tr>
              <td style="background:{EMERALD}; border-radius:10px;">
                <a href="{cta_url}" style="display:inline-block; padding:12px 24px; color:#ffffff; font-size:14px; font-weight:700; text-decoration:none;">{cta_label}</a>
              </td>
            </tr>
          </table>
        """

    return f"""\
<!DOCTYPE html>
<html lang="es">
  <body style="margin:0; padding:32px 16px; background-color:#f1f5f4; font-family:Segoe UI, Helvetica, Arial, sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px; margin:0 auto; background:#ffffff; border-radius:16px; overflow:hidden; border:1px solid #e2e8f0;">
      <tr>
        <td style="background:linear-gradient(135deg, {EMERALD} 0%, {EMERALD_DARK} 100%); padding:28px 32px;">
          <table role="presentation" cellpadding="0" cellspacing="0">
            <tr>
              <td style="width:36px; height:36px; background:rgba(255,255,255,0.15); border-radius:10px; text-align:center; vertical-align:middle; font-size:18px;">🐾</td>
              <td style="padding-left:10px; color:#ffffff; font-size:18px; font-weight:700;">TesaliaVet</td>
            </tr>
          </table>
        </td>
      </tr>
      <tr>
        <td style="padding:32px;">
          <p style="margin:0 0 8px; color:#0f172a; font-size:18px; font-weight:700;">{heading}</p>
          <p style="margin:0 0 20px; color:{SLATE}; font-size:14px; line-height:1.6;">{intro_html}</p>
          {content_html}
          {cta_html}
        </td>
      </tr>
      <tr>
        <td style="padding:18px 32px; background:#f8fafc; border-top:1px solid #e2e8f0;">
          <p style="margin:0; color:{SLATE_LIGHT}; font-size:11.5px; line-height:1.5;">
            Agroveterinaria Tesalia · Tesalia, Huila · Este es un correo automático, no respondas a este mensaje.
          </p>
        </td>
      </tr>
    </table>
  </body>
</html>
"""


def send_email(to_email, subject, html_body, text_body, attachments=None):
    """Envio de bajo nivel compartido por todos los correos transaccionales
    del sistema. Nunca lanza - atrapa y loguea cualquier fallo real de SMTP
    (red caida, credenciales invalidas, adjunto corrupto) para que un correo
    que no se pudo mandar NUNCA tumbe una transaccion ya confirmada (un
    checkout, un pago, una cita) - se llama siempre despues del commit real.
    Devuelve True/False.

    `attachments`: lista opcional de (filename, bytes, mimetype).

    Sin MAIL_USERNAME configurado (mismo criterio que decision 54) se
    loguea en vez de mandar, para poder probar cualquier flujo en
    desarrollo sin credenciales reales."""
    if not current_app.config['MAIL_USERNAME']:
        current_app.logger.info('MAIL_USERNAME no configurado - correo a %s: %s', to_email, subject)
        return False

    try:
        sender = current_app.config['MAIL_DEFAULT_SENDER']

        message = MIMEMultipart('mixed' if attachments else 'alternative')
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = to_email
        # Sin estas dos cabeceras, Gmail y otros proveedores suelen tratar el
        # correo como sospechoso - Message-ID ademas debe usar el dominio
        # real del remitente, no uno inventado (decision 54).
        message['Date'] = formatdate(localtime=True)
        message['Message-ID'] = make_msgid(domain=parseaddr(sender)[1].split('@')[-1])

        if attachments:
            alt = MIMEMultipart('alternative')
            alt.attach(MIMEText(text_body, 'plain'))
            alt.attach(MIMEText(html_body, 'html'))
            message.attach(alt)
            for filename, content, mimetype in attachments:
                part = MIMEApplication(content, _subtype=mimetype.split('/')[-1])
                part.add_header('Content-Disposition', 'attachment', filename=filename)
                message.attach(part)
        else:
            message.attach(MIMEText(text_body, 'plain'))
            message.attach(MIMEText(html_body, 'html'))

        # El sobre SMTP (MAIL FROM) debe ser la direccion pura, sin el nombre
        # de display - mandar "TesaliaVet <correo>" ahi no es estandar y
        # algunos servidores lo rechazan o lo penalizan en el filtro de spam.
        envelope_from = parseaddr(sender)[1]

        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            server.sendmail(envelope_from, [to_email], message.as_string())
        return True
    except Exception:
        current_app.logger.exception('Fallo enviando correo a %s (%s)', to_email, subject)
        return False
