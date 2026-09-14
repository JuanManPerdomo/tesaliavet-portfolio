from ..emails.sender import frontend_url, render_shell, send_email


def send_pqrs_responded(pqrs):
    content_html = f"""
      <p style="margin:0 0 10px; color:#0f172a; font-size:14px;"><strong>Asunto:</strong> {pqrs.subject}</p>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;">
        <tr>
          <td style="padding:16px; color:#0f172a; font-size:14px; line-height:1.6; white-space:pre-line;">{pqrs.response}</td>
        </tr>
      </table>
    """
    html = render_shell(
        'Respondimos tu solicitud',
        f'Hola {pqrs.sender_name}, tenemos una respuesta para tu PQRS.',
        content_html,
        cta_label='Ver detalle',
        cta_url=frontend_url('/notificaciones'),
    )
    text = f'Hola {pqrs.sender_name}, respondimos tu PQRS "{pqrs.subject}":\n\n{pqrs.response}'
    return send_email(pqrs.sender_email, 'Respuesta a tu PQRS - TesaliaVet', html, text)
