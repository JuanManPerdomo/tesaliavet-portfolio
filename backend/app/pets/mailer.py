from ..emails.sender import format_date_es, frontend_url, render_shell, send_email


def send_vaccine_reminder(pet, reminder):
    from datetime import date

    due_date = date.fromisoformat(reminder['nextDueDate'])
    status_label = 'ya venció' if reminder['isOverdue'] else 'vence pronto'
    content_html = f"""
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;">
        <tr>
          <td style="padding:16px;">
            <p style="margin:0 0 6px; color:#0f172a; font-size:14px;"><strong>Mascota:</strong> {pet.name}</p>
            <p style="margin:0 0 6px; color:#0f172a; font-size:14px;"><strong>Vacuna:</strong> {reminder['vaccineName']}</p>
            <p style="margin:0; color:#0f172a; font-size:14px;"><strong>Fecha:</strong> {format_date_es(due_date)} ({status_label})</p>
          </td>
        </tr>
      </table>
    """
    html = render_shell(
        'Recordatorio de vacuna',
        f'Hola {pet.owner.first_name}, la vacuna de {pet.name} {status_label}.',
        content_html,
        cta_label='Agendar cita',
        cta_url=frontend_url('/mis-citas/agendar'),
    )
    text = (
        f'Hola {pet.owner.first_name}, la vacuna {reminder["vaccineName"]} de {pet.name} '
        f'{status_label} ({format_date_es(due_date)}).'
    )
    return send_email(pet.owner.email, f'Recordatorio de vacuna - {pet.name} - TesaliaVet', html, text)
