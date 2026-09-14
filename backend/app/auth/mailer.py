from ..emails.sender import frontend_url, render_shell, send_email


def send_password_reset_code(to_email, code):
    content_html = f"""
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background:#f0fdf6; border:1.5px solid #bbf0d5; border-radius:12px; padding:20px; text-align:center;">
            <span style="font-family:'Courier New', monospace; font-size:34px; font-weight:700; letter-spacing:10px; color:#065f46;">{code}</span>
          </td>
        </tr>
      </table>
      <p style="margin:20px 0 0; color:#94a3b8; font-size:13px; line-height:1.6;">
        Este código es válido por <strong style="color:#475569;">10 minutos</strong>. Si no fuiste tú quien lo solicitó, puedes ignorar este correo — tu contraseña seguirá igual.
      </p>
    """
    html = render_shell(
        'Restablecer tu contraseña',
        'Recibimos una solicitud para restablecer tu contraseña en TesaliaVet. Usa el siguiente código para continuar:',
        content_html,
    )
    text = (
        'Recibimos una solicitud para restablecer tu contraseña en TesaliaVet.\n\n'
        f'Tu código de verificación es: {code}\n\n'
        'Es válido por 10 minutos. Si no fuiste tú, puedes ignorar este correo.'
    )
    return send_email(to_email, 'Tu código de verificación - TesaliaVet', html, text)


def send_welcome(user):
    content_html = """
      <ul style="margin:0; padding-left:18px; color:#475569; font-size:14px; line-height:1.9;">
        <li>Agenda citas veterinarias en minutos</li>
        <li>Lleva el historial clínico y las vacunas de tus mascotas</li>
        <li>Compra productos y sigue tus pedidos</li>
      </ul>
    """
    html = render_shell(
        f'¡Bienvenido, {user.first_name}!',
        'Tu cuenta en TesaliaVet ya está lista. Desde aquí puedes:',
        content_html,
        cta_label='Ir a mi cuenta',
        cta_url=frontend_url('/'),
    )
    text = (
        f'¡Bienvenido a TesaliaVet, {user.first_name}!\n\n'
        'Tu cuenta ya está lista: agenda citas, lleva el historial clínico y las vacunas de tus mascotas, '
        'y compra productos siguiendo tus pedidos.'
    )
    return send_email(user.email, 'Bienvenido a TesaliaVet', html, text)
