from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


# =====================================================
# LANGUAGE CHOICES
# =====================================================
LANGUAGE_CHOICES = [
    ("en", "English"),
    ("hi", "हिंदी (Hindi)"),
    ("ta", "தமிழ் (Tamil)"),
    ("te", "తెలుగు (Telugu)"),
    ("ml", "മലയാളം (Malayalam)"),
    ("kn", "ಕನ್ನಡ (Kannada)"),
    ("mr", "मराठी (Marathi)"),
    ("bn", "বাংলা (Bengali)"),
    ("gu", "ગુજરાતી (Gujarati)"),
    ("pa", "ਪੰਜਾਬੀ (Punjabi)"),
]



class College(models.Model):
    college_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    attendance_percentage = models.PositiveIntegerField(default=75)

    def __str__(self):
        return self.name


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("HOD", "HOD"),
        ("STAFF", "Staff"),
        ("STUDENT", "Student"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    def __str__(self):
        return f"{self.user.username if self.user else 'No User'} - {self.role}"


class Department(models.Model):
    attendance_required = models.FloatField(default=75.0)
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name="departments",
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)

    def __str__(self):
        if self.college:
            return f"{self.name} - {self.college.name}"
        return f"{self.name} - No College"


class Student(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name="students",
        null=True,
        blank=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="students",
        null=True,
        blank=True
    )

    register_number = models.CharField(max_length=50)

    def __str__(self):
        return self.register_number


class Staff(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name="staff",
        null=True,
        blank=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="staff",
        null=True,
        blank=True
    )

    staff_id = models.CharField(max_length=50)

    def __str__(self):
        return self.staff_id


class HOD(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name="hods",
        null=True,
        blank=True
    )

    department = models.OneToOneField(
        Department,
        on_delete=models.CASCADE,
        related_name="hod",
        null=True,
        blank=True
    )

    def __str__(self):
        if self.user:
            return self.user.username
        return "No User"



class Subject(models.Model):
    """
    A subject taught in a department (e.g., Math, Physics).
    """
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="subjects",
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    hours_per_week = models.PositiveIntegerField(default=4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = [("department", "name")]

    def __str__(self):
        return f"{self.name} ({self.department.name})"



class Period(models.Model):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="periods",
    )
    number = models.PositiveIntegerField(help_text="Period number (1, 2, 3, ...)")
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["number"]
        unique_together = [("department", "number")]

    def __str__(self):
        return f"Period {self.number} ({self.start_time} - {self.end_time})"


class Attendance(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        default="ABSENT"
    )

    marked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marked_attendance"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendances",
    )

    period = models.ForeignKey(
        Period,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendances",
)

    class Meta:
        unique_together = [
            ("student", "date", "subject", "period"),
        ]

    def __str__(self):
        return f"{self.student.register_number} - {self.date} - {self.status}"

    




# =====================================================
# PARENT
# =====================================================
class Parent(models.Model):
    """
    Parent / Guardian linked to a student.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="parent_profile",
        null=True,
        blank=True,
    )
    student = models.ForeignKey(
        "Student",
        on_delete=models.CASCADE,
        related_name="parents",
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    relationship = models.CharField(
        max_length=30,
        choices=[
            ("FATHER", "Father"),
            ("MOTHER", "Mother"),
            ("GUARDIAN", "Guardian"),
        ],
        default="FATHER",
    )
    preferred_language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default="en",
    )
    receive_email = models.BooleanField(default=True)
    receive_sms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    receive_whatsapp = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.student.register_number})"


# =====================================================
# NOTIFICATION
# =====================================================
class Notification(models.Model):
    """
    Notification sent to a parent (or stored in inbox).
    """
    NOTIFICATION_TYPES = [
        ("LOW_ATTENDANCE", "Low Attendance Alert"),
        ("CRITICAL_ATTENDANCE", "Critical Attendance Alert"),
        ("WEEKLY_SUMMARY", "Weekly Summary"),
        ("FRAUD_ALERT", "Fraud Alert"),
        ("CUSTOM", "Custom Message"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SENT", "Sent"),
        ("FAILED", "Failed"),
        ("READ", "Read"),
    ]

    recipient = models.ForeignKey(
        Parent,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
    )
    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default="en",
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_notification_type_display()} → {self.recipient.name}"


class AttendanceAuditLog(models.Model):
    """
    Records every change to attendance for accountability.
    """
    ACTION_CHOICES = [
        ("CREATED", "Created"),
        ("UPDATED", "Updated"),
        ("DELETED", "Deleted"),
    ]

    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_changes",
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    old_status = models.CharField(max_length=10, blank=True)
    new_status = models.CharField(max_length=10, blank=True)
    subject_name = models.CharField(max_length=100, blank=True)
    period_number = models.PositiveIntegerField(null=True, blank=True)
    attendance_date = models.DateField(null=True, blank=True)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Attendance Audit Log"
        verbose_name_plural = "Attendance Audit Logs"

    def __str__(self):
        return (
            f"{self.get_action_display()} - "
            f"{self.student.register_number} - "
            f"{self.created_at:%Y-%m-%d %H:%M}"
        )


class AttendanceDispute(models.Model):
    """
    A student's request to correct an attendance record they believe is wrong.
    """
    STATUS_CHOICES = [
        ("PENDING", "Pending Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        related_name="disputes",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="disputes",
    )
    reason = models.TextField(
        help_text="Why the student believes this record is incorrect"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_disputes",
    )
    review_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("attendance", "student")]

    def __str__(self):
        return f"{self.student.register_number} - {self.status}"


