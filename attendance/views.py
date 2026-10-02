from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import College, UserProfile, Department, Student, Staff, HOD, Attendance
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
from .ml_model import predict_attendance_risk
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak

)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages as django_messages
from django.http import HttpResponse
import calendar
from datetime import date, timedelta
import json
from django.utils import timezone
from .translations import get_translation
from .models import Parent, Notification
from .models import Subject  
from .models import Period 
import os
import csv
from django.db import transaction
from django.http import HttpResponse

from .utils.excel_import import (
    build_template_workbook,
    build_error_report,
    parse_and_validate,
    StudentRow,
    ParentRow,
)





def home(request):
    return render(request, "home.html")


def signup(request):
    """
    Signup creates:
    1. A new User
    2. A brand new College (only for this admin)
    3. A UserProfile linking them as ADMIN of that college
    """
    if request.method == "POST":
        login_id = request.POST.get("login_id", "").strip()
        password = request.POST.get("password", "")
        college_name = request.POST.get("college_name", "").strip()
        college_id = request.POST.get("college_id", "").strip()
        email = request.POST.get("email", "").strip()

        # Validation
        errors = []
        if not login_id:
            errors.append("Login ID is required.")
        if not password:
            errors.append("Password is required.")
        if not college_name:
            errors.append("College Name is required.")
        if not college_id:
            errors.append("College ID is required.")

        if User.objects.filter(username=login_id).exists():
            errors.append("This Login ID is already registered.")

        if College.objects.filter(college_id=college_id).exists():
            errors.append("This College ID is already registered.")

        if errors:
            return render(request, "signup.html", {
                "error": " ".join(errors),
                "login_id": login_id,
                "college_name": college_name,
                "college_id": college_id,
                "email": email,
            })

        # 1. Create the College
        college = College.objects.create(
            college_id=college_id,
            name=college_name,
            email=email,
            attendance_percentage=75,
        )

        # 2. Create the User
        user = User.objects.create_user(
            username=login_id,
            password=password,
            email=email,
        )

        # 3. Create UserProfile linking user to THIS college as ADMIN
        UserProfile.objects.create(
            user=user,
            college=college,
            role="ADMIN",
        )

        return redirect("login")

    return render(request, "signup.html")



def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Get user's role
            try:
                role = user.userprofile.role

            except Exception as e:
                return render(request, "login.html", {
                    "error": f"Profile error: {e}"
                })

            # Redirect according to role
            if role == "ADMIN":
                return redirect("admin_dashboard")

            elif role == "HOD":
                return redirect("hod_dashboard")

            elif role == "STAFF":
                return redirect("staff_dashboard")

            elif role == "STUDENT":
                return redirect("student_dashboard")

            else:
                return render(request, "login.html", {
                    "error": "Unknown user role."
                })

        else:

            return render(request, "login.html", {
                "error": "Invalid username or password."
            })

    return render(request, "login.html")

from django.http import JsonResponse
from django.db.models import Count, Q


@login_required
def admin_dashboard(request):
    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    college = profile.college

    # Initial counts (used on page load)
    students = Student.objects.filter(college=college).count()
    staff = Staff.objects.filter(college=college).count()
    departments = Department.objects.filter(college=college).count()
    hods = HOD.objects.filter(college=college).count()

    # Today's attendance %
    from datetime import date
    today = date.today()
    today_records = Attendance.objects.filter(
        student__college=college,
        date=today,
    )
    today_total = today_records.count()
    today_present = today_records.filter(status="PRESENT").count()
    today_pct = round((today_present / today_total) * 100, 1) if today_total > 0 else 0

    return render(request, "admin_dashboard.html", {
        "college": college,
        "students": students,
        "staff": staff,
        "departments": departments,
        "hods": hods,
        "today_pct": today_pct,
    })


# =====================================================
# LIVE STATS API
# =====================================================
@login_required
def admin_stats_api(request):
    """
    Returns live stats as JSON for real-time dashboard updates.
    """
    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return JsonResponse({"error": "unauthorized"}, status=403)

    college = profile.college

    students = Student.objects.filter(college=college).count()
    staff = Staff.objects.filter(college=college).count()
    departments = Department.objects.filter(college=college).count()

    from datetime import date
    today = date.today()
    today_records = Attendance.objects.filter(
        student__college=college,
        date=today,
    )
    today_total = today_records.count()
    today_present = today_records.filter(status="PRESENT").count()
    today_pct = round((today_present / today_total) * 100, 1) if today_total > 0 else 0

    return JsonResponse({
        "students": students,
        "staff": staff,
        "departments": departments,
        "today_pct": today_pct,
        "timestamp": timezone.now().isoformat(),
    })

@login_required
def manage_students(request):
    profile = request.user.userprofile

    # Only college admin can access
    if profile.role != "ADMIN":
        return redirect("home")

    college = profile.college

    # Get only this admin's college students
    students = Student.objects.filter(
        college=college
    ).select_related(
        "user",
        "department"
    )

    return render(
        request,
        "manage_students.html",
        {
            "students": students,
            "college": college,
        }
    )

@login_required
def manage_departments(request):
    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    departments = Department.objects.filter(
        college=profile.college
    )

    return render(
        request,
        "manage_departments.html",
        {
            "departments": departments,
            "college": profile.college,
        }
    )


@login_required
def department_details(request, department_id):
    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    department = get_object_or_404(
        Department,
        id=department_id,
        college=profile.college
    )

    students = Student.objects.filter(
        department=department,
        college=profile.college
    ).select_related("user")

    staff = Staff.objects.filter(
        department=department,
        college=profile.college
    ).select_related("user")

    hod = HOD.objects.filter(
        department=department,
        college=profile.college
    ).select_related("user").first()

    return render(
        request,
        "department_details.html",
        {
            "department": department,
            "students": students,
            "staff": staff,
            "hod": hod,
        }
    )




def home(request):
    return render(request, "home.html")

@login_required
def add_student(request, department_id):

    profile = request.user.userprofile

    # Only college admin can add students
    if profile.role != "ADMIN":
        return redirect("home")

    # Make sure department belongs to admin's college
    department = get_object_or_404(
        Department,
        id=department_id,
        college=profile.college
    )

    if request.method == "POST":

        name = request.POST.get("name")
        register_number = request.POST.get("register_number")
        password = request.POST.get("password")

        # Check duplicate register number
        if Student.objects.filter(
            register_number=register_number
        ).exists():

            return render(
                request,
                "add_student.html",
                {
                    "department": department,
                    "error": "This register number already exists."
                }
            )

        # Create Django User
        user = User.objects.create_user(
            username=register_number,
            password=password,
            first_name=name
        )

        # Create UserProfile
        UserProfile.objects.create(
            user=user,
            college=profile.college,
            role="STUDENT"
        )

        # Create Student
        Student.objects.create(
            user=user,
            college=profile.college,
            department=department,
            register_number=register_number
        )

        return redirect(
            "department_details",
            department_id=department.id
        )

    return render(
        request,
        "add_student.html",
        {
            "department": department
        }
    )
@login_required
def add_department(request):

    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    if request.method == "POST":

        name = request.POST.get("name")

        Department.objects.create(
            college=profile.college,
            name=name
        )

        return redirect("manage_departments")

    return render(request, "add_department.html")


@login_required
def department_details(request, department_id):

    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    department = get_object_or_404(
        Department,
        id=department_id,
        college=profile.college
    )

    students = Student.objects.filter(
        department=department,
        college=profile.college
    )

    staff = Staff.objects.filter(
        department=department,
        college=profile.college
    )

    hod = HOD.objects.filter(
        department=department,
        college=profile.college
    ).first()

    return render(
        request,
        "department_details.html",
        {
            "college": profile.college,
            "department": department,
            "students": students,
            "staff": staff,
            "hod": hod,
        }
    )

@login_required
def add_staff(request, department_id):

    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    department = get_object_or_404(
        Department,
        id=department_id,
        college=profile.college
    )

    if request.method == "POST":

        name = request.POST.get("name")
        staff_id = request.POST.get("staff_id")
        password = request.POST.get("password")

        # Check duplicate Staff ID
        if Staff.objects.filter(staff_id=staff_id).exists():

            return render(
                request,
                "add_staff.html",
                {
                    "department": department,
                    "college": profile.college,
                    "error": "This Staff ID already exists."
                }
            )

        # Create login account
        user = User.objects.create_user(
            username=staff_id,
            password=password,
            first_name=name
        )

        # Create Staff record
        Staff.objects.create(
            user=user,
            college=profile.college,
            department=department,
            staff_id=staff_id
        )

        # Create profile
        UserProfile.objects.create(
            user=user,
            college=profile.college,
            role="STAFF"
        )

        return redirect(
            "department_details",
            department_id=department.id
        )

    return render(
        request,
        "add_staff.html",
        {
            "department": department,
            "college": profile.college
        }
    )

@login_required
def add_hod(request, department_id):

    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    department = get_object_or_404(
        Department,
        id=department_id,
        college=profile.college
    )

    # Check whether this department already has an HOD
    if HOD.objects.filter(department=department).exists():
        return render(
            request,
            "add_hod.html",
            {
                "department": department,
                "college": profile.college,
                "error": "This department already has an HOD."
            }
        )

    if request.method == "POST":

        name = request.POST.get("name")
        hod_id = request.POST.get("hod_id")
        password = request.POST.get("password")

        # Check duplicate username
        if User.objects.filter(username=hod_id).exists():

            return render(
                request,
                "add_hod.html",
                {
                    "department": department,
                    "college": profile.college,
                    "error": "This HOD ID already exists."
                }
            )

        # Create Django login account
        user = User.objects.create_user(
            username=hod_id,
            password=password,
            first_name=name
        )

        # Create HOD
        HOD.objects.create(
            user=user,
            college=profile.college,
            department=department
        )

        # Create profile
        UserProfile.objects.create(
            user=user,
            college=profile.college,
            role="HOD"
        )

        return redirect(
            "department_details",
            department_id=department.id
        )

    return render(
        request,
        "add_hod.html",
        {
            "department": department,
            "college": profile.college
        }
    )

@login_required
def edit_staff(request, staff_id):

    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    staff = get_object_or_404(
        Staff,
        id=staff_id,
        college=profile.college
    )

    if request.method == "POST":

        name = request.POST.get("name")
        new_staff_id = request.POST.get("staff_id")

        # Check if another staff already uses this ID
        if Staff.objects.filter(
            staff_id=new_staff_id
        ).exclude(id=staff.id).exists():

            return render(
                request,
                "edit_staff.html",
                {
                    "staff": staff,
                    "error": "This Staff ID already exists."
                }
            )

        staff.staff_id = new_staff_id
        staff.user.username = new_staff_id
        staff.user.first_name = name

        staff.user.save()
        staff.save()

        return redirect(
            "department_details",
            department_id=staff.department.id
        )

    return render(
        request,
        "edit_staff.html",
        {
            "staff": staff
        }
    )
@login_required
def delete_staff(request, staff_id):

    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    staff = get_object_or_404(
        Staff,
        id=staff_id,
        college=profile.college
    )

    department_id = staff.department.id

    if request.method == "POST":

        user = staff.user

        staff.delete()
        user.delete()

        return redirect(
            "department_details",
            department_id=department_id
        )

    return render(
        request,
        "delete_staff.html",
        {
            "staff": staff
        }
    )



@login_required
def edit_student(request, student_id):

    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    student = get_object_or_404(
        Student,
        id=student_id,
        college=profile.college
    )

    if request.method == "POST":

        name = request.POST.get("name")
        register_number = request.POST.get("register_number")

        # Duplicate register number check (unchanged logic)
        if Student.objects.filter(
            register_number=register_number
        ).exclude(id=student.id).exists():

            return render(
                request,
                "edit_student.html",
                {
                    "student": student,
                    "error": "This register number already exists."
                }
            )

        # ---- Update Student scalar fields ----
        student.register_number = register_number
        student.email = request.POST.get("email", student.email or "")
        student.phone = request.POST.get("phone", student.phone or "")
        student.gender = request.POST.get("gender", student.gender or "")
        student.section = request.POST.get("section", student.section or "")

        year_raw = request.POST.get("year", "").strip()
        if year_raw:
            try:
                student.year = int(year_raw)
            except ValueError:
                pass

        dob_raw = request.POST.get("dob", "").strip()
        if dob_raw:
            from datetime import datetime as _dt
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    student.dob = _dt.strptime(dob_raw, fmt).date()
                    break
                except ValueError:
                    continue

        # ---- Update User ----
        student.user.first_name = name
        student.user.username = register_number
        student.user.save()
        student.save()

        # ---- Handle parents (max 2) ----
        # Existing Parent rows for this student, ordered by id
        existing = list(student.parents.order_by("id"))

        # Parent 1 & Parent 2 fields come from the form
        submitted = []
        for i in (1, 2):
            p_name = request.POST.get(f"parent{i}_name", "").strip()
            p_email = request.POST.get(f"parent{i}_email", "").strip()
            p_phone = request.POST.get(f"parent{i}_phone", "").strip()
            p_rel = request.POST.get(f"parent{i}_relationship", "FATHER").strip()

            if not (p_name or p_email or p_phone):
                continue

            submitted.append({
                "name": p_name,
                "email": p_email,
                "phone": p_phone,
                "relationship": p_rel or "FATHER",
            })

        # Enforce max 2
        submitted = submitted[:2]

        # Update or create
        for idx, data in enumerate(submitted):
            if idx < len(existing):
                p = existing[idx]
                p.name = data["name"]
                p.email = data["email"]
                p.phone = data["phone"]
                p.relationship = data["relationship"]
                p.save()
            else:
                Parent.objects.create(
                    student=student,
                    name=data["name"],
                    email=data["email"],
                    phone=data["phone"],
                    relationship=data["relationship"],
                    preferred_language="en",
                    receive_email=True,
                )

        # Delete extra parents beyond what was submitted (keep at most 2)
        for p in existing[len(submitted):]:
            p.delete()

        return redirect(
            "department_details",
            department_id=student.department.id
        )

    # ---- GET: build context with existing parents ----
    parents = list(student.parents.order_by("id"))
    parent1 = parents[0] if len(parents) > 0 else None
    parent2 = parents[1] if len(parents) > 1 else None

    return render(
        request,
        "edit_student.html",
        {
            "student": student,
            "parent1": parent1,
            "parent2": parent2,
        }
    )


@login_required
def delete_student(request, student_id):

    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    student = get_object_or_404(
        Student,
        id=student_id,
        college=profile.college
    )

    department_id = student.department.id

    if request.method == "POST":

        user = student.user

        student.delete()
        user.delete()

        return redirect(
            "department_details",
            department_id=department_id
        )

    return render(
        request,
        "delete_student.html",
        {
            "student": student
        }
    )

def department_students(request, department_id):

    department = get_object_or_404(
        Department,
        id=department_id
    )

    students = Student.objects.filter(
        department=department
    )

    college = department.college

    return render(
        request,
        "department_students.html",
        {
            "department": department,
            "students": students,
            "college": college,
        }
    )


def department_staff(request, department_id):

    department = get_object_or_404(
        Department,
        id=department_id
    )

    staff = department.staff.all()

    return render(
        request,
        'department_staff.html',
        {
            'department': department,
            'staff': staff,
            'college': department.college
        }
    )


def department_hod(request, department_id):
    department = get_object_or_404(
        Department,
        id=department_id
    )

    hod = HOD.objects.filter(
        department=department
    ).first()

    return render(
        request,
        "department_hod.html",
        {
            "department": department,
            "college": department.college,
            "hod": hod,
        }
    )

@login_required
def admin_dashboard(request):

    if not hasattr(request.user, "userprofile"):
        return redirect("login")

    if request.user.userprofile.role != "ADMIN":
        return redirect("login")

    return render(request, "admin_dashboard.html")


# =====================================================
# XAI HELPER FUNCTIONS
# =====================================================

def get_eligibility_reasons(
    total_classes,
    attended_classes,
    absent_classes,
    attendance_percentage,
    required_percentage
):
    """
    XAI: Explain WHY the student is eligible or not eligible.
    Returns a list of reason strings.
    """
    reasons = []

    if total_classes == 0:
        reasons.append("No attendance has been recorded yet.")
        return reasons

    if attendance_percentage >= required_percentage:
        gap = round(attendance_percentage - required_percentage, 2)
        reasons.append(
            f"Your attendance ({attendance_percentage}%) is "
            f"{gap}% above the required {required_percentage}%."
        )
        reasons.append(
            f"You attended {attended_classes} out of {total_classes} classes."
        )
        if attended_classes == total_classes:
            reasons.append("Perfect attendance! You have not missed any classes.")
    else:
        gap = round(required_percentage - attendance_percentage, 2)
        reasons.append(
            f"Your attendance ({attendance_percentage}%) is "
            f"{gap}% below the required {required_percentage}%."
        )
        reasons.append(
            f"You missed {absent_classes} out of {total_classes} classes."
        )
        # How many classes needed to reach requirement
        classes_needed = int(
            (required_percentage * total_classes / 100) - attended_classes
        ) + 1
        if classes_needed > 0:
            reasons.append(
                f"You need to attend {classes_needed} more classes "
                f"to reach the requirement."
            )

    return reasons


def detect_attendance_anomalies(student):
    """
    XAI: Detect unusual attendance patterns.
    Returns list of dicts: {type, icon, title, detail}.
    """
    anomalies = []

    records = Attendance.objects.filter(student=student).order_by("-date")

    if records.count() < 5:
        return anomalies

    all_records = list(records)

    # ---- Anomaly 1: Sudden change in recent attendance ----
    recent = all_records[:5]
    recent_present = sum(1 for r in recent if r.status == "PRESENT")
    recent_rate = recent_present / len(recent) * 100

    older = all_records[5:15]
    if older:
        older_present = sum(1 for r in older if r.status == "PRESENT")
        older_rate = older_present / len(older) * 100
        diff = recent_rate - older_rate

        if abs(diff) >= 40:
            if diff > 0:
                anomalies.append({
                    "type": "IMPROVEMENT",
                    "icon": "fa-arrow-trend-up",
                    "title": "Strong Improvement Detected",
                    "detail": (
                        f"Your attendance improved by {abs(diff):.0f}% "
                        f"in the last 5 classes "
                        f"(from {older_rate:.0f}% to {recent_rate:.0f}%)."
                    ),
                })
            else:
                anomalies.append({
                    "type": "DECLINE",
                    "icon": "fa-arrow-trend-down",
                    "title": "Sudden Drop Detected",
                    "detail": (
                        f"Your attendance dropped by {abs(diff):.0f}% "
                        f"in the last 5 classes "
                        f"(from {older_rate:.0f}% to {recent_rate:.0f}%)."
                    ),
                })

    # ---- Anomaly 2: Consecutive absences ----
    consecutive = 0
    max_consecutive = 0
    for r in reversed(all_records):  # oldest first
        if r.status == "ABSENT":
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            consecutive = 0

    if max_consecutive >= 3:
        anomalies.append({
            "type": "STREAK",
            "icon": "fa-triangle-exclamation",
            "title": f"{max_consecutive} Consecutive Absences",
            "detail": (
                f"You were absent for {max_consecutive} classes in a row. "
                f"This significantly lowered your attendance."
            ),
        })

    # ---- Anomaly 3: Day-of-week pattern ----
    day_absences = {}
    day_totals = {}

    for r in all_records:
        day = r.date.strftime("%A")
        day_totals[day] = day_totals.get(day, 0) + 1
        if r.status == "ABSENT":
            day_absences[day] = day_absences.get(day, 0) + 1

    for day, total in day_totals.items():
        if total >= 3:
            absent = day_absences.get(day, 0)
            rate = absent / total * 100
            if rate >= 60:
                anomalies.append({
                    "type": "PATTERN",
                    "icon": "fa-calendar-day",
                    "title": f"Pattern: High Absence on {day}s",
                    "detail": (
                        f"You missed {absent} out of {total} classes "
                        f"on {day}s ({rate:.0f}% absence rate)."
                    ),
                })

    return anomalies


def generate_student_recommendations(
    student,
    attendance_percentage,
    required_percentage
):
    """
    XAI: Personalized recommendations based on data.
    Returns list of dicts: {type, icon, title, detail}.
    """
    recommendations = []

    records = Attendance.objects.filter(student=student).order_by("-date")

    if records.count() == 0:
        return recommendations

    all_records = list(records)

    # ---- Recommendation 1: Recent trend ----
    recent = all_records[:5]
    if recent:
        recent_present = sum(1 for r in recent if r.status == "PRESENT")
        recent_rate = recent_present / len(recent) * 100

        if recent_rate >= 80 and attendance_percentage < required_percentage:
            recommendations.append({
                "type": "POSITIVE",
                "icon": "fa-fire",
                "title": "Great Recent Momentum",
                "detail": (
                    f"Your recent attendance ({recent_rate:.0f}%) is much "
                    f"better than your average ({attendance_percentage}%). "
                    f"Keep this up to reach {required_percentage}%."
                ),
            })

        elif recent_rate < 50 and attendance_percentage >= required_percentage:
            recommendations.append({
                "type": "WARNING",
                "icon": "fa-bell",
                "title": "Declining Trend — Act Now",
                "detail": (
                    f"Your recent attendance ({recent_rate:.0f}%) has dropped "
                    f"sharply. Maintain your standing before it falls below "
                    f"the requirement."
                ),
            })

    # ---- Recommendation 2: Day-of-week focus ----
    day_absences = {}
    day_totals = {}
    for r in all_records:
        day = r.date.strftime("%A")
        day_totals[day] = day_totals.get(day, 0) + 1
        if r.status == "ABSENT":
            day_absences[day] = day_absences.get(day, 0) + 1

    worst_day = None
    worst_rate = 0
    for day, total in day_totals.items():
        if total >= 3:
            absent = day_absences.get(day, 0)
            rate = absent / total * 100
            if rate > worst_rate:
                worst_rate = rate
                worst_day = day

    if worst_day and worst_rate >= 50:
        recommendations.append({
            "type": "INSIGHT",
            "icon": "fa-calendar-week",
            "title": f"Focus on {worst_day}s",
            "detail": (
                f"You miss {worst_rate:.0f}% of classes on {worst_day}s. "
                f"Improving {worst_day} attendance will boost your average."
            ),
        })

    # ---- Recommendation 3: Action needed ----
    if attendance_percentage < required_percentage:
        total = len(all_records)
        attended = sum(1 for r in all_records if r.status == "PRESENT")
        classes_needed = int(
            (required_percentage * total / 100) - attended
        ) + 1

        if classes_needed > 0:
            recommendations.append({
                "type": "ACTION",
                "icon": "fa-bullseye",
                "title": "Attend the Next Few Classes",
                "detail": (
                    f"Attend {classes_needed} consecutive classes to reach "
                    f"the {required_percentage}% requirement."
                ),
            })

    # ---- Recommendation 4: Perfect attendance praise ----
    if attendance_percentage == 100:
        recommendations.append({
            "type": "POSITIVE",
            "icon": "fa-trophy",
            "title": "Perfect Attendance!",
            "detail": (
                "You have attended every single class. Outstanding commitment!"
            ),
        })

    return recommendations


# =====================================================
# UPDATED student_dashboard VIEW
# =====================================================

@login_required
def student_dashboard(request):

    try:
        student = Student.objects.select_related(
            "user",
            "department",
            "college"
        ).get(user=request.user)

    except Student.DoesNotExist:
        return render(request, "student_not_configured.html")

    # ---------------------------------------------
    # ATTENDANCE RECORDS
    # ---------------------------------------------
    attendance_records = Attendance.objects.filter(student=student)

    total_classes = attendance_records.count()
    attended_classes = attendance_records.filter(status="PRESENT").count()
    absent_classes = attendance_records.filter(status="ABSENT").count()

    # ---------------------------------------------
    # ATTENDANCE PERCENTAGE
    # ---------------------------------------------
    if total_classes > 0:
        attendance_percentage = round(
            (attended_classes / total_classes) * 100, 2
        )
    else:
        attendance_percentage = 0

    # ---------------------------------------------
    # REQUIRED ATTENDANCE
    # ---------------------------------------------
    required_percentage = student.department.attendance_required

    # ---------------------------------------------
    # ELIGIBILITY
    # ---------------------------------------------
    if total_classes == 0:
        eligibility = "NO ATTENDANCE"
    elif attendance_percentage >= required_percentage:
        eligibility = "ELIGIBLE"
    else:
        eligibility = "NOT ELIGIBLE"

    # ---------------------------------------------
    # XAI: ELIGIBILITY REASONS
    # ---------------------------------------------
    eligibility_reasons = get_eligibility_reasons(
        total_classes,
        attended_classes,
        absent_classes,
        attendance_percentage,
        required_percentage,
    )

    # ---------------------------------------------
    # AI PREDICTION (SHAP)
    # ---------------------------------------------
    prediction = 0
    risk_probability = 0
    shap_explanations = []

    if total_classes > 0:
        (
            prediction,
            risk_probability,
            shap_explanations
        ) = predict_attendance_risk(attendance_percentage)

    if prediction == 1:
        risk_status = "AT RISK"
    else:
        risk_status = "SAFE"

    # ---------------------------------------------
    # XAI: ANOMALIES
    # ---------------------------------------------
    anomalies = detect_attendance_anomalies(student)

    # ---------------------------------------------
    # XAI: RECOMMENDATIONS
    # ---------------------------------------------
    recommendations = generate_student_recommendations(
        student,
        attendance_percentage,
        required_percentage,
    )

    # ---------------------------------------------
    # SEND DATA TO HTML
    # ---------------------------------------------
    return render(
        request,
        "student_dashboard.html",
        {
            "student": student,
            "total_classes": total_classes,
            "attended_classes": attended_classes,
            "absent_classes": absent_classes,
            "attendance_percentage": attendance_percentage,
            "required_percentage": required_percentage,
            "eligibility": eligibility,
            "eligibility_reasons": eligibility_reasons,
            "risk_status": risk_status,
            "risk_probability": round(risk_probability * 100, 2),
            "shap_explanations": shap_explanations,
            "anomalies": anomalies,
            "recommendations": recommendations,
        }
    )



@login_required
def mark_attendance(request, department_id):
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    department = get_object_or_404(
        Department, id=department_id, college=profile.college
    )

    students = Student.objects.filter(
        department=department
    ).select_related("user").order_by("register_number")

    subjects = Subject.objects.filter(department=department, is_active=True)
    periods = Period.objects.filter(department=department, is_active=True)

    if not subjects.exists() or not periods.exists():
        return render(request, "mark_attendance.html", {
            "department": department,
            "students": students,
            "subjects": subjects,
            "periods": periods,
            "no_subjects": not subjects.exists(),
            "no_periods": not periods.exists(),
        })

    if request.method == "POST":
        attendance_date = request.POST.get("date")
        subject_id = request.POST.get("subject")
        period_id = request.POST.get("period")

        subject = get_object_or_404(Subject, id=subject_id, department=department)
        period = get_object_or_404(Period, id=period_id, department=department)

        for student in students:
            status = request.POST.get(f"attendance_{student.id}")

            if status in ["PRESENT", "ABSENT"]:

                # Check if record already exists
                existing = Attendance.objects.filter(
                    student=student,
                    date=attendance_date,
                    subject=subject,
                    period=period,
                ).first()

                if existing:
                    # Update case
                    if existing.status != status:
                        old_status = existing.status
                        existing.status = status
                        existing.marked_by = request.user
                        existing.save()

                        # Log the change
                        log_attendance_change(
                            attendance=existing,
                            student=student,
                            user=request.user,
                            action="UPDATED",
                            old_status=old_status,
                            new_status=status,
                        )
                else:
                    # Create case
                    new_record = Attendance.objects.create(
                        student=student,
                        date=attendance_date,
                        subject=subject,
                        period=period,
                        status=status,
                        marked_by=request.user,
                    )

                    # Log the creation
                    log_attendance_change(
                        attendance=new_record,
                        student=student,
                        user=request.user,
                        action="CREATED",
                        new_status=status,
                    )

        django_messages.success(
            request,
            f"✓ Attendance saved: {subject.name} — "
            f"Period {period.number} ({period.start_time:%H:%M} - {period.end_time:%H:%M})"
        )
        return redirect("mark_attendance", department_id=department.id)

    from datetime import date
    return render(request, "mark_attendance.html", {
        "department": department,
        "students": students,
        "subjects": subjects,
        "periods": periods,
        "today": date.today(),
    })



@login_required
def staff_dashboard(request):
    profile = request.user.userprofile

    if profile.role != "STAFF":
        return redirect("home")

    departments = Department.objects.filter(
        college=profile.college
    )

    # XAI: insights per department
    department_insights = []
    for dept in departments:
        dept_xai = get_department_insights(dept)
        department_insights.append({
            "department": dept,
            "xai": dept_xai,
        })

    return render(
        request,
        "staff_dashboard.html",
        {
            "profile": profile,
            "departments": departments,
            "department_insights": department_insights,
        }
    )

@login_required
def attendance_settings(request, department_id):
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    department = get_object_or_404(
        Department,
        id=department_id,
        college=profile.college
    )

    if request.method == "POST":
        try:
            required = float(
                request.POST.get("attendance_required")
            )

            if required < 0 or required > 100:
                raise ValueError

            department.attendance_required = required
            department.save(
                update_fields=["attendance_required"]
            )

            return redirect(
                "attendance_settings",
                department_id=department.id
            )

        except (TypeError, ValueError):
            return render(
                request,
                "attendance_settings.html",
                {
                    "department": department,
                    "error": "Enter a percentage between 0 and 100."
                }
            )

    return render(
        request,
        "attendance_settings.html",
        {
            "department": department
        }
    )

@login_required
def change_hod(request, department_id):

    profile = request.user.userprofile

    # Only ADMIN can change HOD
    if profile.role != "ADMIN":
        return redirect("home")

    # Get department belonging to this college
    department = get_object_or_404(
        Department,
        id=department_id,
        college=profile.college
    )

    # Get current HOD
    current_hod = HOD.objects.filter(
        department=department
    ).first()

    # If no HOD exists, send to Add HOD
    if not current_hod:
        return redirect(
            "add_hod",
            department_id=department.id
        )

    if request.method == "POST":

        name = request.POST.get("name")
        hod_id = request.POST.get("hod_id")
        password = request.POST.get("password")

        # Check if new HOD ID belongs to another user
        existing_user = User.objects.filter(
            username=hod_id
        ).exclude(
            id=current_hod.user.id
        ).first()

        if existing_user:
            return render(
                request,
                "change_hod.html",
                {
                    "department": department,
                    "college": profile.college,
                    "hod": current_hod,
                    "error": "This HOD ID already exists."
                }
            )

        # Update existing HOD's login account
        current_hod.user.username = hod_id
        current_hod.user.first_name = name

        if password:
            current_hod.user.set_password(password)

        current_hod.user.save()

        return redirect(
            "department_details",
            department_id=department.id
        )

    return render(
        request,
        "change_hod.html",
        {
            "department": department,
            "college": profile.college,
            "hod": current_hod
        }
    )


def detect_attendance_anomalies(student):
    """
    Detect and explain unusual attendance patterns.
    Returns list of (flag, explanation).
    """
    anomalies = []
    
    records = Attendance.objects.filter(
        student=student
    ).order_by("date")
    
    if records.count() < 5:
        return anomalies
    
    # --- Anomaly 1: Sudden change in attendance ---
    recent = list(records[:5])
    recent_present = sum(1 for r in recent if r.status == "PRESENT")
    recent_rate = recent_present / len(recent) * 100
    
    older = list(records[5:15])
    if older:
        older_present = sum(1 for r in older if r.status == "PRESENT")
        older_rate = older_present / len(older) * 100
        
        diff = recent_rate - older_rate
        if abs(diff) > 40:
            direction = "improved" if diff > 0 else "dropped"
            anomalies.append((
                "SUDDEN_CHANGE",
                f"Attendance has {direction} by {abs(diff):.0f}% "
                f"in the last 5 classes (from {older_rate:.0f}% to {recent_rate:.0f}%)."
            ))
    
    # --- Anomaly 2: Consecutive absences ---
    consecutive_absent = 0
    max_consecutive = 0
    for r in records:
        if r.status == "ABSENT":
            consecutive_absent += 1
            max_consecutive = max(max_consecutive, consecutive_absent)
        else:
            consecutive_absent = 0
    
    if max_consecutive >= 3:
        anomalies.append((
            "CONSECUTIVE_ABSENCE",
            f"Student was absent for {max_consecutive} consecutive classes."
        ))
    
    # --- Anomaly 3: Day-of-week pattern ---
    day_absences = {}
    day_totals = {}
    for r in records:
        day = r.date.strftime("%A")
        day_totals[day] = day_totals.get(day, 0) + 1
        if r.status == "ABSENT":
            day_absences[day] = day_absences.get(day, 0) + 1
    
    for day, total in day_totals.items():
        if total >= 3:
            absent = day_absences.get(day, 0)
            rate = absent / total * 100
            if rate >= 60:
                anomalies.append((
                    "DAY_PATTERN",
                    f"High absence on {day}s: "
                    f"{absent}/{total} classes missed ({rate:.0f}%)."
                ))
    
    return anomalies




@login_required
def department_details(request, department_id):
    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    department = get_object_or_404(
        Department,
        id=department_id,
        college=profile.college
    )

    students = Student.objects.filter(
        department=department,
        college=profile.college
    ).select_related("user")

    staff = Staff.objects.filter(
        department=department,
        college=profile.college
    ).select_related("user")

    hod = HOD.objects.filter(
        department=department,
        college=profile.college
    ).select_related("user").first()

    # ---------------------------------------------
    # XAI: DEPARTMENT INSIGHTS
    # ---------------------------------------------
    dept_xai = get_department_insights(department)

    return render(
        request,
        "department_details.html",
        {
            "college": profile.college,
            "department": department,
            "students": students,
            "staff": staff,
            "hod": hod,
            "dept_xai": dept_xai,
        }
    )

def generate_student_recommendations(student, attendance_percentage, required):
    """
    Generate XAI-based recommendations.
    """
    recommendations = []
    
    records = Attendance.objects.filter(student=student)
    
    if records.count() == 0:
        return recommendations
    
    # Recommendation 1: Based on trend
    recent = list(records.order_by("-date")[:5])
    if recent:
        recent_present = sum(1 for r in recent if r.status == "PRESENT")
        recent_rate = recent_present / len(recent) * 100
        
        if recent_rate >= 80 and attendance_percentage < required:
            recommendations.append({
                "type": "POSITIVE",
                "icon": "trending-up",
                "title": "Good Recent Trend",
                "detail": (
                    f"Your recent attendance ({recent_rate:.0f}%) is much "
                    f"better than your average ({attendance_percentage}%). "
                    f"Keep it up to reach the {required}% requirement."
                )
            })
        elif recent_rate < 50 and attendance_percentage >= required:
            recommendations.append({
                "type": "WARNING",
                "icon": "trending-down",
                "title": "Declining Trend Detected",
                "detail": (
                    f"Your recent attendance ({recent_rate:.0f}%) has dropped "
                    f"significantly. Act now to maintain your eligibility."
                )
            })
    
    # Recommendation 2: Day-of-week analysis
    day_absences = {}
    day_totals = {}
    for r in records:
        day = r.date.strftime("%A")
        day_totals[day] = day_totals.get(day, 0) + 1
        if r.status == "ABSENT":
            day_absences[day] = day_absences.get(day, 0) + 1
    
    worst_day = None
    worst_rate = 0
    for day, total in day_totals.items():
        if total >= 3:
            absent = day_absences.get(day, 0)
            rate = absent / total * 100
            if rate > worst_rate:
                worst_rate = rate
                worst_day = day
    
    if worst_day and worst_rate >= 50:
        recommendations.append({
            "type": "INSIGHT",
            "icon": "calendar-day",
            "title": f"Pattern Detected: {worst_day}s",
            "detail": (
                f"You miss {worst_rate:.0f}% of classes on {worst_day}s. "
                f"Focus on {worst_day} attendance to improve your average."
            )
        })
    
    # Recommendation 3: Class count needed
    if attendance_percentage < required:
        total = records.count()
        attended = records.filter(status="PRESENT").count()
        needed_total = (required * total / 100)
        classes_needed = int(needed_total - attended) + 1
        
        if classes_needed > 0:
            recommendations.append({
                "type": "ACTION",
                "icon": "bullseye",
                "title": "Action Required",
                "detail": (
                    f"Attend the next {classes_needed} classes consecutively "
                    f"to reach the {required}% requirement."
                )
            })
    
    return recommendations



def get_department_insights(department):
    """
    XAI: Analyze department health and explain why.
    Returns dict with health status, insights, and per-student breakdown.
    """
    students = Student.objects.filter(department=department)
    total_students = students.count()

    required = department.attendance_required

    insights = []
    at_risk_students = []
    eligible_count = 0
    warning_count = 0
    critical_count = 0
    no_data_count = 0

    total_records = 0
    total_present = 0

    # Track day-of-week absences across department
    day_absences = {}
    day_totals = {}

    for student in students:
        records = Attendance.objects.filter(student=student)
        total = records.count()

        if total == 0:
            no_data_count += 1
            continue

        attended = records.filter(status="PRESENT").count()
        pct = (attended / total) * 100

        total_records += total
        total_present += attended

        # Track day patterns
        for r in records:
            day = r.date.strftime("%A")
            day_totals[day] = day_totals.get(day, 0) + 1
            if r.status == "ABSENT":
                day_absences[day] = day_absences.get(day, 0) + 1

        # Categorize student
        if pct >= required:
            eligible_count += 1
        elif pct >= required - 10:
            warning_count += 1
            at_risk_students.append({
                "student": student,
                "percentage": round(pct, 1),
                "gap": round(required - pct, 1),
                "severity": "WARNING",
            })
        else:
            critical_count += 1
            at_risk_students.append({
                "student": student,
                "percentage": round(pct, 1),
                "gap": round(required - pct, 1),
                "severity": "CRITICAL",
            })

    # Sort at-risk students by lowest percentage first
    at_risk_students.sort(key=lambda x: x["percentage"])

    # Department average
    if total_records > 0:
        avg_pct = round((total_present / total_records) * 100, 1)
    else:
        avg_pct = 0

    # Department health
    active_students = total_students - no_data_count
    if active_students == 0:
        health = "NO DATA"
        health_message = "No attendance recorded yet."
    else:
        eligible_pct = (eligible_count / active_students) * 100
        if eligible_pct >= 80:
            health = "EXCELLENT"
            health_message = (
                f"{eligible_count}/{active_students} students meet the "
                f"{required}% requirement."
            )
        elif eligible_pct >= 60:
            health = "GOOD"
            health_message = (
                f"{eligible_count}/{active_students} students meet the "
                f"{required}% requirement."
            )
        elif eligible_pct >= 40:
            health = "NEEDS ATTENTION"
            health_message = (
                f"Only {eligible_count}/{active_students} students meet the "
                f"{required}% requirement."
            )
        else:
            health = "CRITICAL"
            health_message = (
                f"Only {eligible_count}/{active_students} students meet the "
                f"{required}% requirement."
            )

    # Build insights list
    if total_students > 0:
        insights.append(
            f"Department average attendance: {avg_pct}% "
            f"(required: {required}%)."
        )

    if critical_count > 0:
        insights.append(
            f"{critical_count} student(s) are significantly below the "
            f"required percentage."
        )

    if warning_count > 0:
        insights.append(
            f"{warning_count} student(s) are close to falling below the threshold."
        )

    if no_data_count > 0:
        insights.append(
            f"{no_data_count} student(s) have no attendance recorded yet."
        )

    # Worst day insight
    worst_day = None
    worst_rate = 0
    for day, total in day_totals.items():
        if total >= 5:
            absent = day_absences.get(day, 0)
            rate = absent / total * 100
            if rate > worst_rate:
                worst_rate = rate
                worst_day = day

    if worst_day and worst_rate >= 30:
        insights.append(
            f"Highest absence on {worst_day}s: {worst_rate:.0f}% of classes missed."
        )

    # Best day insight
    best_day = None
    best_rate = 100
    for day, total in day_totals.items():
        if total >= 5:
            absent = day_absences.get(day, 0)
            rate = absent / total * 100
            if rate < best_rate:
                best_rate = rate
                best_day = day

    if best_day and best_rate < 20:
        insights.append(
            f"Best attendance on {best_day}s: only {best_rate:.0f}% absences."
        )

    return {
        "health": health,
        "health_message": health_message,
        "average": avg_pct,
        "total_students": total_students,
        "eligible_count": eligible_count,
        "warning_count": warning_count,
        "critical_count": critical_count,
        "no_data_count": no_data_count,
        "at_risk_students": at_risk_students,
        "insights": insights,
    }

import csv
from django.http import HttpResponse
from datetime import datetime, timedelta


@login_required
def attendance_reports(request):
    """
    Main report page with filters and preview.
    """
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    college = profile.college

    # Get all departments in this college
    departments = Department.objects.filter(college=college)

    # ---- Filters ----
    department_id = request.GET.get("department")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    student_id = request.GET.get("student")

    # Default: last 30 days
    if not start_date:
        start_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")

    # ---- Base Query ----
    records = Attendance.objects.filter(
        student__college=college,
        date__gte=start_date,
        date__lte=end_date,
    ).select_related("student", "student__user", "student__department")

    selected_department = None
    selected_student = None

    if department_id:
        records = records.filter(student__department_id=department_id)
        selected_department = Department.objects.filter(id=department_id).first()

    if student_id:
        records = records.filter(student_id=student_id)
        selected_student = Student.objects.filter(id=student_id).first()

    # ---- Summary ----
    total_records = records.count()
    total_present = records.filter(status="PRESENT").count()
    total_absent = records.filter(status="ABSENT").count()

    if total_records > 0:
        overall_percentage = round((total_present / total_records) * 100, 2)
    else:
        overall_percentage = 0

    # ---- Per-Student Breakdown ----
    students_list = Student.objects.filter(
        college=college
    ).select_related("user", "department")

    if department_id:
        students_list = students_list.filter(department_id=department_id)

    student_stats = []

    for student in students_list:
        s_records = records.filter(student=student)
        s_total = s_records.count()

        if s_total == 0:
            continue

        s_present = s_records.filter(status="PRESENT").count()
        s_absent = s_records.filter(status="ABSENT").count()
        s_pct = round((s_present / s_total) * 100, 2)

        required = student.department.attendance_required

        if s_pct >= required:
            status = "ELIGIBLE"
        elif s_pct >= required - 10:
            status = "WARNING"
        else:
            status = "CRITICAL"

        student_stats.append({
            "student": student,
            "total": s_total,
            "present": s_present,
            "absent": s_absent,
            "percentage": s_pct,
            "required": required,
            "status": status,
        })

    # Sort by lowest percentage first
    student_stats.sort(key=lambda x: x["percentage"])

    # ---- XAI Insights ----
    report_insights = []

    if total_records == 0:
        report_insights.append(
            "No attendance records found for the selected filters."
        )
    else:
        report_insights.append(
            f"Overall attendance: {overall_percentage}% "
            f"({total_present} present / {total_absent} absent out of {total_records} records)."
        )

        critical = sum(1 for s in student_stats if s["status"] == "CRITICAL")
        warning = sum(1 for s in student_stats if s["status"] == "WARNING")
        eligible = sum(1 for s in student_stats if s["status"] == "ELIGIBLE")

        if critical > 0:
            report_insights.append(
                f"⚠ {critical} student(s) are significantly below the required attendance."
            )
        if warning > 0:
            report_insights.append(
                f"{warning} student(s) are close to falling below the threshold."
            )
        if eligible > 0:
            report_insights.append(
                f"✓ {eligible} student(s) are meeting the attendance requirement."
            )

        # Worst day analysis
        day_absences = {}
        day_totals = {}
        for r in records:
            day = r.date.strftime("%A")
            day_totals[day] = day_totals.get(day, 0) + 1
            if r.status == "ABSENT":
                day_absences[day] = day_absences.get(day, 0) + 1

        worst_day = None
        worst_rate = 0
        for day, total in day_totals.items():
            if total >= 3:
                absent = day_absences.get(day, 0)
                rate = absent / total * 100
                if rate > worst_rate:
                    worst_rate = rate
                    worst_day = day

        if worst_day and worst_rate >= 30:
            report_insights.append(
                f"Highest absence on {worst_day}s: {worst_rate:.0f}% of records."
            )

    return render(
        request,
        "attendance_reports.html",
        {
            "college": college,
            "departments": departments,
            "selected_department": selected_department,
            "selected_student": selected_student,
            "start_date": start_date,
            "end_date": end_date,
            "total_records": total_records,
            "total_present": total_present,
            "total_absent": total_absent,
            "overall_percentage": overall_percentage,
            "student_stats": student_stats,
            "report_insights": report_insights,
        }
    )


@login_required
def download_attendance_report(request):
    """
    Download filtered attendance report as CSV.
    """
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    college = profile.college

    department_id = request.GET.get("department")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    student_id = request.GET.get("student")

    if not start_date:
        start_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")

    records = Attendance.objects.filter(
        student__college=college,
        date__gte=start_date,
        date__lte=end_date,
    ).select_related(
        "student", "student__user", "student__department"
    ).order_by("date", "student__register_number")

    if department_id:
        records = records.filter(student__department_id=department_id)

    if student_id:
        records = records.filter(student_id=student_id)

    # ---- Create CSV Response ----
    response = HttpResponse(content_type="text/csv")
    filename = f"attendance_report_{start_date}_to_{end_date}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)

    # Header row
    writer.writerow([
        "Date",
        "Register Number",
        "Student Name",
        "Department",
        "Status",
        "Marked By",
    ])

    # Data rows
    for record in records:
        writer.writerow([
            record.date.strftime("%Y-%m-%d"),
            record.student.register_number,
            record.student.user.get_full_name() or record.student.user.username,
            record.student.department.name,
            record.status,
            record.marked_by.get_full_name() if record.marked_by else "—",
        ])

    return response


@login_required
def download_summary_report(request):
    """
    Download per-student summary as CSV.
    """
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    college = profile.college

    department_id = request.GET.get("department")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if not start_date:
        start_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")

    students = Student.objects.filter(college=college).select_related(
        "user", "department"
    )

    if department_id:
        students = students.filter(department_id=department_id)

    response = HttpResponse(content_type="text/csv")
    filename = f"attendance_summary_{start_date}_to_{end_date}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        "Register Number",
        "Student Name",
        "Department",
        "Total Classes",
        "Present",
        "Absent",
        "Percentage",
        "Required",
        "Status",
    ])

    for student in students:
        records = Attendance.objects.filter(
            student=student,
            date__gte=start_date,
            date__lte=end_date,
        )
        total = records.count()

        if total == 0:
            continue

        present = records.filter(status="PRESENT").count()
        absent = records.filter(status="ABSENT").count()
        pct = round((present / total) * 100, 2)
        required = student.department.attendance_required

        if pct >= required:
            status = "ELIGIBLE"
        elif pct >= required - 10:
            status = "WARNING"
        else:
            status = "CRITICAL"

        writer.writerow([
            student.register_number,
            student.user.get_full_name() or student.user.username,
            student.department.name,
            total,
            present,
            absent,
            f"{pct}%",
            f"{required}%",
            status,
        ])

    return response


@login_required
def download_pdf_report(request):
    """Generate professional PDF attendance report."""
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    college = profile.college
    department_id = request.GET.get("department")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if not start_date:
        start_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")

    students = Student.objects.filter(college=college).select_related(
        "user", "department"
    ).order_by("register_number")

    selected_department = None
    if department_id:
        students = students.filter(department_id=department_id)
        selected_department = Department.objects.filter(id=department_id).first()

    student_stats = []
    total_records_all = 0
    total_present_all = 0

    for student in students:
        records = Attendance.objects.filter(
            student=student,
            date__gte=start_date,
            date__lte=end_date,
        )
        total = records.count()
        if total == 0:
            continue

        present = records.filter(status="PRESENT").count()
        absent = records.filter(status="ABSENT").count()
        pct = round((present / total) * 100, 2)
        required = student.department.attendance_required

        if pct >= required:
            status = "Eligible"
        elif pct >= required - 10:
            status = "Warning"
        else:
            status = "Critical"

        student_stats.append({
            "register_number": student.register_number,
            "name": student.user.get_full_name() or student.user.username,
            "department": student.department.name,
            "total": total,
            "present": present,
            "absent": absent,
            "percentage": pct,
            "status": status,
        })

        total_records_all += total
        total_present_all += present

    student_stats.sort(key=lambda x: x["percentage"])

    overall_pct = 0
    if total_records_all > 0:
        overall_pct = round((total_present_all / total_records_all) * 100, 2)

    # Build PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=30, leftMargin=30,
        topMargin=30, bottomMargin=30,
    )

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Heading1"],
        fontSize=20, textColor=colors.HexColor("#0b2b4a"),
        alignment=TA_CENTER, spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "SubtitleStyle", parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor("#6b7f99"),
        alignment=TA_CENTER, spaceAfter=4,
    )
    heading_style = ParagraphStyle(
        "HeadingStyle", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#0b2b4a"),
        spaceBefore=12, spaceAfter=6,
    )

    elements.append(Paragraph(college.name, title_style))
    elements.append(Paragraph("Attendance Report", subtitle_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        f"<b>Period:</b> {start_date} to {end_date}", subtitle_style
    ))
    if selected_department:
        elements.append(Paragraph(
            f"<b>Department:</b> {selected_department.name}", subtitle_style
        ))
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("Summary", heading_style))
    summary_data = [
        ["Total Records", "Present", "Absent", "Overall %"],
        [
            str(total_records_all),
            str(total_present_all),
            str(total_records_all - total_present_all),
            f"{overall_pct}%",
        ],
    ]
    summary_table = Table(summary_data, colWidths=[2.2 * inch] * 4)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b2b4a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 1), (-1, 1), 14),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#0b2b4a")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f0f4fa")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 16))

    elements.append(Paragraph(
        f"Per-Student Breakdown ({len(student_stats)} students)",
        heading_style,
    ))

    if student_stats:
        table_data = [[
            "Register No.", "Student Name", "Department",
            "Total", "Present", "Absent", "Attend %", "Status"
        ]]
        for stat in student_stats:
            table_data.append([
                stat["register_number"],
                stat["name"],
                stat["department"],
                str(stat["total"]),
                str(stat["present"]),
                str(stat["absent"]),
                f"{stat['percentage']}%",
                stat["status"],
            ])

        student_table = Table(
            table_data,
            colWidths=[
                1.2 * inch, 2.2 * inch, 1.8 * inch,
                0.8 * inch, 0.8 * inch, 0.8 * inch,
                0.9 * inch, 1.0 * inch,
            ],
            repeatRows=1,
        )
        student_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b2b4a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTSIZE", (0, 1), (-1, -1), 8.5),
            ("ALIGN", (3, 1), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                [colors.white, colors.HexColor("#f8fafd")]),
        ]))
        elements.append(student_table)
    else:
        elements.append(Paragraph(
            "No attendance records found for the selected filters.",
            subtitle_style,
        ))

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    filename = f"attendance_report_{start_date}_to_{end_date}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response




@login_required
def email_report(request):
    """Email the attendance report (as CSV) to a recipient."""
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    if request.method != "POST":
        return redirect("attendance_reports")

    college = profile.college
    recipient = request.POST.get("recipient_email")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    department_id = request.POST.get("department")

    if not recipient:
        django_messages.error(request, "Please provide a recipient email.")
        return redirect("attendance_reports")

    # Build records
    records = Attendance.objects.filter(
        student__college=college,
        date__gte=start_date,
        date__lte=end_date,
    ).select_related(
        "student", "student__user", "student__department"
    ).order_by("date")

    if department_id:
        records = records.filter(student__department_id=department_id)

    # Build CSV content
    csv_lines = ["Date,Register Number,Student Name,Department,Status"]
    for r in records:
        name = r.student.user.get_full_name() or r.student.user.username
        csv_lines.append(
            f"{r.date},{r.student.register_number},"
            f"{name},{r.student.department.name},{r.status}"
        )
    csv_content = "\n".join(csv_lines)

    try:
        subject = f"Attendance Report: {start_date} to {end_date}"
        body = (
            f"Hello,\n\n"
            f"Please find attached the attendance report.\n\n"
            f"Period: {start_date} to {end_date}\n"
            f"College: {college.name}\n"
            f"Total Records: {records.count()}\n\n"
            f"— Attendance System"
        )

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )

        filename = f"attendance_report_{start_date}_to_{end_date}.csv"
        email.attach(filename, csv_content, "text/csv")
        email.send(fail_silently=False)

        django_messages.success(request, f"✓ Report sent to {recipient}")

    except Exception as e:
        django_messages.error(request, f"Failed to send email: {str(e)}")

    return redirect("attendance_reports")

@login_required
def attendance_calendar(request):
    """
    Monthly calendar view showing attendance for a student or department.
    """
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF", "STUDENT"]:
        return redirect("home")

    # Determine student
    student = None
    college = profile.college

    # Students can only see their own calendar
    if profile.role == "STUDENT":
        try:
            student = Student.objects.select_related(
                "user", "department", "college"
            ).get(user=request.user)
            college = student.college
        except Student.DoesNotExist:
            return render(request, "student_not_configured.html")

    # Admin/Staff/HOD can pick a student
    else:
        student_id = request.GET.get("student")
        if student_id:
            student = Student.objects.filter(
                id=student_id, college=college
            ).select_related("user", "department").first()

    # Month/Year selection
    today = date.today()
    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
        if month < 1 or month > 12:
            month = today.month
    except (TypeError, ValueError):
        year = today.year
        month = today.month

    # Previous / Next month
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    # Build calendar
    cal = calendar.Calendar(firstweekday=6)  # Sunday first
    month_days = cal.monthdayscalendar(year, month)  # list of weeks

    # Get attendance records for this month
    attendance_map = {}
    if student:
        records = Attendance.objects.filter(
            student=student,
            date__year=year,
            date__month=month,
        )
        for r in records:
            attendance_map[r.date.day] = r.status

    # Build weeks with day info
    weeks = []
    for week in month_days:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({
                    "day": "",
                    "status": "empty",
                    "is_today": False,
                })
            else:
                status = attendance_map.get(day, "NO_DATA")
                is_today = (year == today.year and
                            month == today.month and
                            day == today.day)
                week_data.append({
                    "day": day,
                    "status": status,
                    "is_today": is_today,
                })
        weeks.append(week_data)

    # Monthly summary
    month_records = [
        v for v in attendance_map.values()
        if v in ("PRESENT", "ABSENT")
    ]
    total = len(month_records)
    present = month_records.count("PRESENT")
    absent = month_records.count("ABSENT")
    percentage = round((present / total) * 100, 1) if total > 0 else 0

    # XAI Insights
    calendar_insights = []

    if student:
        if total == 0:
            calendar_insights.append(
                f"No attendance records for {student.user.get_full_name() or student.user.username} "
                f"in {calendar.month_name[month]} {year}."
            )
        else:
            calendar_insights.append(
                f"Attended {present} of {total} classes "
                f"({percentage}%) in {calendar.month_name[month]} {year}."
            )

            required = student.department.attendance_required
            if percentage >= required:
                calendar_insights.append(
                    f"✓ Above the required {required}% for this month."
                )
            else:
                calendar_insights.append(
                    f"⚠ Below the required {required}% for this month."
                )

            # Find best/worst weeks
            week_percentages = []
            for week in month_days:
                week_days = [d for d in week if d != 0]
                if not week_days:
                    continue
                w_total = 0
                w_present = 0
                for d in week_days:
                    s = attendance_map.get(d)
                    if s in ("PRESENT", "ABSENT"):
                        w_total += 1
                        if s == "PRESENT":
                            w_present += 1
                if w_total > 0:
                    week_percentages.append(
                        (round((w_present / w_total) * 100, 1), week_days[0], week_days[-1])
                    )

            if week_percentages:
                best = max(week_percentages, key=lambda x: x[0])
                worst = min(week_percentages, key=lambda x: x[0])
                calendar_insights.append(
                    f"📈 Best week: {best[1]}–{best[2]} at {best[0]}%"
                )
                calendar_insights.append(
                    f"📉 Weakest week: {worst[1]}–{worst[2]} at {worst[0]}%"
                )
    else:
        calendar_insights.append("Select a student to view attendance details.")

    # Students list for dropdown (admin/staff/hod only)
    students_list = []
    if profile.role != "STUDENT":
        students_list = Student.objects.filter(
            college=college
        ).select_related("user", "department").order_by("register_number")

    return render(
        request,
        "attendance_calendar.html",
        {
            "college": college,
            "student": student,
            "students_list": students_list,
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month],
            "weeks": weeks,
            "prev_year": prev_year,
            "prev_month": prev_month,
            "next_year": next_year,
            "next_month": next_month,
            "today": today,
            "total": total,
            "present": present,
            "absent": absent,
            "percentage": percentage,
            "calendar_insights": calendar_insights,
        }
    )


# =====================================================
# NOTIFICATION HELPERS
# =====================================================
def create_attendance_notification(parent, student, percentage, required, notification_type):
    """
    Create a notification for a parent in their preferred language.
    """
    gap = round(required - percentage, 2)
    if gap < 0:
        gap = 0

    translation = get_translation(notification_type, parent.preferred_language)

    context = {
        "parent_name": parent.name,
        "student_name": student.user.get_full_name() or student.user.username,
        "register_number": student.register_number,
        "department": student.department.name,
        "college": student.college.name,
        "percentage": percentage,
        "required": required,
        "gap": gap,
    }

    subject = translation["subject"].format(**context)
    message = translation["message"].format(**context)

    notification = Notification.objects.create(
        recipient=parent,
        notification_type=notification_type.upper(),
        language=parent.preferred_language,
        subject=subject,
        message=message,
    )

    return notification


def send_notification_email(notification, audio_path=None):
    """
    Send the notification via email.
    Optionally attach a voice message.
    """
    parent = notification.recipient

    if not parent.receive_email:
        notification.status = "FAILED"
        notification.save()
        return False

    try:
        from django.core.mail import EmailMessage
        from django.conf import settings

        email = EmailMessage(
            subject=notification.subject,
            body=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[parent.email],
        )

        # Attach voice message if available
        if audio_path and os.path.exists(audio_path):
            email.attach_file(audio_path)
            print(f"[voice] Attached: {audio_path}")

        email.send(fail_silently=False)
        notification.status = "SENT"
        notification.sent_at = timezone.now()
        notification.save()
        return True

    except Exception as e:
        notification.status = "FAILED"
        notification.save()
        print(f"[voice] Email send failed: {e}")
        return False


@login_required
def notify_low_attendance(request, student_id):
    """
    Send low-attendance notification to all parents of a student.
    Uses REAL attendance data.
    """
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    student = get_object_or_404(
        Student,
        id=student_id,
        college=profile.college,
    )

    # ---- REAL ATTENDANCE CALCULATION ----
    records = Attendance.objects.filter(student=student)
    total = records.count()
    present = records.filter(status="PRESENT").count()
    absent = records.filter(status="ABSENT").count()

    if total > 0:
        percentage = round((present / total) * 100, 2)
    else:
        percentage = 0

    required = student.department.attendance_required

    # ---- Guard: student already eligible ----
    if percentage >= required:
        django_messages.warning(
            request,
            f"{student.user.get_full_name() or student.user.username} "
            f"already has sufficient attendance ({percentage}% ≥ {required}%)."
        )
        return redirect("department_students", department_id=student.department.id)

    # ---- Fetch parents ----
    parents = student.parents.all()

    if not parents.exists():
        django_messages.error(
            request,
            f"No parents registered for {student.user.get_full_name() or student.user.username}."
        )
        return redirect("department_students", department_id=student.department.id)

    # ---- Determine notification type ----
    notif_type = "critical_attendance" if percentage < required - 15 else "low_attendance"

    # ---- Send to each parent ----
    sent_count = 0
    failed_count = 0

    for parent in parents:
        if not parent.receive_email:
            continue

        try:
            notification = create_attendance_notification(
                parent=parent,
                student=student,
                percentage=percentage,      # ← real value
                required=required,          # ← real value
                notification_type=notif_type,
            )
            success = send_notification_email(notification)

            if success:
                sent_count += 1
            else:
                failed_count += 1

        except Exception as e:
            print(f"Error sending to {parent.email}: {e}")
            failed_count += 1

    # ---- Feedback ----
    if sent_count > 0:
        django_messages.success(
            request,
            f"✓ Notification sent to {sent_count} parent(s) — "
            f"attendance {percentage}% (required {required}%)."
        )
    if failed_count > 0:
        django_messages.error(
            request,
            f"Failed to send to {failed_count} parent(s)."
        )

    return redirect("department_students", department_id=student.department.id)


@login_required
def add_parent(request, student_id):
    """
    Admin: Add a parent for a student.
    """
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    student = get_object_or_404(
        Student,
        id=student_id,
        college=profile.college,
    )

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        relationship = request.POST.get("relationship", "FATHER")
        language = request.POST.get("preferred_language", "en")
        receive_email = request.POST.get("receive_email") == "on"

        if not name or not email:
            return render(request, "add_parent.html", {
                "student": student,
                "college": profile.college,
                "error": "Name and email are required.",
            })

        Parent.objects.create(
            student=student,
            name=name,
            email=email,
            phone=phone,
            relationship=relationship,
            preferred_language=language,
            receive_email=receive_email,
        )

        django_messages.success(request, f"✓ Parent '{name}' added.")
        return redirect("department_students", department_id=student.department.id)

    # Import language choices
    from .models import LANGUAGE_CHOICES

    return render(request, "add_parent.html", {
        "student": student,
        "college": profile.college,
        "languages": LANGUAGE_CHOICES,
    })


@login_required
def parent_notifications(request):
    """
    Parent: view their notifications (their own inbox).
    Also allows language change.
    """
    profile = request.user.userprofile

    if profile.role != "PARENT":
        return redirect("home")

    parent = get_object_or_404(Parent, user=request.user)

    notifications = parent.notifications.all()

    # Mark as read
    for n in notifications.filter(status="SENT"):
        n.status = "READ"
        n.read_at = timezone.now()
        n.save()

    from .models import LANGUAGE_CHOICES

    return render(request, "parent_notifications.html", {
        "parent": parent,
        "notifications": notifications,
        "languages": LANGUAGE_CHOICES,
    })


@login_required
def change_language(request):
    """
    Parent: change preferred language.
    """
    if request.method != "POST":
        return redirect("parent_notifications")

    profile = request.user.userprofile

    if profile.role != "PARENT":
        return redirect("home")

    parent = get_object_or_404(Parent, user=request.user)
    new_lang = request.POST.get("language", "en")

    valid_langs = [code for code, _ in LANGUAGE_CHOICES]
    if new_lang in valid_langs:
        parent.preferred_language = new_lang
        parent.save()
        django_messages.success(request, "Language preference updated.")
    else:
        django_messages.error(request, "Invalid language.")

    return redirect("parent_notifications")



@login_required
def manage_subjects(request, department_id):
    """List, add subjects for a department."""
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    department = get_object_or_404(
        Department, id=department_id, college=profile.college
    )

    subjects = Subject.objects.filter(department=department)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip()
        hours = request.POST.get("hours_per_week", "4")

        if name:
            try:
                Subject.objects.create(
                    department=department,
                    name=name,
                    code=code,
                    hours_per_week=int(hours),
                )
                django_messages.success(request, f"Subject '{name}' added.")
            except Exception as e:
                django_messages.error(request, f"Error: {e}")
        return redirect("manage_subjects", department_id=department.id)

    return render(request, "manage_subjects.html", {
        "department": department,
        "subjects": subjects,
    })


@login_required
def delete_subject(request, subject_id):
    """Delete a subject."""
    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    subject = get_object_or_404(
        Subject, id=subject_id, department__college=profile.college
    )
    dept_id = subject.department.id

    if request.method == "POST":
        subject.delete()
        django_messages.success(request, "Subject deleted.")
        return redirect("manage_subjects", department_id=dept_id)

    return render(request, "delete_subject.html", {"subject": subject})



from .models import Period   # add to imports if not present


@login_required
def manage_periods(request, department_id):
    """List and add periods for a department (staff/admin/HOD)."""
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    department = get_object_or_404(
        Department, id=department_id, college=profile.college
    )

    periods = Period.objects.filter(department=department).order_by("number")

    if request.method == "POST":
        number = request.POST.get("number")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        if not (number and start_time and end_time):
            django_messages.error(request, "All fields are required.")
            return redirect("manage_periods", department_id=department.id)

        if Period.objects.filter(department=department, number=number).exists():
            django_messages.error(
                request, f"Period {number} already exists."
            )
            return redirect("manage_periods", department_id=department.id)

        try:
            Period.objects.create(
                department=department,
                number=int(number),
                start_time=start_time,
                end_time=end_time,
            )
            django_messages.success(
                request, f"✓ Period {number} added successfully."
            )
        except Exception as e:
            django_messages.error(request, f"Error: {e}")

        return redirect("manage_periods", department_id=department.id)

    return render(request, "manage_periods.html", {
        "department": department,
        "periods": periods,
    })


@login_required
def edit_period(request, period_id):
    """Edit an existing period."""
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    period = get_object_or_404(
        Period, id=period_id, department__college=profile.college
    )

    if request.method == "POST":
        number = request.POST.get("number")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        if not (number and start_time and end_time):
            django_messages.error(request, "All fields are required.")
        else:
            # Check for duplicates (exclude current)
            duplicate = Period.objects.filter(
                department=period.department, number=number
            ).exclude(id=period.id).exists()

            if duplicate:
                django_messages.error(
                    request, f"Period {number} already exists."
                )
            else:
                period.number = int(number)
                period.start_time = start_time
                period.end_time = end_time
                period.save()
                django_messages.success(request, "✓ Period updated.")

        return redirect("manage_periods", department_id=period.department.id)

    return render(request, "edit_period.html", {
        "department": period.department,
        "period": period,
    })


@login_required
def delete_period(request, period_id):
    """Delete a period."""
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    period = get_object_or_404(
        Period, id=period_id, department__college=profile.college
    )
    dept_id = period.department.id

    if request.method == "POST":
        period.delete()
        django_messages.success(request, "Period deleted.")
        return redirect("manage_periods", department_id=dept_id)

    return render(request, "delete_period.html", {"period": period})



@login_required
def auto_create_periods(request, department_id):
    """Create default periods 1-6 with standard timings."""
    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    department = get_object_or_404(
        Department, id=department_id, college=profile.college
    )

    # Default schedule
    defaults = [
        (1, "09:00", "10:00"),
        (2, "10:00", "11:00"),
        (3, "11:15", "12:15"),
        (4, "13:00", "14:00"),
        (5, "14:00", "15:00"),
        (6, "15:15", "16:15"),
    ]

    created = 0
    for num, start, end in defaults:
        _, was_created = Period.objects.get_or_create(
            department=department,
            number=num,
            defaults={"start_time": start, "end_time": end},
        )
        if was_created:
            created += 1

    django_messages.success(request, f"Created {created} default periods.")
    return redirect("manage_periods", department_id=department.id)





def manage_hods(request):
    return render(request, "manage_hods.html")  # create this later

def manage_users(request):
    return render(request, "manage_users.html")

def view_attendance(request):
    return render(request, "attendance_reports.html")

def college_settings(request):
    return render(request, "college_settings.html")

def access_control(request):
    return render(request, "access_control.html")

def admin_profile(request):
    return render(request, "admin_profile.html")

def attendance_percentage_settings(request):
    return render(request, "attendance_settings.html")

def academic_year_settings(request):
    return render(request, "academic_year_settings.html")

def attendance_rules(request):
    return render(request, "attendance_rules.html")



# =====================================================
# ADMIN DASHBOARD EXTRA PAGES
# =====================================================

@login_required
def manage_staff(request):
    """List all staff in the college."""
    profile = request.user.userprofile
    if profile.role != "ADMIN":
        return redirect("home")

    college = profile.college
    staff = Staff.objects.filter(college=college).select_related(
        "user", "department"
    )

    return render(request, "manage_staff.html", {
        "college": college,
        "staff": staff,
    })


@login_required
def manage_hods(request):
    """List all HODs in the college."""
    profile = request.user.userprofile
    if profile.role != "ADMIN":
        return redirect("home")

    college = profile.college
    hods = HOD.objects.filter(college=college).select_related(
        "user", "department"
    )

    return render(request, "manage_hods.html", {
        "college": college,
        "hods": hods,
    })


@login_required
def manage_users(request):
    """List all user accounts in the college."""
    profile = request.user.userprofile
    if profile.role != "ADMIN":
        return redirect("home")

    college = profile.college
    users = User.objects.filter(
        userprofile__college=college
    ).select_related("userprofile")

    return render(request, "manage_users.html", {
        "college": college,
        "users": users,
    })


@login_required
def view_attendance(request):
    """Redirect to reports page."""
    return redirect("attendance_reports")


@login_required
def college_settings(request):
    """Edit college details."""
    profile = request.user.userprofile
    if profile.role != "ADMIN":
        return redirect("home")

    college = profile.college

    if request.method == "POST":
        college.name = request.POST.get("name", college.name)
        college.email = request.POST.get("email", college.email)
        college.phone = request.POST.get("phone", college.phone)
        college.attendance_percentage = request.POST.get(
            "attendance_percentage", college.attendance_percentage
        )
        college.save()
        django_messages.success(request, "✓ College settings updated.")
        return redirect("college_settings")

    return render(request, "college_settings.html", {
        "college": college,
    })


@login_required
def access_control(request):
    """View roles and users per role."""
    profile = request.user.userprofile
    if profile.role != "ADMIN":
        return redirect("home")

    college = profile.college

    role_counts = {
        "ADMIN": UserProfile.objects.filter(college=college, role="ADMIN").count(),
        "HOD": UserProfile.objects.filter(college=college, role="HOD").count(),
        "STAFF": UserProfile.objects.filter(college=college, role="STAFF").count(),
        "STUDENT": UserProfile.objects.filter(college=college, role="STUDENT").count(),
    }

    return render(request, "access_control.html", {
        "college": college,
        "role_counts": role_counts,
    })


@login_required
def admin_profile(request):
    """View and edit own admin profile."""
    profile = request.user.userprofile

    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.save()

        # Optional password change
        new_password = request.POST.get("new_password")
        if new_password:
            user.set_password(new_password)
            user.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)

        django_messages.success(request, "✓ Profile updated.")
        return redirect("admin_profile")

    return render(request, "admin_profile.html", {
        "profile": profile,
        "college": profile.college,
    })


@login_required
def attendance_percentage_settings(request):
    """Set the default attendance percentage for the college."""
    profile = request.user.userprofile
    if profile.role != "ADMIN":
        return redirect("home")

    college = profile.college

    if request.method == "POST":
        try:
            value = float(request.POST.get("attendance_percentage", 75))
            if 0 <= value <= 100:
                college.attendance_percentage = value
                college.save()
                django_messages.success(request, f"✓ Set to {value}%")
            else:
                django_messages.error(request, "Value must be 0-100.")
        except ValueError:
            django_messages.error(request, "Invalid number.")
        return redirect("attendance_percentage_settings")

    return render(request, "attendance_percentage_settings.html", {
        "college": college,
    })


@login_required
def academic_year_settings(request):
    """Configure academic year and semester."""
    profile = request.user.userprofile
    if profile.role != "ADMIN":
        return redirect("home")

    # Stored on session for now (no model field)
    if request.method == "POST":
        request.session["academic_year"] = request.POST.get("academic_year", "")
        request.session["semester"] = request.POST.get("semester", "")
        django_messages.success(request, "✓ Academic year saved.")
        return redirect("academic_year_settings")

    return render(request, "academic_year_settings.html", {
        "college": profile.college,
        "academic_year": request.session.get("academic_year", "2025-2026"),
        "semester": request.session.get("semester", "1"),
    })


@login_required
def attendance_rules(request):
    """Configure attendance rules text."""
    profile = request.user.userprofile
    if profile.role != "ADMIN":
        return redirect("home")

    if request.method == "POST":
        request.session["attendance_rules"] = request.POST.get("rules", "")
        django_messages.success(request, "✓ Rules saved.")
        return redirect("attendance_rules")

    return render(request, "attendance_rules.html", {
        "college": profile.college,
        "rules": request.session.get("attendance_rules", ""),
    })


@login_required
def add_college(request):
    """Create a new college."""
    profile = request.user.userprofile

    # Only ADMIN can create colleges
    if profile.role != "ADMIN":
        return redirect("home")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        college_id = request.POST.get("college_id", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        attendance_percentage = request.POST.get("attendance_percentage", "75")

        if not name or not college_id:
            return render(request, "add_college.html", {
                "error": "College name and College ID are required.",
            })

        if College.objects.filter(college_id=college_id).exists():
            return render(request, "add_college.html", {
                "error": f"College ID '{college_id}' already exists.",
            })

        try:
            college = College.objects.create(
                college_id=college_id,
                name=name,
                email=email,
                phone=phone,
                attendance_percentage=int(attendance_percentage),
            )
            django_messages.success(
                request,
                f"✓ College '{college.name}' created successfully!"
            )
            return redirect("manage_colleges")
        except Exception as e:
            return render(request, "add_college.html", {
                "error": str(e),
            })

    return render(request, "add_college.html")


@login_required
def manage_colleges(request):
    """List all colleges."""
    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    colleges = College.objects.all().order_by("-id")

    return render(request, "manage_colleges.html", {
        "colleges": colleges,
        "current_college": profile.college,
    })


@login_required
def switch_college(request, college_id):
    """Switch the current admin's active college."""
    profile = request.user.userprofile

    if profile.role != "ADMIN":
        return redirect("home")

    college = get_object_or_404(College, id=college_id)
    profile.college = college
    profile.save()

    django_messages.success(request, f"✓ Switched to {college.name}")
    return redirect("admin_dashboard")


from attendance.voice_generator import generate_voice


def generate_attendance_voice(parent, student, percentage, required, notification_type):
    """
    Generate a voice file for a parent notification.
    Returns the file path or None.
    """
    from attendance.translations import get_translation

    # Get the translated text
    t = get_translation(notification_type, parent.preferred_language)

    context = {
        "parent_name": parent.name,
        "student_name": student.user.get_full_name() or student.user.username,
        "register_number": student.register_number,
        "department": student.department.name,
        "college": student.college.name,
        "percentage": round(percentage, 1),
        "required": required,
        "gap": round(required - percentage, 1),
    }

    # Full text message (for speech)
    full_text = t["message"].format(**context)

    # Limit to ~500 chars to keep the audio under ~1 minute
    if len(full_text) > 500:
        full_text = full_text[:500] + "..."

    # Build a unique filename
    filename = (
        f"alert_{parent.id}_"
        f"{student.id}_"
        f"{notification_type}_"
        f"{int(percentage)}.mp3"
    )

    # Generate the voice file
    audio_path = generate_voice(
        full_text,
        parent.preferred_language,
        filename,
    )

    return audio_path



from .models import AttendanceAuditLog


def log_attendance_change(
    attendance,
    student,
    user,
    action,
    old_status="",
    new_status="",
    reason="",
):
    """
    Create an audit log entry for an attendance change.
    """
    try:
        AttendanceAuditLog.objects.create(
            attendance=attendance,
            student=student,
            changed_by=user,
            action=action,
            old_status=old_status or "",
            new_status=new_status or "",
            subject_name=attendance.subject.name if attendance and attendance.subject else "",
            period_number=attendance.period.number if attendance and attendance.period else None,
            attendance_date=attendance.date if attendance else None,
            reason=reason,
        )
    except Exception as e:
        print(f"[audit] Failed to log: {e}")


@login_required
def attendance_audit_log(request):
    """Display audit log with filters."""
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD"]:
        return redirect("home")

    college = profile.college

    # Filters
    action_filter = request.GET.get("action", "")
    student_filter = request.GET.get("student", "")
    days_filter = request.GET.get("days", "7")

    try:
        days = int(days_filter)
    except ValueError:
        days = 7

    cutoff = timezone.now() - timedelta(days=days)

    logs = AttendanceAuditLog.objects.filter(
        student__college=college,
        created_at__gte=cutoff,
    ).select_related(
        "student", "student__user", "student__department",
        "changed_by", "attendance",
    )

    if action_filter:
        logs = logs.filter(action=action_filter)

    if student_filter:
        logs = logs.filter(student_id=student_filter)

    # Summary stats
    total_changes = logs.count()
    updated_count = logs.filter(action="UPDATED").count()
    created_count = logs.filter(action="CREATED").count()

    # Students list for filter dropdown
    students_list = Student.objects.filter(
        college=college
    ).order_by("register_number")

    return render(request, "attendance_audit_log.html", {
        "college": college,
        "logs": logs[:500],  # Limit to 500 for performance
        "total_changes": total_changes,
        "updated_count": updated_count,
        "created_count": created_count,
        "action_filter": action_filter,
        "student_filter": student_filter,
        "days_filter": days,
        "students_list": students_list,
    })


from .models import AttendanceDispute
import calendar


@login_required
def student_portal(request):
    """
    Student self-service portal.
    Shows attendance %, calendar, subjects, and dispute history.
    """
    profile = request.user.userprofile

    if profile.role != "STUDENT":
        return redirect("home")

    try:
        student = Student.objects.select_related(
            "user", "department", "college"
        ).get(user=request.user)
    except Student.DoesNotExist:
        return render(request, "student_not_configured.html")

    # All attendance records
    records = Attendance.objects.filter(student=student).select_related(
        "subject", "period"
    ).order_by("-date")

    total = records.count()
    present = records.filter(status="PRESENT").count()
    absent = records.filter(status="ABSENT").count()

    percentage = round((present / total) * 100, 2) if total > 0 else 0
    required = student.department.attendance_required

    if total == 0:
        eligibility = "NO DATA"
    elif percentage >= required:
        eligibility = "ELIGIBLE"
    else:
        eligibility = "NOT ELIGIBLE"

    # Subject-wise breakdown
    subjects_data = []
    subjects = Subject.objects.filter(
        department=student.department, is_active=True
    )
    for subj in subjects:
        subj_records = records.filter(subject=subj)
        subj_total = subj_records.count()
        if subj_total == 0:
            continue
        subj_present = subj_records.filter(status="PRESENT").count()
        subj_pct = round((subj_present / subj_total) * 100, 1)
        subjects_data.append({
            "subject": subj,
            "total": subj_total,
            "present": subj_present,
            "absent": subj_total - subj_present,
            "percentage": subj_pct,
        })

    # Recent absences (for disputes)
    recent_absences = records.filter(status="ABSENT")[:20]

    # Existing disputes
    disputes = AttendanceDispute.objects.filter(
        student=student
    ).select_related("attendance", "attendance__subject", "attendance__period")

    # IDs of attendance records already disputed
    disputed_ids = set(disputes.values_list("attendance_id", flat=True))

    return render(request, "student_portal.html", {
        "student": student,
        "total": total,
        "present": present,
        "absent": absent,
        "percentage": percentage,
        "required": required,
        "eligibility": eligibility,
        "subjects_data": subjects_data,
        "recent_absences": recent_absences,
        "disputes": disputes,
        "disputed_ids": disputed_ids,
    })


@login_required
def raise_dispute(request, attendance_id):
    """
    Student raises a dispute for a record marked absent.
    """
    profile = request.user.userprofile

    if profile.role != "STUDENT":
        return redirect("home")

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect("home")

    attendance = get_object_or_404(
        Attendance,
        id=attendance_id,
        student=student,
    )

    # Can only dispute ABSENT records
    if attendance.status != "ABSENT":
        django_messages.error(request, "You can only dispute absent records.")
        return redirect("student_portal")

    # Check if already disputed
    if AttendanceDispute.objects.filter(
        attendance=attendance, student=student
    ).exists():
        django_messages.warning(request, "You have already raised a request for this class.")
        return redirect("student_portal")

    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()

        if not reason:
            django_messages.error(request, "Please provide a reason.")
        else:
            AttendanceDispute.objects.create(
                attendance=attendance,
                student=student,
                reason=reason,
            )
            django_messages.success(
                request,
                "✓ Request submitted. Your teacher will review it."
            )
            return redirect("student_portal")

    return render(request, "raise_dispute.html", {
        "student": student,
        "attendance": attendance,
    })


@login_required
def manage_disputes(request):
    """
    Staff/Admin views all pending dispute requests.
    """
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    college = profile.college

    # Optional status filter
    status_filter = request.GET.get("status", "PENDING")

    disputes = AttendanceDispute.objects.filter(
        student__college=college,
    ).select_related(
        "student", "student__user", "student__department",
        "attendance", "attendance__subject", "attendance__period",
    )

    if status_filter in ["PENDING", "APPROVED", "REJECTED"]:
        disputes = disputes.filter(status=status_filter)

    pending_count = AttendanceDispute.objects.filter(
        student__college=college, status="PENDING"
    ).count()

    return render(request, "manage_disputes.html", {
        "college": college,
        "disputes": disputes,
        "status_filter": status_filter,
        "pending_count": pending_count,
    })


@login_required
def review_dispute(request, dispute_id):
    """
    Staff/Admin approves or rejects a dispute.
    """
    profile = request.user.userprofile

    if profile.role not in ["ADMIN", "HOD", "STAFF"]:
        return redirect("home")

    dispute = get_object_or_404(
        AttendanceDispute,
        id=dispute_id,
        student__college=profile.college,
    )

    if request.method == "POST":
        action = request.POST.get("action")  # "approve" or "reject"
        note = request.POST.get("review_note", "").strip()

        if action == "approve":
            # Update the attendance
            att = dispute.attendance
            if att.status == "ABSENT":
                old_status = att.status
                att.status = "PRESENT"
                att.marked_by = request.user
                att.save()

                # Log in audit trail
                log_attendance_change(
                    attendance=att,
                    student=dispute.student,
                    user=request.user,
                    action="UPDATED",
                    old_status=old_status,
                    new_status="PRESENT",
                    reason=f"Dispute approved: {note or 'No note'}",
                )

            dispute.status = "APPROVED"
            django_messages.success(
                request,
                f"✓ Approved — {dispute.student.register_number}'s "
                f"attendance marked PRESENT."
            )

        elif action == "reject":
            dispute.status = "REJECTED"
            django_messages.info(
                request,
                f"Request from {dispute.student.register_number} rejected."
            )

        else:
            django_messages.error(request, "Invalid action.")
            return redirect("manage_disputes")

        dispute.reviewed_by = request.user
        dispute.review_note = note
        dispute.reviewed_at = timezone.now()
        dispute.save()

        return redirect("manage_disputes")

    return render(request, "review_dispute.html", {
        "dispute": dispute,
    })





def _require_admin(request):
    """Return (profile, error_response). Reused in every bulk view."""
    profile = getattr(request.user, "userprofile", None)
    if profile is None or profile.role != "ADMIN":
        return None, redirect("home")
    return profile, None


def _serialise_rows(rows):
    """Convert list[StudentRow] to JSON-safe dicts for the session."""
    out = []
    for r in rows:
        out.append({
            "row_number": r.row_number,
            "register_number": r.register_number,
            "name": r.name,
            "email": r.email,
            "phone": r.phone,
            "gender": r.gender,
            "dob": r.dob.isoformat() if r.dob else "",
            "department_name": r.department_name,
            "year": r.year,
            "section": r.section,
            "parents": [
                {
                    "name": p.name,
                    "phone": p.phone,
                    "email": p.email,
                    "relationship": p.relationship,
                }
                for p in r.parents
            ],
            "errors": list(r.errors),
        })
    return out


def _rows_from_session(payload):
    """Rebuild StudentRow objects from session dicts."""
    from datetime import date as _date
    rows = []
    for d in payload:
        dob = None
        if d.get("dob"):
            try:
                y, m, day = d["dob"].split("-")
                dob = _date(int(y), int(m), int(day))
            except Exception:
                dob = None

        parents = [
            ParentRow(
                name=p["name"],
                phone=p["phone"],
                email=p["email"],
                relationship=p["relationship"],
            )
            for p in d.get("parents", [])
        ]

        rows.append(StudentRow(
            row_number=d["row_number"],
            register_number=d["register_number"],
            name=d["name"],
            email=d["email"],
            phone=d["phone"],
            gender=d["gender"],
            dob=dob,
            department_name=d["department_name"],
            year=d["year"],
            section=d["section"],
            parents=parents,
            errors=list(d.get("errors", [])),
        ))
    return rows


# -----------------------------------------------------
# 1. UPLOAD + PREVIEW
# -----------------------------------------------------
@login_required
def bulk_add_students(request):
    """
    GET  → upload form
    POST → parse+validate, show preview page
    """
    profile, err = _require_admin(request)
    if err:
        return err

    college = profile.college

    if request.method == "POST":
        uploaded = request.FILES.get("excel_file")

        if not uploaded:
            django_messages.error(request, "Please choose an .xlsx file to upload.")
            return redirect("bulk_add_students")

        if not uploaded.name.lower().endswith(".xlsx"):
            django_messages.error(request, "Only .xlsx files are accepted.")
            return redirect("bulk_add_students")

        if uploaded.size > 5 * 1024 * 1024:
            django_messages.error(request, "File too large (max 5 MB).")
            return redirect("bulk_add_students")

        existing = set(
            Student.objects.filter(college=college)
            .values_list("register_number", flat=True)
        )
        dept_lookup = {
            d.name.strip().lower(): d
            for d in Department.objects.filter(college=college)
        }

        file_bytes = uploaded.read()
        rows, global_errors = parse_and_validate(
            file_bytes,
            existing_register_numbers=existing,
            department_lookup=dept_lookup,
        )

        request.session["bulk_import_rows"] = _serialise_rows(rows)
        request.session["bulk_import_global_errors"] = global_errors
        request.session["bulk_import_college_id"] = college.id

        total = len(rows)
        valid = sum(1 for r in rows if r.is_valid)
        invalid = total - valid

        return render(request, "bulk_add_students.html", {
            "college": college,
            "rows": _serialise_rows(rows),
            "global_errors": global_errors,
            "total": total,
            "valid_count": valid,
            "invalid_count": invalid,
            "preview_mode": True,
        })

    return render(request, "bulk_add_students.html", {
        "college": college,
        "preview_mode": False,
    })


# -----------------------------------------------------
# 2. DOWNLOAD TEMPLATE
# -----------------------------------------------------
@login_required
def bulk_download_template(request):
    profile, err = _require_admin(request)
    if err:
        return err

    buf = build_template_workbook()
    response = HttpResponse(
        buf.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
    response["Content-Disposition"] = (
        'attachment; filename="student_bulk_upload_template.xlsx"'
    )
    return response


# -----------------------------------------------------
# 3. CONFIRM IMPORT
# -----------------------------------------------------
@login_required
def bulk_import_confirm(request):
    """
    POST only. Reads the stashed rows, writes everything inside a single
    transaction. Refuses to import if any row is invalid.
    """
    profile, err = _require_admin(request)
    if err:
        return err

    if request.method != "POST":
        return redirect("bulk_add_students")

    college = profile.college
    session_rows = request.session.get("bulk_import_rows") or []
    session_college_id = request.session.get("bulk_import_college_id")

    if not session_rows or session_college_id != college.id:
        django_messages.error(request, "No pending import found. Please upload again.")
        return redirect("bulk_add_students")

    rows = _rows_from_session(session_rows)

    invalid = [r for r in rows if not r.is_valid]
    if invalid:
        django_messages.error(
            request,
            f"Cannot import — {len(invalid)} row(s) still have errors. "
            f"Fix them and re-upload.",
        )
        return redirect("bulk_add_students")

    # Rebuild dept lookup fresh
    dept_lookup = {
        d.name.strip().lower(): d
        for d in Department.objects.filter(college=college)
    }

    created_students = 0
    created_parents = 0

    try:
        with transaction.atomic():
            for row in rows:
                dept = dept_lookup.get(row.department_name.strip().lower())
                if dept is None:
                    raise ValueError(
                        f"Row {row.row_number}: department "
                        f"'{row.department_name}' disappeared."
                    )

                # Safety net — DB may have changed since upload
                if Student.objects.filter(
                    register_number=row.register_number
                ).exists():
                    raise ValueError(
                        f"Row {row.row_number}: Student ID "
                        f"{row.register_number} was created after upload."
                    )

                # Create the Django login user (same pattern as add_student)
                user = User.objects.create_user(
                    username=row.register_number,
                    password=row.register_number,   # default password
                    first_name=row.name,
                    email=row.email or "",
                )

                UserProfile.objects.create(
                    user=user,
                    college=college,
                    role="STUDENT",
                )

                student = Student.objects.create(
                    user=user,
                    college=college,
                    department=dept,
                    register_number=row.register_number,
                    email=row.email or "",
                    phone=row.phone or "",
                    gender=row.gender or "",
                    dob=row.dob,
                    year=row.year,
                    section=row.section or "",
                )
                created_students += 1

                # Parents (max 2, guaranteed by layout)
                for p in row.parents[:2]:
                    Parent.objects.create(
                        student=student,
                        name=p.name,
                        email=p.email,
                        phone=p.phone or "",
                        relationship=p.relationship,
                        preferred_language="en",
                        receive_email=True,
                    )
                    created_parents += 1

    except Exception as e:
        django_messages.error(
            request,
            f"Import failed — nothing was saved. {e}",
        )
        return redirect("bulk_add_students")

    # Clear session
    request.session.pop("bulk_import_rows", None)
    request.session.pop("bulk_import_global_errors", None)
    request.session.pop("bulk_import_college_id", None)

    django_messages.success(
        request,
        f"✓ Imported {created_students} student(s) and "
        f"{created_parents} parent(s). "
        f"Each new student's default password = their Student ID.",
    )
    return redirect("manage_students")


# -----------------------------------------------------
# 4. DOWNLOAD ERROR REPORT
# -----------------------------------------------------
@login_required
def bulk_download_error_report(request):
    profile, err = _require_admin(request)
    if err:
        return err

    session_rows = request.session.get("bulk_import_rows") or []
    if not session_rows:
        django_messages.error(request, "No pending validation results.")
        return redirect("bulk_add_students")

    rows = _rows_from_session(session_rows)
    buf = build_error_report(rows)

    response = HttpResponse(
        buf.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
    response["Content-Disposition"] = (
        'attachment; filename="bulk_import_errors.xlsx"'
    )
    return response