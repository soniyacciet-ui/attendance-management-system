"""
Automated attendance notification system.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from attendance.models import Student, Attendance, Notification
from attendance.views import (
    create_attendance_notification,
    send_notification_email,
)


class Command(BaseCommand):
    help = "Auto-notify parents when students fall below required attendance"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--cooldown", type=int, default=30)
        parser.add_argument("--student-id", type=int)

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        cooldown = options["cooldown"]
        student_id = options.get("student_id")

        now = timezone.now()
        cooldown_cutoff = now - timedelta(days=cooldown)

        self.stdout.write(self.style.WARNING(
            f"\n{'=' * 60}\n"
            f"Auto Notification System\n"
            f"{'=' * 60}\n"
            f"Mode:     {'DRY RUN' if dry_run else 'LIVE'}\n"
            f"Cooldown: {cooldown} days\n"
            f"Time:     {now.strftime('%Y-%m-%d %H:%M')}\n"
            f"{'=' * 60}\n"
        ))

        students = Student.objects.select_related("user", "department", "college")
        if student_id:
            students = students.filter(id=student_id)

        total_sent = 0
        total_failed = 0
        total_skipped = 0
        total_eligible = 0

        for student in students:
            records = Attendance.objects.filter(student=student)
            total = records.count()
            if total == 0:
                continue

            present = records.filter(status="PRESENT").count()
            percentage = round((present / total) * 100, 2)
            required = student.department.attendance_required

            if percentage >= required:
                total_eligible += 1
                continue

            parents = student.parents.all()
            if not parents.exists():
                continue

            is_critical = percentage < (required - 15)
            notif_type = "critical_attendance" if is_critical else "low_attendance"

            student_name = student.user.get_full_name() or student.user.username
            self.stdout.write(
                f"\n  >> {student_name} ({student.register_number}): "
                f"{percentage}% / {required}% - "
                f"{'CRITICAL' if is_critical else 'LOW'}"
            )

            for parent in parents:
                if not parent.receive_email:
                    continue

                recent = Notification.objects.filter(
                    recipient=parent,
                    notification_type=notif_type.upper(),
                    created_at__gte=cooldown_cutoff,
                ).exists()

                if recent:
                    total_skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(
                        f"    [DRY] {parent.email} ({parent.preferred_language})"
                    )
                    total_sent += 1
                    continue

                try:
                    n = create_attendance_notification(
                        parent=parent,
                        student=student,
                        percentage=percentage,
                        required=required,
                        notification_type=notif_type,
                    )
                    if send_notification_email(n):
                        self.stdout.write(f"    [OK] {parent.email} ({parent.preferred_language})")
                        total_sent += 1
                    else:
                        total_failed += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"    [FAIL] {parent.email}: {e}"))
                    total_failed += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n{'=' * 60}\n"
            f"SUMMARY\n"
            f"{'=' * 60}\n"
            f"[OK] Sent:          {total_sent}\n"
            f"[FAIL] Failed:      {total_failed}\n"
            f"[SKIP] Cooldown:    {total_skipped}\n"
            f"[SKIP] Eligible:    {total_eligible}\n"
            f"{'=' * 60}\n"
        ))