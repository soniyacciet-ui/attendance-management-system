"""
URL configuration for attendance_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from attendance import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('',views.home,name='home'),

    path('login/',views.login_view,name='login'),

    path("signup/", views.signup, name="signup"),

     path("admin-dashboard/",views.admin_dashboard,name="admin_dashboard"),

     path("admin-stats-api/", views.admin_stats_api, name="admin_stats_api"),

     path(
    "manage-students/",
    views.manage_students,
    name="manage_students"
),

path(
    "departments/",
    views.manage_departments,
    name="manage_departments"
),

path(
    "department/<int:department_id>/",
    views.department_details,
    name="department_details"
),

path(
    "department/<int:department_id>/add-student/",
    views.add_student,
    name="add_student"
),

path(
    "department/add/",
    views.add_department,
    name="add_department"
),

path(
    "department/<int:department_id>/add-staff/",
    views.add_staff,
    name="add_staff"
),

path(
    "department/<int:department_id>/add-hod/",
    views.add_hod,
    name="add_hod"
),

path(
    "staff/<int:staff_id>/edit/",
    views.edit_staff,
    name="edit_staff"
),

path(
    "staff/<int:staff_id>/delete/",
    views.delete_staff,
    name="delete_staff"
),

path(
    "student/<int:student_id>/edit/",
    views.edit_student,
    name="edit_student"
),

path(
    "student/<int:student_id>/delete/",
    views.delete_student,
    name="delete_student"
),

path(
    'department/<int:department_id>/students/',
    views.department_students,
    name='department_students'
),

path(
    'department/<int:department_id>/staff/',
    views.department_staff,
    name='department_staff'
),

path(
    'department/<int:department_id>/hod/',
    views.department_hod,
    name='department_hod'
),

path(
    "student/dashboard/",
    views.student_dashboard,
    name="student_dashboard"
),

path(
    "logout/",
    auth_views.LogoutView.as_view(next_page="/"),
    name="logout"
),

path(
    "department/<int:department_id>/attendance/",
    views.mark_attendance,
    name="mark_attendance"
),

path(
    "staff/dashboard/",
    views.staff_dashboard,
    name="staff_dashboard"
),

path(
    "department/<int:department_id>/attendance-settings/",
    views.attendance_settings,
    name="attendance_settings"
),

path(
    "department/<int:department_id>/change-hod/",
    views.change_hod,
    name="change_hod"
),

path("reports/", 
     views.attendance_reports, 
     name="attendance_reports"
),

path("reports/download/", 
     views.download_attendance_report, 
     name="download_attendance_report"
),

path("reports/download-summary/", 
     views.download_summary_report, 
     name="download_summary_report"
),

path("reports/email/", 
     views.email_report, 
     name="email_report"
),

path("calendar/", 
     views.attendance_calendar, 
     name="attendance_calendar"
),

path("parents/add/<int:student_id>/",
      views.add_parent, 
      name="add_parent"
),

path("notifications/send/<int:student_id>/", 
     views.notify_low_attendance, 
     name="notify_low_attendance"
),

path("notifications/inbox/", 
     views.parent_notifications, 
     name="parent_notifications"
),

path("notifications/change-language/", 
     views.change_language, 
     name="change_language"
),

path("department/<int:department_id>/subjects/", 
     views.manage_subjects, 
     name="manage_subjects"
),

path("subjects/<int:subject_id>/delete/", 
     views.delete_subject, 
     name="delete_subject"
),

path("department/<int:department_id>/periods/", 
     views.manage_periods, 
     name="manage_periods"
),

path("periods/<int:period_id>/edit/", 
     views.edit_period, 
     name="edit_period"
),

path("periods/<int:period_id>/delete/", 
     views.delete_period, 
    name="delete_period"
),

path("department/<int:department_id>/periods/auto/", 
     views.auto_create_periods, 
     name="auto_create_periods"
),

path("manage-staff/", 
     views.manage_staff, 
     name="manage_staff"
),

path("manage-hods/", 
     views.manage_hods, 
     name="manage_hods"
),

path("manage-users/", 
     views.manage_users, 
     name="manage_users"
),

path("view-attendance/", 
     views.view_attendance, 
     name="view_attendance"
),

path("college-settings/", 
     views.college_settings, 
     name="college_settings"
),

path("access-control/", 
    views.access_control, 
    name="access_control"
),

path("admin-profile/", 
    views.admin_profile, 
    name="admin_profile"
),

path("attendance-percentage-settings/", 
     views.attendance_percentage_settings, 
     name="attendance_percentage_settings"
),

path("academic-year-settings/", 
     views.academic_year_settings, 
     name="academic_year_settings"
),

path("attendance-rules/", 
     views.attendance_rules, 
     name="attendance_rules"
),

path("add-college/", views.add_college, name="add_college"),
path("manage-colleges/", views.manage_colleges, name="manage_colleges"),
path("switch-college/<int:college_id>/", views.switch_college, name="switch_college"),
path("audit-log/", views.attendance_audit_log, name="attendance_audit_log"),
path("student/portal/", views.student_portal, name="student_portal"),
path("student/dispute/<int:attendance_id>/", views.raise_dispute, name="raise_dispute"),
path("disputes/", views.manage_disputes, name="manage_disputes"),
path("disputes/<int:dispute_id>/review/", views.review_dispute, name="review_dispute"),
    # ---------- Bulk Student Import ----------
    path(
        "students/bulk-add/",
        views.bulk_add_students,
        name="bulk_add_students",
    ),
    path(
        "students/bulk-add/download-template/",
        views.bulk_download_template,
        name="bulk_download_template",
    ),
    path(
        "students/bulk-add/confirm/",
        views.bulk_import_confirm,
        name="bulk_import_confirm",
    ),
    path(
        "students/bulk-add/error-report/",
        views.bulk_download_error_report,
        name="bulk_download_error_report",
    ),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
