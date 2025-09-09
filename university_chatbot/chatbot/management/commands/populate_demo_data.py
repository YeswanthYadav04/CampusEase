# chatbot/management/commands/populate_demo_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from chatbot.models import Student, Lecture, AttendanceRecord
from datetime import datetime, timedelta
import json
import os

class Command(BaseCommand):
    help = 'Populates the database with demo student data'

    def handle(self, *args, **options):
        # Create demo students
        students_data = [
            {
                'username': 'student1',
                'password': 'demo123',
                'first_name': 'Rahul',
                'last_name': 'Sharma',
                'enrollment_no': 'PU20231001',
                'semester': 4,
                'department': 'Computer Science'
            },
            {
                'username': 'student2',
                'password': 'demo123',
                'first_name': 'Priya',
                'last_name': 'Patel',
                'enrollment_no': 'PU20231002',
                'semester': 4,
                'department': 'Computer Science'
            },
            {
                'username': 'student3',
                'password': 'demo123',
                'first_name': 'Amit',
                'last_name': 'Verma',
                'enrollment_no': 'PU20231003',
                'semester': 4,
                'department': 'Computer Science'
            }
        ]

        # Get the path to the timetable.json file
        timetable_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'timetable.json')
        
        # Load timetable data
        try:
            with open(timetable_path, 'r') as f:
                timetable_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Timetable file not found. Please create chatbot/data/timetable.json'))
            return

        for student_info in students_data:
            # Create user
            user, created = User.objects.get_or_create(
                username=student_info['username'],
                defaults={
                    'first_name': student_info['first_name'],
                    'last_name': student_info['last_name']
                }
            )
            if created:
                user.set_password(student_info['password'])
                user.save()

            # Create student profile
            student, created = Student.objects.get_or_create(
                user=user,
                defaults={
                    'enrollment_no': student_info['enrollment_no'],
                    'semester': student_info['semester'],
                    'department': student_info['department'],
                    'current_attendance': 75.0  # Default attendance
                }
            )

            # Create attendance records for each subject
            subjects = set()
            for day, slots in timetable_data['Timetable'].items():
                for slot, details in slots.items():
                    if 'subject' in details:
                        subjects.add(details['subject'])
            
            for subject in subjects:
                AttendanceRecord.objects.get_or_create(
                    student=student,
                    subject=subject,
                    defaults={
                        'total_classes': 30,
                        'attended_classes': 22  # ~73% attendance
                    }
                )

            # Create lecture records for the next 2 weeks
            start_date = datetime.now().date()
            for i in range(14):  # Next 2 weeks
                current_date = start_date + timedelta(days=i)
                day_name = current_date.strftime('%A').lower()
                
                if day_name in timetable_data['Timetable']:
                    day_schedule = timetable_data['Timetable'][day_name]
                    
                    for time_slot, details in day_schedule.items():
                        if 'subject' in details:
                            Lecture.objects.get_or_create(
                                student=student,
                                day=day_name,
                                time_slot=time_slot,
                                subject=details['subject'],
                                defaults={
                                    'faculty': details.get('faculty', ''),
                                    'email': details.get('email', ''),
                                    'classroom': details.get('classroom', ''),
                                    'date': current_date,
                                    'is_attended': False  # Initially not attended
                                }
                            )

        self.stdout.write(self.style.SUCCESS('Demo data populated successfully!'))