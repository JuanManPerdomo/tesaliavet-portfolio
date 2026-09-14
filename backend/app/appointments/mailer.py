from ..emails.sender import format_datetime_es, frontend_url, render_shell, send_email


def _appointment_url(appointment):
    return frontend_url(f'/mis-citas/{appointment.id}')


def _details_box(appointment):
    pet_name = appointment.pet.name if appointment.pet else 'tu mascota'
    return f"""
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;">
        <tr>
          <td style="padding:16px;">
            <p style="margin:0 0 6px; color:#0f172a; font-size:14px;"><strong>Mascota:</strong> {pet_name}</p>
            <p style="margin:0 0 6px; color:#0f172a; font-size:14px;"><strong>Fecha:</strong> {format_datetime_es(appointment.appointment_datetime)}</p>
            <p style="margin:0; color:#0f172a; font-size:14px;"><strong>Motivo:</strong> {appointment.reason or 'Sin motivo especificado'}</p>
          </td>
        </tr>
      </table>
    """


def send_appointment_created(appointment):
    html = render_shell(
        'Cita agendada',
        f'Hola {appointment.owner.first_name}, tu cita quedó registrada.',
        _details_box(appointment),
        cta_label='Ver mi cita',
        cta_url=_appointment_url(appointment),
    )
    text = (
        f'Hola {appointment.owner.first_name}, tu cita para {appointment.pet.name if appointment.pet else "tu mascota"} '
        f'el {format_datetime_es(appointment.appointment_datetime)} quedó registrada.'
    )
    return send_email(appointment.owner.email, 'Cita agendada - TesaliaVet', html, text)


def send_appointment_confirmed(appointment):
    html = render_shell(
        'Tu cita fue confirmada',
        f'Hola {appointment.owner.first_name}, te esperamos en la fecha acordada.',
        _details_box(appointment),
        cta_label='Ver mi cita',
        cta_url=_appointment_url(appointment),
    )
    text = (
        f'Hola {appointment.owner.first_name}, tu cita del {format_datetime_es(appointment.appointment_datetime)} '
        'fue confirmada.'
    )
    return send_email(appointment.owner.email, 'Cita confirmada - TesaliaVet', html, text)


def send_appointment_cancelled(appointment):
    content_html = _details_box(appointment)
    if appointment.cancel_reason:
        content_html += f"""
          <p style="margin:12px 0 0; padding:14px; background:#fef2f2; border:1px solid #fecaca; border-radius:10px; color:#991b1b; font-size:13px;">
            <strong>Motivo:</strong> {appointment.cancel_reason}
          </p>
        """
    html = render_shell(
        'Cita cancelada',
        f'Hola {appointment.owner.first_name}, tu cita fue cancelada.',
        content_html,
        cta_label='Agendar otra cita',
        cta_url=frontend_url('/mis-citas/agendar'),
    )
    text = f'Hola {appointment.owner.first_name}, tu cita del {format_datetime_es(appointment.appointment_datetime)} fue cancelada.'
    return send_email(appointment.owner.email, 'Cita cancelada - TesaliaVet', html, text)


def send_appointment_reminder(appointment):
    html = render_shell(
        'Recordatorio: tienes una cita mañana',
        f'Hola {appointment.owner.first_name}, te recordamos tu cita en TesaliaVet.',
        _details_box(appointment),
        cta_label='Ver mi cita',
        cta_url=_appointment_url(appointment),
    )
    text = (
        f'Hola {appointment.owner.first_name}, te recordamos tu cita para '
        f'{appointment.pet.name if appointment.pet else "tu mascota"} el '
        f'{format_datetime_es(appointment.appointment_datetime)}.'
    )
    return send_email(appointment.owner.email, 'Recordatorio de cita mañana - TesaliaVet', html, text)
