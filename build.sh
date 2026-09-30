#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Force-create superuser using Python (reliable)
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_management.settings')
django.setup()
from django.contrib.auth.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'soniya.c.ciet@gmail.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin@123456')

user, created = User.objects.get_or_create(username=username)
user.email = email
user.is_staff = True
user.is_superuser = True
user.set_password(password)
user.save()

print('===== SUPERUSER READY =====')
print('Username:', username)
print('Email:', email)
print('Password length:', len(password))
print('===========================')

# Also create UserProfile + College if missing
from attendance.models import College, UserProfile, Department

if not College.objects.exists():
    college = College.objects.create(
        college_id='CIET',
        name='My College',
        attendance_percentage=75
    )
    print('Created College:', college.name)
else:
    college = College.objects.first()

profile, _ = UserProfile.objects.get_or_create(
    user=user,
    defaults={'college': college, 'role': 'ADMIN'}
)
print('Profile role:', profile.role)

if not Department.objects.filter(college=college).exists():
    Department.objects.create(
        college=college,
        name='AI&DS',
        attendance_required=75.0
    )
    print('Created Department: AI&DS')

print('===== SETUP COMPLETE =====')
"#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Force-create superuser using Python (reliable)
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_management.settings')
django.setup()
from django.contrib.auth.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'soniya.c.ciet@gmail.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin@123456')

user, created = User.objects.get_or_create(username=username)
user.email = email
user.is_staff = True
user.is_superuser = True
user.set_password(password)
user.save()

print('===== SUPERUSER READY =====')
print('Username:', username)
print('Email:', email)
print('Password length:', len(password))
print('===========================')

# Also create UserProfile + College if missing
from attendance.models import College, UserProfile, Department

if not College.objects.exists():
    college = College.objects.create(
        college_id='CIET',
        name='My College',
        attendance_percentage=75
    )
    print('Created College:', college.name)
else:
    college = College.objects.first()

profile, _ = UserProfile.objects.get_or_create(
    user=user,
    defaults={'college': college, 'role': 'ADMIN'}
)
print('Profile role:', profile.role)

if not Department.objects.filter(college=college).exists():
    Department.objects.create(
        college=college,
        name='AI&DS',
        attendance_required=75.0
    )
    print('Created Department: AI&DS')

print('===== SETUP COMPLETE =====')
"