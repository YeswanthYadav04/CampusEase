# chatbot/views.py
# In views.py, update the import line
from .utils import (
    translate_text, 
    detect_language, 
    calculate_similarity, 
    enhanced_document_search,
    understand_query
)
from django.conf import settings

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.utils.translation import activate, get_language
from django.core.files.storage import FileSystemStorage
from .models import Document, FAQ, AttendanceRecord, Timetable, Student,Lecture
from .forms import DocumentForm, FAQForm
from .utils import translate_text
import json
import os
import re
from datetime import datetime, timedelta

# Add the home view at the top
def home(request):
    return render(request, 'chatbot/home.html')

# Add the student_login view if it's missing
def student_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chat_interface')
        else:
            return render(request, 'chatbot/login.html', {'error': 'Invalid credentials'})
    return render(request, 'chatbot/login.html')

# Add the admin_login view if it's missing
def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'chatbot/admin_login.html', {'error': 'Invalid admin credentials'})
    return render(request, 'chatbot/admin_login.html')

# Add the chat_interface view if it's missing
@login_required
def chat_interface(request):
    return render(request, 'chatbot/chat.html')

# Add the set_language view if it's missing
def set_language(request):
    if request.method == 'POST':
        language = request.POST.get('language', 'en')
        activate(language)
        response = JsonResponse({'status': 'success'})
        response.set_cookie('django_language', language)
        return response
    return JsonResponse({'status': 'error'})

# Helper function to check if user is admin
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    documents = Document.objects.all().order_by('-uploaded_at')
    faqs = FAQ.objects.all()
    
    if request.method == 'POST':
        # Handle document upload
        if 'upload_document' in request.POST:
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                document = form.save(commit=False)
                document.save()
                return redirect('admin_dashboard')
        # Handle FAQ creation
        elif 'add_faq' in request.POST:
            faq_form = FAQForm(request.POST)
            if faq_form.is_valid():
                faq_form.save()
                return redirect('admin_dashboard')
    else:
        form = DocumentForm()
        faq_form = FAQForm()
    
    return render(request, 'chatbot/admin_dashboard.html', {
        'documents': documents,
        'faqs': faqs,
        'form': form,
        'faq_form': faq_form,
    })

@login_required
@user_passes_test(is_admin)
def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == 'POST':
        document.delete()
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def delete_faq(request, faq_id):
    faq = get_object_or_404(FAQ, id=faq_id)
    if request.method == 'POST':
        faq.delete()
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')

@login_required
def download_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    # Check if the file exists
    if not document.file or not document.file.storage.exists(document.file.name):
        return HttpResponse("File not found. Please contact administrator.", status=404)
    
    try:
        # Serve the file for download
        response = HttpResponse(document.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{document.filename()}"'
        return response
    except Exception as e:
        return HttpResponse(f"Error downloading file: {str(e)}", status=500)

def detect_language(text):
    """
    Improved language detection that handles mixed language text
    """
    if not text or not isinstance(text, str):
        return 'en'
    
    text = text.lower()
    
    # Count Hindi characters (Devanagari Unicode block)
    hindi_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
    # Count Gujarati characters (Gujarati Unicode block)
    gujarati_chars = sum(1 for char in text if '\u0A80' <= char <= '\u0AFF')
    # Count English letters
    english_chars = sum(1 for char in text if 'a' <= char <= 'z')
    
    total_chars = len(text)
    
    # If significant Hindi characters found, treat as Hindi
    if hindi_chars > 0 and (hindi_chars / total_chars > 0.1 or hindi_chars >= 2):
        return 'hi'
    # If significant Gujarati characters found, treat as Gujarati
    elif gujarati_chars > 0 and (gujarati_chars / total_chars > 0.1 or gujarati_chars >= 2):
        return 'gu'
    else:
        return 'en'

def extract_english_keywords(text):
    """
    Extract English keywords from mixed language text
    """
    # Common academic keywords to look for
    academic_keywords = [
        'ppt', 'notes', 'pdf', 'syllabus', 'assignment', 'project',
        'unit', 'chapter', 'lecture', 'subject', 'document', 'file'
    ]
    
    # Extract words that look like English (basic approach)
    words = text.split()
    english_words = []
    
    for word in words:
        # If word contains mostly English letters or is an academic keyword
        if (any('a' <= char <= 'z' for char in word) and 
            not any('\u0900' <= char <= '\u097F' for char in word) and
            not any('\u0A80' <= char <= '\u0AFF' for char in word)):
            english_words.append(word.lower())
        # Check if it's an academic keyword even if mixed
        elif any(keyword in word.lower() for keyword in academic_keywords):
            for keyword in academic_keywords:
                if keyword in word.lower():
                    english_words.append(keyword)
    
    return ' '.join(english_words)

def translate_to_english(text, source_language):
    """
    Translate Hindi and Gujarati academic terms to English
    """
    if source_language == 'hi':
        # Hindi to English translation
        hindi_to_english = {
            'chahiye': 'need', 'mujhe': 'i', 'mein': 'in', 'ka': 'of', 'ki': 'of',
            'notes': 'notes', 'ppt': 'ppt', 'syllabus': 'syllabus', 'book': 'book',
            'assignment': 'assignment', 'project': 'project', 'report': 'report',
            'unit': 'unit', 'chapter': 'chapter', 'lecture': 'lecture', 'class': 'class',
            'myjhe': 'i', 'chaihye': 'need', 'chahiye': 'need', 'mujhe': 'i',
            'unit1': '1', 'unit2': '2', 'unit3': '3', 'unit4': '4', 'unit5': '5',
            'unit6': '6', 'unit7': '7', 'unit8': '8', 'unit9': '9', 'unit10': '10',
            'ek': '1', 'do': '2', 'teen': '3', 'char': '4', 'panch': '5',
            'che': '6', 'saat': '7', 'aath': '8', 'nau': '9', 'das': '10',
            'pustak': 'book', 'kaksha': 'class', 'path': 'chapter', 'prashn': 'question'
        }
        translation_dict = hindi_to_english
    
    elif source_language == 'gu':
        # Gujarati to English translation
        gujarati_to_english = {
            'joiye': 'need', 'mane': 'i', 'ma': 'in', 'no': 'of', 'ni': 'of',
            'notes': 'notes', 'ppt': 'ppt', 'syllabus': 'syllabus', 'pustak': 'book',
            'assignment': 'assignment', 'project': 'project', 'report': 'report',
            'unit': 'unit', 'chapter': 'chapter', 'lecture': 'lecture', 'class': 'class',
            'mane': 'i', 'joiye': 'need', 'jaroor': 'need',
            'unit1': '1', 'unit2': '2', 'unit3': '3', 'unit4': '4', 'unit5': '5',
            'unit6': '6', 'unit7': '7', 'unit8': '8', 'unit9': '9', 'unit10': '10',
            'ek': '1', 'be': '2', 'tran': '3', 'char': '4', 'panch': '5',
            'cha': '6', 'sat': '7', 'aath': '8', 'nav': '9', 'das': '10',
            'pustak': 'book', 'kaksha': 'class', 'prakaran': 'chapter', 'prashna': 'question'
        }
        translation_dict = gujarati_to_english
    
    else:
        return text.lower()
    
    translated_words = []
    for word in text.split():
        lower_word = word.lower()
        if lower_word in translation_dict:
            translated_words.append(translation_dict[lower_word])
        else:
            # Keep English words, numbers, and subject names as they are
            if (any('a' <= char <= 'z' for char in lower_word) or 
                any('0' <= char <= '9' for char in lower_word) or
                len(lower_word) > 2):  # Assume longer words might be subject names
                translated_words.append(lower_word)
    
    return ' '.join(translated_words)

def search_documents_logical(query, documents):
    """
    Logical document search that follows subject -> unit -> type hierarchy
    """
    query = query.lower()
    query_words = query.split()
    
    # Get all available subjects from the database (dynamic)
    available_subjects = list(Document.objects.values_list('subject', flat=True).distinct())
    available_subjects_lower = [subject.lower() for subject in available_subjects]
    
    # Extract requested subject (check against available subjects)
    requested_subject = None
    for word in query_words:
        if word in available_subjects_lower:
            requested_subject = available_subjects[available_subjects_lower.index(word)]
            break
    
    # If no exact subject match, try partial matches
    if not requested_subject:
        for subject in available_subjects:
            subject_lower = subject.lower()
            # Check if any query word is in the subject name
            if any(word in subject_lower for word in query_words if len(word) > 3):
                requested_subject = subject
                break
    
    # Extract requested unit
    requested_unit = None
    for word in query_words:
        if word.isdigit():
            requested_unit = int(word)
            break
    
    # Extract requested document type
    requested_type = None
    doc_types = {
        'ppt': 'ppt', 'powerpoint': 'ppt', 'presentation': 'ppt',
        'notes': 'notes', 'note': 'notes',
        'syllabus': 'syllabus', 'syllabi': 'syllabus',
        'assignment': 'assignment', 'assignments': 'assignment',
        'circular': 'circular', 'circulars': 'circular',
        'question': 'question_paper', 'paper': 'question_paper', 'exam': 'question_paper'
    }
    
    for word in query_words:
        if word in doc_types:
            requested_type = doc_types[word]
            break
    
    # Filter documents step by step
    filtered_docs = documents
    
    # Step 1: Filter by subject (if requested)
    if requested_subject:
        subject_docs = [doc for doc in filtered_docs if doc.subject.lower() == requested_subject.lower()]
        if not subject_docs:
            return []  # No documents for this subject
        filtered_docs = subject_docs
    else:
        # If subject was requested but not found, return empty
        # Check if user was trying to ask for a specific subject
        subject_keywords = ['se', 'daa', 'dvd', 'ep', 'toc', 'aws', 'pce', 'software', 'engineering', 
                           'design', 'algorithm', 'data', 'visualization', 'analytics', 
                           'enterprise', 'programming', 'theory', 'computation', 'professionalism', 'corporate', 'ethics']
        
        if any(keyword in query for keyword in subject_keywords):
            # User was asking for a subject but we couldn't match it exactly
            return []
    
    # Step 2: Filter by unit (if requested)
    if requested_unit is not None:
        unit_docs = [doc for doc in filtered_docs if doc.unit == requested_unit]
        if not unit_docs:
            return []  # No documents for this unit
        filtered_docs = unit_docs
    
    # Step 3: Filter by document type (if requested)
    if requested_type:
        type_docs = [doc for doc in filtered_docs if doc.doc_type == requested_type]
        if not type_docs:
            return []  # No documents of this type
        filtered_docs = type_docs
    
    return filtered_docs

def get_file_icon(doc_type):
    """Return appropriate icon for file type"""
    icons = {
        'ppt': '📊',
        'notes': '📝',
        'syllabus': '📄',
        'circular': '📢',
        'assignment': '📋',
        'question_paper': '📑',
    }
    return icons.get(doc_type, '📄')

def get_available_subjects():
    """Get all available subjects from the database"""
    return list(Document.objects.values_list('subject', flat=True).distinct())

# Add this function to get the current student
def get_current_student(user):
    try:
        return Student.objects.get(user=user)
    except Student.DoesNotExist:
        return None

# Add this function to get current lecture
# Fix the get_current_lecture function
def get_current_lecture(student):
    now = datetime.now()
    current_time = now.time()
    current_day = now.strftime('%A').lower()
    
    try:
        # Get today's lectures
        today_lectures = Lecture.objects.filter(
            student=student,
            day=current_day,
            date=now.date()
        )
        
        for lecture in today_lectures:
            start_str, end_str = lecture.time_slot.split('-')
            start_time = datetime.strptime(start_str, '%H:%M').time()  # Fixed format
            end_time = datetime.strptime(end_str, '%H:%M').time()  # Fixed format
            
            if start_time <= current_time <= end_time:
                return lecture
    except Exception as e:
        print(f"Error getting current lecture: {e}")
    
    return None

# Add this function to calculate attendance projection
def calculate_attendance_projection(current_percentage, target_percentage, total_classes, attended_classes):
    if current_percentage >= target_percentage:
        return 0, "You have already achieved your target attendance!"
    
    # Calculate how many more classes need to be attended to reach target
    # Formula: (attended + x) / (total + x) = target/100
    # Solving for x: x = (target * total - 100 * attended) / (100 - target)
    
    if target_percentage == 100:
        # Special case for 100% target
        needed = total_classes - attended_classes
        return needed, f"You need to attend all remaining {needed} classes to reach 100% attendance."
    
    x = (target_percentage * total_classes - 100 * attended_classes) / (100 - target_percentage)
    needed = max(0, round(x))
    
    if needed == 0:
        return 0, "You're very close to your target! Just maintain your attendance."
    
    return needed, f"You need to attend {needed} more classes to reach {target_percentage}% attendance."

def get_remaining_classes(student, subject):
    """Calculate remaining classes for a subject based on timetable and academic calendar"""
    try:
        # Load timetable data
        with open('chatbot/data/timetable.json', 'r') as f:
            timetable_data = json.load(f)
        
        # Load academic calendar
        with open('chatbot/data/academic_calendar_2025_odd_term.json', 'r') as f:
            calendar_data = json.load(f)
        
        # Get today's date
        today = datetime.now().date()
        
        # Find all future classes for this subject
        remaining_classes = []
        
        # Check each day in the timetable
        for day_name, day_schedule in timetable_data['Timetable'].items():
            for time_slot, details in day_schedule.items():
                if 'subject' in details and details['subject'] == subject:
                    # This is a class for the requested subject
                    # We need to find all future occurrences of this class
                    
                    # Calculate next occurrence of this day
                    day_map = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 
                              'thursday': 3, 'friday': 4, 'saturday': 5}
                    current_weekday = today.weekday()
                    target_weekday = day_map[day_name.lower()]
                    
                    # Days until next occurrence
                    days_until = (target_weekday - current_weekday) % 7
                    if days_until == 0:
                        # Today is the day, check if class is in future
                        start_time_str = time_slot.split('-')[0]
                        start_time = datetime.strptime(start_time_str, '%H:%M').time()
                        current_time = datetime.now().time()
                        
                        if current_time < start_time:
                            days_until = 0  # Class is later today
                        else:
                            days_until = 7  # Class is next week
                    elif days_until < 0:
                        days_until += 7
                    
                    class_date = today + timedelta(days=days_until)
                    
                    # Check if this date is within academic calendar and not a holiday
                    date_str = class_date.isoformat()
                    if date_str in calendar_data['Academic Calendar']['Daywise Schedule']:
                        events = calendar_data['Academic Calendar']['Daywise Schedule'][date_str]
                        if 'Teaching' in str(events) or 'Weekly' in str(events):
                            # This is a teaching day, add to remaining classes
                            remaining_classes.append({
                                'date': class_date,
                                'time_slot': time_slot,
                                'classroom': details.get('classroom', '')
                            })
        
        return remaining_classes
        
    except Exception as e:
        print(f"Error calculating remaining classes: {e}")
        return None

def debug_language_detection(request):
    """
    Debug function to test language detection
    """
    if request.method == 'POST':
        text = request.POST.get('text', '')
        
        # Test all detection methods
        detected_lang = detect_language(text)
        
        # Count characters for each language
        hindi_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
        gujarati_chars = sum(1 for char in text if '\u0A80' <= char <= '\u0AFF')
        english_chars = sum(1 for char in text if 'a' <= char <= 'z' or 'A' <= char <= 'Z')
        total_chars = len(text)
        
        # Calculate percentages
        hindi_percent = (hindi_chars / total_chars * 100) if total_chars > 0 else 0
        gujarati_percent = (gujarati_chars / total_chars * 100) if total_chars > 0 else 0
        english_percent = (english_chars / total_chars * 100) if total_chars > 0 else 0
        
        # Log the detection details for debugging
        print(f"Text: {text}")
        print(f"Detected language: {detected_lang}")
        print(f"Hindi characters: {hindi_chars} ({hindi_percent:.1f}%)")
        print(f"Gujarati characters: {gujarati_chars} ({gujarati_percent:.1f}%)")
        print(f"English characters: {english_chars} ({english_percent:.1f}%)")
        print(f"Total characters: {total_chars}")
        
        # Try translation to test the translation function
        translated_text = ""
        if detected_lang != 'en' and detected_lang in ['hi', 'gu']:
            try:
                translated_text = translate_text(text, 'en')
                print(f"Translated to English: {translated_text}")
            except Exception as e:
                print(f"Translation error: {e}")
                translated_text = "Translation failed"
        
        return JsonResponse({
            'text': text,
            'detected_language': detected_lang,
            'hindi_chars': hindi_chars,
            'hindi_percent': round(hindi_percent, 1),
            'gujarati_chars': gujarati_chars,
            'gujarati_percent': round(gujarati_percent, 1),
            'english_chars': english_chars,
            'english_percent': round(english_percent, 1),
            'total_chars': total_chars,
            'translated_text': translated_text
        })
    
    return render(request, 'chatbot/debug_language.html')


def get_faculty_schedule(faculty_name):
    """Get the schedule for a specific faculty"""
    try:
        # Try to load timetable data with multiple fallback paths
        timetable_paths = [
            'chatbot/data/timetable.json',
            'data/timetable.json',
            os.path.join(settings.BASE_DIR, 'chatbot/data/timetable.json'),
            os.path.join(settings.BASE_DIR, 'data/timetable.json')
        ]
        
        timetable_data = None
        for path in timetable_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        timetable_data = json.load(f)
                    break
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Failed to load timetable from {path}: {e}")
                continue
        
        if not timetable_data:
            print("Could not load timetable data from any path")
            return None
        
        faculty_schedule = {}
        faculty_name_lower = faculty_name.lower()
        
        # Check if we have the expected timetable structure
        if 'Timetable' not in timetable_data:
            print("Timetable data does not contain 'Timetable' key")
            # Try to use the root object as timetable
            timetable_data = {'Timetable': timetable_data}
        
        for day, slots in timetable_data['Timetable'].items():
            if not isinstance(slots, dict):
                continue
                
            for time_slot, details in slots.items():
                if not isinstance(details, dict):
                    continue
                    
                # Check if faculty field exists and matches
                if 'faculty' in details and details['faculty']:
                    # Case-insensitive partial matching
                    if faculty_name_lower in details['faculty'].lower():
                        if day not in faculty_schedule:
                            faculty_schedule[day] = []
                        
                        faculty_schedule[day].append({
                            'time_slot': time_slot,
                            'subject': details.get('subject', 'Unknown Subject'),
                            'classroom': details.get('classroom', 'Unknown Classroom'),
                            'faculty': details.get('faculty', 'Unknown Faculty')
                        })
        
        # If no schedule found, try fuzzy matching
        if not faculty_schedule:
            print(f"No exact match found for {faculty_name}, trying fuzzy matching")
            faculty_schedule = fuzzy_faculty_search(faculty_name, timetable_data)
        
        return faculty_schedule if faculty_schedule else None
        
    except Exception as e:
        print(f"Error getting faculty schedule: {e}")
        import traceback
        traceback.print_exc()
        return None


def fuzzy_faculty_search(faculty_name, timetable_data):
    """
    Fuzzy matching for faculty names when exact match fails
    """
    faculty_schedule = {}
    faculty_name_lower = faculty_name.lower()
    
    # Common name variations and abbreviations
    name_variations = {
        'gaurav': ['gaurav', 'gaurav soni', 'soni'],
        'keerthana': ['keerthana', 'keerthana s', 'keerthi'],
        'anand': ['anand', 'anand javdekar', 'javdekar'],
        'pratima': ['pratima', 'pratima chaudhari', 'chaudhari'],
        'gauri': ['gauri', 'gauri upreti', 'upreti'],
        'nidhi': ['nidhi', 'nidhi patel', 'patel'],
        'nithya': ['nithya', 'nithya arumugam', 'arumugam']
    }
    
    # Find possible name variations
    possible_names = []
    for base_name, variations in name_variations.items():
        if any(variation in faculty_name_lower for variation in variations):
            possible_names.extend(variations)
    
    # If no variations found, use the original name
    if not possible_names:
        possible_names = [faculty_name_lower]
    
    # Search for any matching faculty
    for day, slots in timetable_data['Timetable'].items():
        if not isinstance(slots, dict):
            continue
            
        for time_slot, details in slots.items():
            if not isinstance(details, dict):
                continue
                
            if 'faculty' in details and details['faculty']:
                current_faculty_lower = details['faculty'].lower()
                
                # Check if any possible name matches
                for possible_name in possible_names:
                    if possible_name in current_faculty_lower:
                        if day not in faculty_schedule:
                            faculty_schedule[day] = []
                        
                        faculty_schedule[day].append({
                            'time_slot': time_slot,
                            'subject': details.get('subject', 'Unknown Subject'),
                            'classroom': details.get('classroom', 'Unknown Classroom'),
                            'faculty': details.get('faculty', 'Unknown Faculty')
                        })
                        break
    
    return faculty_schedule

# Update the process_message function to include the new features
@login_required
def process_message(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        user_language = detect_language(user_message)
        
        # First, understand the query type
        query_type = understand_query(user_message)
        
        # Translate non-English queries to English for processing
        if user_language != 'en':
            search_query = translate_text(user_message, 'en')
        else:
            search_query = user_message.lower()
        
        response_text = "I'm sorry, I didn't understand that. Could you rephrase?"
        response_type = "text"
        
        # Get current student
        student = get_current_student(request.user)
        
        # Process based on query type
        if query_type == 'document_request':
            # Use enhanced document search
            documents = Document.objects.filter(is_active=True)
            found_docs = enhanced_document_search(search_query, list(documents))
            
            if found_docs:
                response_text = "I found these documents for you:\n"
                for doc in found_docs[:5]:  # Limit to 5 results
                    download_url = f"/download-document/{doc.id}/"
                    icon = get_file_icon(doc.doc_type)
                    unit_info = f" (Unit {doc.unit})" if doc.unit else ""
                    response_text += f"- {icon} <a href='{download_url}' style='color: #3f51b5; text-decoration: none;' target='_blank'>{doc.title}{unit_info}</a>\n"
                response_type = "html"
            else:
                # Provide helpful feedback
                available_subjects = get_available_subjects()
                response_text = f"I couldn't find documents matching your request. Available subjects: {', '.join(available_subjects)}. Please contact admin if you need specific documents."
        
        elif query_type == 'attendance_query':
            if student:
                # Improved subject detection logic
                subject_attendance = None
                
                # First, get all subjects for this student
                all_subjects = AttendanceRecord.objects.filter(student=student).values_list('subject', flat=True)
                
                # Check if the query contains any specific subject name
                for subject in all_subjects:
                    # Check if the subject name (or significant part of it) is in the query
                    subject_words = subject.lower().split()
                    for word in subject_words:
                        if len(word) > 3 and word in search_query:  # Only check words longer than 3 characters
                            subject_attendance = AttendanceRecord.objects.filter(
                                student=student, 
                                subject=subject
                            ).first()
                            break
                    if subject_attendance:
                        break
                
                # If no specific subject found, check for common subject abbreviations
                if not subject_attendance:
                    subject_mappings = {
                        'daa': 'Design and Analysis of Algorithms',
                        'se': 'Software Engineering',
                        'dvd': 'Data Visualization & Data Analytics',
                        'ep': 'Enterprise Programming',
                        'toc': 'Theory of Computation',
                        'aws': 'AWS Fundamentals',
                        'pce': 'Professionalism & Corporate Ethics'
                    }
                    
                    for abbr, full_name in subject_mappings.items():
                        if abbr in search_query:
                            subject_attendance = AttendanceRecord.objects.filter(
                                student=student, 
                                subject=full_name
                            ).first()
                            if subject_attendance:
                                break
                
                if subject_attendance:
                    response_text = f"Your attendance in {subject_attendance.subject} is {subject_attendance.percentage}% ({subject_attendance.attended_classes}/{subject_attendance.total_classes} classes)."
                    
                    # Check if user is asking about target attendance
                    if any(word in search_query for word in ['target', 'reach', 'achieve', 'kitne', 'kaise', 'how many', 'percentage', '%']):
                        # Try to extract target percentage
                        target_percentage = None
                        words = search_query.split()
                        for i, word in enumerate(words):
                            if word.isdigit():
                                num = int(word)
                                if 0 <= num <= 100:
                                    target_percentage = num
                                    break
                            # Also check for percentage numbers like "85%"
                            elif '%' in word and word.replace('%', '').isdigit():
                                num = int(word.replace('%', ''))
                                if 0 <= num <= 100:
                                    target_percentage = num
                                    break
                        
                        if target_percentage:
                            needed, message = calculate_attendance_projection(
                                subject_attendance.percentage,
                                target_percentage,
                                subject_attendance.total_classes,
                                subject_attendance.attended_classes
                            )
                            
                            # Calculate when this target can be achieved based on timetable
                            if needed > 0:
                                # Get remaining classes from timetable
                                remaining_classes = get_remaining_classes(student, subject_attendance.subject)
                                if remaining_classes:
                                    # Calculate how many weeks it will take
                                    classes_per_week = len(remaining_classes)
                                    weeks_needed = (needed + classes_per_week - 1) // classes_per_week  # Ceiling division
                                    message += f" You can achieve this in approximately {weeks_needed} weeks."
                            
                            response_text += " " + message
                else:
                    # Calculate overall attendance across all subjects
                    attendance_records = AttendanceRecord.objects.filter(student=student)
                    if attendance_records:
                        total_classes = sum(record.total_classes for record in attendance_records)
                        attended_classes = sum(record.attended_classes for record in attendance_records)
                        
                        if total_classes > 0:
                            overall_percentage = round((attended_classes / total_classes) * 100, 2)
                            response_text = f"Your overall attendance is {overall_percentage}% ({attended_classes}/{total_classes} classes across all subjects)."
                            
                            # Check if user is asking about target overall attendance
                            if any(word in search_query for word in ['target', 'reach', 'achieve', 'kitne', 'kaise', 'how many', 'percentage', '%']):
                                # Try to extract target percentage
                                target_percentage = None
                                words = search_query.split()
                                for i, word in enumerate(words):
                                    if word.isdigit():
                                        num = int(word)
                                        if 0 <= num <= 100:
                                            target_percentage = num
                                            break
                                    elif '%' in word and word.replace('%', '').isdigit():
                                        num = int(word.replace('%', ''))
                                        if 0 <= num <= 100:
                                            target_percentage = num
                                            break
                                
                                if target_percentage:
                                    needed, message = calculate_attendance_projection(
                                        overall_percentage,
                                        target_percentage,
                                        total_classes,
                                        attended_classes
                                    )
                                    response_text += " " + message
                        else:
                            response_text = "No attendance records found for you."
                    else:
                        response_text = "No attendance records found for you."
            else:
                response_text = "I couldn't find your student profile. Please contact administration."
        
        elif query_type == 'timetable_query':
            if student:
                # Get today's day
                today = datetime.now().strftime('%A')
                response_text = f"Your timetable for {today}:\n"
                
                # Load timetable data
                with open('chatbot/data/timetable.json', 'r') as f:
                    timetable_data = json.load(f)
                
                today_schedule = timetable_data['Timetable'].get(today.lower(), {})
                
                if today_schedule:
                    for time_slot, details in today_schedule.items():
                        if 'subject' in details:
                            response_text += f"{time_slot}: {details['subject']} ({details['classroom']}) with {details['faculty']}\n"
                        else:
                            response_text += f"{time_slot}: {details['activity']}\n"
                else:
                    response_text = "You don't have any classes scheduled for today."
            else:
                response_text = "I couldn't find your student profile. Please contact administration."
        
        elif query_type == 'faculty_query':
            if student:
                # Load timetable data to get all faculty
                with open('chatbot/data/timetable.json', 'r') as f:
                    timetable_data = json.load(f)
                
                all_faculty = {}
                faculty_found = None
                
                for day, slots in timetable_data['Timetable'].items():
                    for slot, details in slots.items():
                        if 'faculty' in details and 'subject' in details:
                            faculty_name = details['faculty']
                            all_faculty[faculty_name] = {
                                'subject': details['subject'],
                                'email': details.get('email', 'Not available'),
                                'classroom': details.get('classroom', 'Not specified')
                            }
                            
                            # Check if this faculty is mentioned in the query
                            if faculty_name.lower() in search_query:
                                faculty_found = faculty_name
                                break
                    
                    if faculty_found:
                        break
                
                if faculty_found:
                    faculty_info = all_faculty[faculty_found]
                    
                    # Check what kind of information is being requested
                    if any(word in search_query for word in ['email', 'mail', 'contact', 'id']):
                        # Email/contact request
                        response_text = f"{faculty_found}'s email: {faculty_info['email']}"
                    
                    elif any(word in search_query for word in ['schedule', 'lecture', 'time', 'when', 'day']):
                        # Schedule request - get faculty's complete schedule
                        faculty_schedule = get_faculty_schedule(faculty_found)
                        
                        if faculty_schedule:
                            response_text = f"{faculty_found}'s schedule:\n"
                            for day, classes in faculty_schedule.items():
                                if classes:
                                    response_text += f"{day.title()}:\n"
                                    for cls in classes:
                                        response_text += f"  {cls['time_slot']}: {cls['subject']} ({cls['classroom']})\n"
                        else:
                            response_text = f"No schedule found for {faculty_found}."
                    
                    else:
                        # General faculty information
                        response_text = f"Faculty: {faculty_found}\nSubject: {faculty_info['subject']}\nEmail: {faculty_info['email']}\nUsually teaches in: {faculty_info['classroom']}"
            else:
                response_text = "I couldn't find your student profile. Please contact administration."
        
        elif query_type == 'current_lecture':
            if student:
                current_lecture = get_current_lecture(student)
                if current_lecture:
                    response_text = f"Your current lecture is {current_lecture.subject} with {current_lecture.faculty} in {current_lecture.classroom}."
                    if current_lecture.email:
                        response_text += f" Faculty email: {current_lecture.email}"
                else:
                    response_text = "You don't have any lecture right now according to your timetable."
            else:
                response_text = "I couldn't find your student profile. Please contact administration."
        
        elif query_type == 'academic_calendar':
            try:
                with open('chatbot/data/academic_calendar_2025_odd_term.json', 'r') as f:
                    calendar_data = json.load(f)
                
                # Check for specific date
                if any(word in search_query for word in ['today', 'aj', 'aaj']):
                    today = datetime.now().date().isoformat()
                    if today in calendar_data['Academic Calendar']['Daywise Schedule']:
                        events = calendar_data['Academic Calendar']['Daywise Schedule'][today]
                        response_text = f"Today's schedule: {', '.join(events)}"
                    else:
                        response_text = "No special events scheduled for today according to the academic calendar."
                
                # Check for specific event
                elif any(word in search_query for word in ['exam', 'midterm', 'end sem', 'diwali', 'vacation']):
                    if 'exam' in search_query:
                        response_text = "Exam dates:\n"
                        if 'Mid Sem Exam Start' in calendar_data['Academic Calendar']['Daywise Schedule'].values():
                            response_text += "Mid Semester Exams: July 28 - August 2, 2025\n"
                        if 'End Sem Theory Exam' in calendar_data['Academic Calendar']['Daywise Schedule'].values():
                            response_text += "End Semester Theory Exams: November 10-22, 2025\n"
                    
                    elif 'diwali' in search_query:
                        response_text = "Diwali Vacation: October 19 - November 2, 2025"
                    
                    else:
                        response_text = "Academic Calendar Highlights:\n"
                        response_text += f"Term: {calendar_data['Academic Calendar']['Term']}\n"
                        response_text += f"Teaching End: October 11, 2025\n"
                        response_text += f"Diwali Vacation: October 19 - November 2, 2025\n"
                        response_text += f"End Semester Exams: November 10-22, 2025"
                
                else:
                    response_text = f"Academic Calendar: {calendar_data['Academic Calendar']['Term']}\n"
                    response_text += f"Programs: {', '.join(calendar_data['Academic Calendar']['Programs'])}\n"
                    response_text += f"Semesters: {', '.join(calendar_data['Academic Calendar']['Semester'])}\n"
                    response_text += "Key dates available. Ask about specific events like exams or vacations."
                    
            except FileNotFoundError:
                response_text = "Academic calendar data is not available at the moment."
        
        else:
            # Check if it matches any FAQ using similarity matching
            faqs = FAQ.objects.all()
            best_match = None
            highest_similarity = 0
            
            for faq in faqs:
                similarity = calculate_similarity(search_query, faq.question.lower())
                if similarity > highest_similarity and similarity > 0.3:
                    highest_similarity = similarity
                    best_match = faq
            
            if best_match:
                response_text = best_match.answer
            else:
                response_text = "I'm sorry, I couldn't find information about that. Could you try rephrasing your question?"
        
        # Translate response if needed
        if user_language != 'en':
            response_text = translate_text(response_text, user_language)
        
        return JsonResponse({'response': response_text, 'type': response_type})
    
    return JsonResponse({'error': 'Invalid request'})





# Add this import at the top of views.py
from django.contrib.auth import logout as auth_logout

# Add this logout function
def logout_view(request):
    auth_logout(request)
    return redirect('home')






