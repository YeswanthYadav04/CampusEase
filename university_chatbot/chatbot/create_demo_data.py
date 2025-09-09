# chatbot/create_demo_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_chatbot.settings')
django.setup()

from chatbot.models import FAQ

# Create some demo FAQs
faqs = [
    {
        'question': 'When is the exam form deadline?',
        'answer': 'The exam form deadline is November 15th, 2023.',
        'category': 'examination'
    },
    {
        'question': 'How do I apply for scholarships?',
        'answer': 'Scholarship applications can be submitted through the student portal between September 1st and October 15th.',
        'category': 'scholarship'
    },
    {
        'question': 'What are the hostel fees?',
        'answer': 'Hostel fees are ₹25,000 per semester which includes accommodation and meals.',
        'category': 'hostel'
    },
]

for faq_data in faqs:
    faq = FAQ.objects.create(
        question=faq_data['question'],
        answer=faq_data['answer'],
        category=faq_data['category']
    )
    print(f"Created FAQ: {faq.question}")

print("Demo data created successfully!")