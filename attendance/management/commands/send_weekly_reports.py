"""
Django management command to send weekly attendance reports to all parents.

Usage:
    python manage.py send_weekly_reports
    python manage.py send_weekly_reports --days 7
    python manage.py send_weekly_reports --student-id 2
    python manage.py send_weekly_reports --dry-run
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q
from datetime import date, timedelta
from collections import defaultdict

from attendance.models import (
    Student, Parent, Attendance, Notification,
)
from attendance.translations import get_translation
from attendance.views import send_notification_email


class Command(BaseCommand):
    help = "Send weekly attendance summaries to all parents"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Number of days to look back (default: 7)",
        )
        parser.add_argument(
            "--student-id",
            type=int,
            help="Send only to this student's parents (for testing)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview without sending emails",
        )

    def handle(self, *args, **options):
        days = options["days"]
        student_id = options.get("student_id")
        dry_run = options.get("dry_run", False)

        today = date.today()
        week_start = today - timedelta(days=days)
        week_end = today

        self.stdout.write(self.style.WARNING(
            f"\n{'=' * 60}\n"
            f"Weekly Attendance Reports\n"
            f"{'=' * 60}\n"
            f"Period: {week_start} → {week_end}\n"
            f"Mode: {'DRY RUN (no emails)' if dry_run else 'LIVE'}\n"
            f"{'=' * 60}\n"
        ))

        # ---- Fetch students ----
        students = Student.objects.select_related(
            "user", "department", "college"
        )

        if student_id:
            students = students.filter(id=student_id)

        total_sent = 0
        total_failed = 0
        total_skipped = 0

        for student in students:
            # Get student's parents
            parents = student.parents.all()

            if not parents.exists():
                total_skipped += 1
                continue

            # Get this week's attendance
            week_records = Attendance.objects.filter(
                student=student,
                date__gte=week_start,
                date__lte=week_end,
            )

            week_total = week_records.count()

            # Get overall attendance (all-time)
            all_records = Attendance.objects.filter(student=student)
            overall_total = all_records.count()
            overall_present = all_records.filter(status="PRESENT").count()

            if week_total == 0:
                # No classes this week — skip
                self.stdout.write(
                    f"  ⏭ {student.register_number}: No records this week. Skipping."
                )
                total_skipped += 1
                continue

            week_present = week_records.filter(status="PRESENT").count()
            week_absent = week_records.filter(status="ABSENT").count()
            week_pct = round((week_present / week_total) * 100, 2)

            if overall_total > 0:
                overall_pct = round((overall_present / overall_total) * 100, 2)
            else:
                overall_pct = 0

            required = student.department.attendance_required

            # ---- Send to each parent ----
            for parent in parents:
                if not parent.receive_email:
                    continue

                # Build message in parent's language
                translation = get_translation(
                    "weekly_summary",
                    parent.preferred_language,
                )

                context = {
                    "parent_name": parent.name,
                    "student_name": student.user.get_full_name() or student.user.username,
                    "register_number": student.register_number,
                    "department": student.department.name,
                    "college": student.college.name,
                    "week_start": str(week_start),
                    "week_end": str(week_end),
                    "present": week_present,
                    "absent": week_absent,
                    "percentage": week_pct,
                    "overall_percentage": overall_pct,
                    "required": required,
                }

                subject = translation["subject"].format(**context)
                message = translation["message"].format(**context)

                self.stdout.write(
                    f"  → {parent.email} ({parent.preferred_language}): "
                    f"{week_pct}% (week) / {overall_pct}% (overall)"
                )

                if dry_run:
                    total_sent += 1
                    continue

                # Create notification record
                notification = Notification.objects.create(
                    recipient=parent,
                    notification_type="WEEKLY_SUMMARY",
                    language=parent.preferred_language,
                    subject=subject,
                    message=message,
                )

                # Send email
                if send_notification_email(notification):
                    total_sent += 1
                else:
                    total_failed += 1

        # ---- Summary ----
        self.stdout.write(self.style.SUCCESS(
            f"\n{'=' * 60}\n"
            f"SUMMARY\n"
            f"{'=' * 60}\n"
            f"✅ Sent:    {total_sent}\n"
            f"❌ Failed:  {total_failed}\n"
            f"⏭ Skipped: {total_skipped}\n"
            f"{'=' * 60}\n"
        ))