# chatbot/utils.py

# Enhanced translation and language detection
from googletrans import Translator
from langdetect import detect, DetectorFactory
import logging
import re  # Add this import
# Set seed for consistent language detection
DetectorFactory.seed = 0

# Initialize translator
translator = Translator()

# Simple translation dictionary for demo purposes
# In a real application, you would use a proper translation API or librarya

# chatbot/utils.py (update translation_dict)
translation_dict = {
    # English to Hindi translations
    'en': {
        'hi': {
            'Hello! How can I help you today?': 'नमस्ते! मैं आपकी आज कैसे मदद कर सकता हूँ?',
            'Here are some documents that might be relevant': 'यहाँ कुछ दस्तावेज़ हैं जो प्रासंगिक हो सकते हैं',
            'Your overall attendance is': 'आपकी कुल उपस्थिति है',
            "Today's schedule": 'आज का कार्यक्रम',
            'Sorry, I did not understand that': 'क्षमा करें, मैं समझ नहीं पाया',
            'Math': 'गणित',
            'Physics': 'भौतिक विज्ञान',
            'Chemistry': 'रसायन विज्ञान',
            'Computer Science': 'कंप्यूटर विज्ञान',
            'Your current lecture is': 'आपकी वर्तमान कक्षा है',
            'with': 'के साथ',
            'in': 'में',
            'Faculty email:': 'शिक्षक ईमेल:',
            'You don\'t have any lecture right now according to your timetable.': 'आपके समय सारणी के अनुसार आपकी अभी कोई कक्षा नहीं है।',
            'Your timetable for': 'आपकी समय सारणी',
            'You don\'t have any classes scheduled for today.': 'आज के लिए आपकी कोई कक्षाएं निर्धारित नहीं हैं।',
            'Your attendance in': 'में आपकी उपस्थिति',
            'classes': 'कक्षाएं',
            'Your attendance:': 'आपकी उपस्थिति:',
            'No attendance records found for you.': 'आपके लिए कोई उपस्थिति रिकॉर्ड नहीं मिला।',
            'Faculty:': 'शिक्षक:',
            'Subject:': 'विषय:',
            'Email:': 'ईमेल:',
            'Usually teaches in:': 'आमतौर पर पढ़ाते हैं:',
            'For': 'के लिए',
            'Today\'s schedule:': 'आज का कार्यक्रम:',
            'No special events scheduled for today according to the academic calendar.': 'शैक्षणिक कैलेंडर के अनुसार आज के लिए कोई विशेष कार्यक्रम निर्धारित नहीं है।',
            'Exam dates:': 'परीक्षा की तारीखें:',
            'Mid Semester Exams:': 'मध्य सेमेस्टर परीक्षाएं:',
            'End Semester Theory Exams:': 'अंत सेमेस्टर सिद्धांत परीक्षाएं:',
            'Diwali Vacation:': 'दिवाली अवकाश:',
            'Academic Calendar Highlights:': 'शैक्षणिक कैलेंडर के मुख्य बिंदु:',
            'Term:': 'सत्र:',
            'Teaching End:': 'शिक्षण समाप्ति:',
            'Programs:': 'कार्यक्रम:',
            'Semesters:': 'सेमेस्टर:',
            'Key dates available. Ask about specific events like exams or vacations.': 'मुख्य तिथियां उपलब्ध हैं। परीक्षा या अवकाश जैसे विशेष कार्यक्रमों के बारे में पूछें।',
            'Academic calendar data is not available at the moment.': 'शैक्षणिक कैलेंडर डेटा इस समय उपलब्ध नहीं है。',
            
            # Common academic queries in Hindi
            'send': 'भेजो',
            'me': 'मुझे',
            'i need': 'मुझे चाहिए',
            'give me': 'मुझे दो',
            'provide': 'उपलब्ध कराओ',
            'want': 'चाहिए',
            
            # Document types
            'presentation': 'प्रस्तुति',
            'slide': 'स्लाइड',
            'lecture': 'व्याख्यान',
            'material': 'सामग्री',
            'book': 'किताब',
            
            # Common verbs
            'download': 'डाउनलोड',
            'see': 'देखो',
            'show': 'दिखाओ',
            'find': 'खोजो',
            'search': 'खोजो',
            
            # Common academic subjects (abbreviations)
            'se': 'सॉफ्टवेयर इंजीनियरिंग',
            'daa': 'एल्गोरिदम का डिजाइन और विश्लेषण',
            'dvd': 'डेटा विज़ुअलाइज़ेशन और डेटा एनालिटिक्स',
            'ep': 'एंटरप्राइज प्रोग्रामिंग',
            'toc': 'कम्प्यूटेशन का सिद्धांत',
            'aws': 'AWS फंडामेंटल्स',
            'pce': 'पेशेवरता और कॉर्पोरेट नैतिकता',
            
            # Common phrases
            'of': 'का',
            'for': 'के लिए',
            'the': '',
            'please': 'कृपया',
            'thank you': 'धन्यवाद',
        },
        'gu': {
            'Hello! How can I help you today?': 'નમસ્તે! હું તમને આજે કેવી રીતે મદદ કરી શકું?',
            'Here are some documents that might be relevant': 'અહીં કેટલાક દસ્તાવેજો છે જે સંબંધિત હોઈ શકે છે',
            'Your overall attendance is': 'તમારી એકંદર હાજરી છે',
            "Today's schedule": 'આજનું શેડ્યૂલ',
            'Sorry, I did not understand that': 'માફ કરશો, હું તે સમજી શક્યો નથી',
            'Math': 'ગણિત',
            'Physics': 'ભૌતિક વિજ્ઞાન',
            'Chemistry': 'રસાયણ શાસ્ત્ર',
            'Computer Science': 'કમ્પ્યુટર વિજ્ઞાન',
            'Your current lecture is': 'તમારું વર્તમાન લેક્ચર છે',
            'with': 'સાથે',
            'in': 'માં',
            'Faculty email:': 'ફેકલ્ટી ઇમેઇલ:',
            'You don\'t have any lecture right now according to your timetable.': 'તમારા ટાઇમટેબલ મુજબ તમારું હમણાં કોઈ લેક્ચર નથી.',
            'Your timetable for': 'માટે તમારું ટાઇમટેબલ',
            'You don\'t have any classes scheduled for today.': 'આજે માટે તમારી કોઈ ક્લાસ સ્કેડ્યુલ નથી.',
            'Your attendance in': 'માં તમારી હાજરી',
            'classes': 'વર્ગો',
            'Your attendance:': 'તમારી હાજરી:',
            'No attendance records found for you.': 'તમારા માટે કોઈ હાજરી રેકોર્ડ્સ મળ્યા નથી.',
            'Faculty:': 'ફેકલ્ટી:',
            'Subject:': 'વિષય:',
            'Email:': 'ઇમેઇલ:',
            'Usually teaches in:': 'સામાન્ય રીતે આમાં શિક્ષણ આપે છે:',
            'For': 'માટે',
            'Today\'s schedule:': 'આજનું શેડ्यૂલ:',
            'No special events scheduled for today according to the academic calendar.': 'એકેડેમિક કેલેન્ડર મુજબ આજે માટે કોઈ ખાસ ઇવેન્ટ્સ સ્કેડ્યુલ નથી.',
            'Exam dates:': 'પરીક્ષાની તારીખો:',
            'Mid Semester Exams:': 'મિડ સेમેસ्टર પરીક્ષાઓ:',
            'End Semester Theory Exams:': 'अંત સેमેસ્ટર સિદ્ધાંત પરીક્ષાઓ:',
            'Diwali Vacation:': 'દિવાળી વેકેશન:',
            'Academic Calendar Highlights:': 'એકેડેमિક કેલેન્ડર હાઇલાઇટ્સ:',
            'Term:': 'ટર્મ:',
            'Teaching End:': 'શિક્ષણ સમાપ્તિ:',
            'Programs:': 'પ્રોગ્રામ્સ:',
            'Semesters:': 'સेमેસ્ટર્સ:',
            'Key dates available. Ask about specific events like exams or vacations.': 'મુખ્ય તારીખો ઉપલબ્ધ છે. પરીક્ષા અથવા વેકેશન જેવી ચોક્કસ ઘટનાઓ વિશે પૂછો.',
            'Academic calendar data is not available at the moment.': 'એકેડેમિક કેલेન્ડર ડેટા હાલમાં ઉપલબ્ધ નથી.',
            
            # Common academic queries in Gujarati
            'send': 'મોકલો',
            'me': 'મને',
            'i need': 'મને જોઈએ છે',
            'give me': 'મને આપો',
            'provide': 'પૂરું પાડો',
            'want': 'જોઈએ',
            
            # Document types
            'presentation': 'પ્રેઝન્ટેશન',
            'slide': 'સ્લાઇડ',
            'lecture': 'લેક્ચર',
            'material': 'સામગ્રી',
            'book': 'પુસ્તક',
            
            # Common verbs
            'download': 'ડાઉનલોડ',
            'see': 'જુઓ',
            'show': 'બતાવો',
            'find': 'શોધો',
            'search': 'શોધો',
            
            # Common academic subjects (abbreviations)
            'se': 'સોફ્ટવેર એન્જિનિયરિંગ',
            'daa': 'અલ્ગોરિધમની ડિઝાઇન અને વિશ્લેષણ',
            'dvd': 'ડેટા વિઝ્યુલાઇઝેશન અને ડેટા એનાલિટિક્સ',
            'ep': 'એન્ટરપ્રાઇઝ પ્રોગ્રામિંગ',
            'toc': 'કમ્પ્યુટેશનનો સિદ્ધાંત',
            'aws': 'AWS ફંડામેن્ટલ્સ',
            'pce': 'પ્રોફેશનલિઝમ અને કોર્પોરેટ એથિક્સ',
            
            # Common phrases
            'of': 'નું',
            'for': 'માટે',
            'the': '',
            'please': 'કૃપા કરીને',
            'thank you': 'આભાર',
        }
    }
}

def detect_language(text):
    """
    Improved language detection that handles mixed language text
    """
    if not text or not isinstance(text, str):
        return 'en'
    
    try:
        # First try langdetect
        lang_code = detect(text)
        
        # Validate if it's one of our supported languages
        if lang_code in ['en', 'hi', 'gu']:
            return lang_code
            
        # Fallback to character-based detection
        hindi_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
        gujarati_chars = sum(1 for char in text if '\u0A80' <= char <= '\u0AFF')
        
        if hindi_chars > 1:
            return 'hi'
        elif gujarati_chars > 1:
            return 'gu'
        else:
            return 'en'
            
    except Exception as e:
        # Fallback to character-based detection
        hindi_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
        gujarati_chars = sum(1 for char in text if '\u0A80' <= char <= '\u0AFF')
        
        if hindi_chars > 1:
            return 'hi'
        elif gujarati_chars > 1:
            return 'gu'
        else:
            return 'en'

def translate_text(text, dest_language='en'):
    """
    Improved translation using Google Translate API with fallback
    """
    if dest_language == 'en' or not text:
        return text
    
    try:
        # Use googletrans for better translation
        translation = translator.translate(text, dest=dest_language)
        return translation.text
    except Exception as e:
        # Fallback to dictionary-based translation
        print(f"Translation API error: {e}, falling back to dictionary")
        return translate_text_fallback(text, dest_language)

def translate_text_fallback(text, dest_language='en'):
    """
    Fallback translation using dictionary
    """
    if dest_language == 'en':
        return text
    
    try:
        # Try to translate the whole text
        if text in translation_dict['en'][dest_language]:
            return translation_dict['en'][dest_language][text]
        
        # If not found, try to translate individual words
        words = text.split()
        translated_words = []
        for word in words:
            if word in translation_dict['en'][dest_language]:
                translated_words.append(translation_dict['en'][dest_language][word])
            else:
                translated_words.append(word)
        
        return ' '.join(translated_words)
    except:
        return text  # Return original text if translation fails
    

# Add these imports at the top of utils.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Add these functions at the end of utils.py

def calculate_similarity(text1, text2):
    """
    Calculate similarity between two texts using TF-IDF
    """
    try:
        vectorizer = TfidfVectorizer().fit_transform([text1, text2])
        vectors = vectorizer.toarray()
        return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    except Exception as e:
        print(f"Similarity calculation error: {e}")
        return 0

def enhanced_document_search(query, documents):
    """
    Use TF-IDF and cosine similarity for better document matching
    """
    # Prepare document texts for similarity comparison
    doc_texts = []
    for doc in documents:
        # Use extracted text if available, otherwise use metadata
        if hasattr(doc, 'extracted_text') and doc.extracted_text:
            doc_text = f"{doc.title} {doc.subject} {doc.extracted_text}"
        else:
            doc_text = f"{doc.title} {doc.subject} {doc.description} {doc.doc_type}"
        
        if doc.unit:
            doc_text += f" unit {doc.unit}"
        doc_texts.append(doc_text)
    
    # Add the query to the corpus
    all_texts = doc_texts + [query]
    
    try:
        # Create TF-IDF matrix
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Calculate cosine similarity between query and documents
        cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
        
        # Get indices of documents sorted by similarity
        similar_indices = cosine_similarities.argsort()[0][-5:][::-1]  # Top 5 matches
        
        # Return the most relevant documents
        relevant_docs = []
        for i in similar_indices:
            if cosine_similarities[0][i] > 0.1:
                relevant_docs.append(documents[i])
        
        return relevant_docs
    except Exception as e:
        print(f"Document search error: {e}")
        return []

def understand_query(query):
    """
    Enhanced query understanding with NLP
    """
    query = query.lower()
    
    # Define patterns for different types of queries
    patterns = {
        'document_request': [
            r'(send|give|provide|get|need|want|chahiye|joiye).*(ppt|notes|pdf|document|file|syllabus|assignment)',
            r'(ppt|notes|pdf|document|file|syllabus|assignment).*(send|give|provide|get|need|want|chahiye|joiye)',
            r'(unit|chapter).*\d+',
        ],
        'attendance_query': [
            r'attendance|haziri|upasthiti|kitna|percentage|%',
            r'how many.*class|kitni.*class',
        ],
        'timetable_query': [
            r'(timetable|schedule|time table|samay|vartaman)',
            r'(current|now|abhi|aj).*(class|lecture|period)',
        ],
        'faculty_query': [
            r'(faculty|teacher|professor|sir|maam|madam)',
            r'(email|contact|phone|number)',
            r'(schedule|timing|office hours)',
        ],
        'current_lecture': [
            r'(current|now|abhi).*(lecture|class|period)',
            r'which.*(lecture|class).*now',
        ],
        'academic_calendar': [
            r'(calendar|academic calendar|holiday|vacation|exam)',
        ]
    }
    
    # Check which pattern matches
    for query_type, pattern_list in patterns.items():
        for pattern in pattern_list:
            try:
                if re.search(pattern, query, re.IGNORECASE):
                    return query_type
            except:
                continue
                
    return 'general'