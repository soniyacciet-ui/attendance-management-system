"""
Signals: automatically notify parents when a student's attendance drops.
DEBUG VERSION
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from attendance.models import Attendance, Notification
from attendance.views import (
    create_attendance_notification,
    send_notification_email,
)


@receiver(post_save, sender=Attendance)
@receiver(post_save, sender=Attendance)
def check_attendance_threshold(sender, instance, created, **kwargs):
    """
    When attendance is marked, check if student dropped below required.
    If yes, notify parents with email + AI voice message.
    """
    student = instance.student
    department = student.department
    required = department.attendance_required

    records = Attendance.objects.filter(student=student)
    total = records.count()
    if total == 0:
        return

    present = records.filter(status="PRESENT").count()
    percentage = round((present / total) * 100, 2)

    if percentage >= required:
        return

    # Cooldown
    cutoff = timezone.now() - timedelta(days=30)
    if Notification.objects.filter(
        recipient__student=student,
        created_at__gte=cutoff,
    ).exists():
        return

    is_critical = percentage < (required - 15)
    notif_type = "critical_attendance" if is_critical else "low_attendance"

    parents = student.parents.filter(receive_email=True)
    if not parents.exists():
        return

    # Import here to avoid circular imports
    from attendance.views import (
        create_attendance_notification,
        send_notification_email,
        generate_attendance_voice,
    )

    

# Inside check_attendance_threshold, replace the parents loop:

    for parent in parents:
        try:
        # 1. Create notification record
            notification = create_attendance_notification(
                parent=parent,
                student=student,
                percentage=percentage,
                required=required,
                notification_type=notif_type,
            )

        # 2. Generate the AI voice file
            audio_path = generate_attendance_voice(
                parent=parent,
                student=student,
                percentage=percentage,
                required=required,
                notification_type=notif_type,
            )

        # 3. Send email with audio (if parent wants email)
            if parent.receive_email:
                send_notification_email(notification, audio_path=audio_path)

        except Exception as e:
            print(f"[signal] Failed for {parent.name}: {e}")