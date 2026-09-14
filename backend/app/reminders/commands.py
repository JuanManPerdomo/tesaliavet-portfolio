from datetime import date, datetime, timedelta

import click

from ..extensions import db
from ..models import Appointment, Pet, PetVaccination
from ..appointments.mailer import send_appointment_reminder
from ..notifications.routes import VACCINE_ATTENTION_WINDOW_DAYS
from ..pets.mailer import send_vaccine_reminder
from ..pets.routes import _next_vaccine_reminder

REMINDABLE_APPOINTMENT_STATUSES = ('Pendiente', 'Confirmada')


def register_reminder_commands(app):
    """Un solo comando de Flask CLI (sin dependencias nuevas, decision 2/109)
    para los 2 recordatorios que necesitan un job programado en vez de
    reaccionar a una accion puntual (cita 24h antes, vacuna por vencer) -
    pensado para que un scheduler externo (Task Scheduler en desarrollo,
    cron en un servidor real) lo dispare 1 vez al dia. No existe ningun
    scheduler dentro del proceso de Flask."""

    @app.cli.command('send-daily-reminders')
    def send_daily_reminders():
        appt_sent, appt_total = _send_appointment_reminders()
        click.echo(f'Recordatorios de citas: {appt_sent}/{appt_total} enviados')

        vac_sent, vac_total = _send_vaccine_reminders()
        click.echo(f'Recordatorios de vacunas: {vac_sent}/{vac_total} enviados')


def _send_appointment_reminders():
    tomorrow = date.today() + timedelta(days=1)
    start = datetime.combine(tomorrow, datetime.min.time())
    end = start + timedelta(days=1)

    appointments = Appointment.query.filter(
        Appointment.appointment_datetime >= start,
        Appointment.appointment_datetime < end,
        Appointment.status.in_(REMINDABLE_APPOINTMENT_STATUSES),
        Appointment.reminder_sent_at.is_(None),
    ).all()

    sent = 0
    for appointment in appointments:
        if send_appointment_reminder(appointment):
            appointment.reminder_sent_at = datetime.now()
            sent += 1
    db.session.commit()
    return sent, len(appointments)


def _send_vaccine_reminders():
    window_end = date.today() + timedelta(days=VACCINE_ATTENTION_WINDOW_DAYS)
    pets = Pet.query.filter_by(is_active=True).all()

    sent = 0
    checked = 0
    for pet in pets:
        reminder = _next_vaccine_reminder(pet)
        if not reminder:
            continue
        due_date = date.fromisoformat(reminder['nextDueDate'])
        if due_date > window_end:
            continue

        vaccination = PetVaccination.query.get(reminder['id'])
        if not vaccination or vaccination.reminder_sent_at:
            continue

        checked += 1
        if send_vaccine_reminder(pet, reminder):
            vaccination.reminder_sent_at = datetime.now()
            sent += 1
    db.session.commit()
    return sent, checked
