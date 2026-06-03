import os
import json
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from current_affairs.models import DailyDigest, Topic, MCQ, MainsQuestion

def load_data():
    dump_path = '../client/dump.json'
    if not os.path.exists(dump_path):
        print(f"Error: {dump_path} not found.")
        sys.exit(1)
        
    with open(dump_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for entry in data:
        date_id = entry.get('id')
        date_text = entry.get('date')
        day = entry.get('day')
        tagline = entry.get('tagline', "नेति नेति — Less noise. More clarity.")
        announcement = entry.get('announcement', "")
        revise_summary = entry.get('reviseSummary', [])
        
        # Create DailyDigest
        digest, created = DailyDigest.objects.update_or_create(
            date_id=date_id,
            defaults={
                'date_text': date_text,
                'day': day,
                'tagline': tagline,
                'announcement': announcement,
                'revise_summary': revise_summary
            }
        )
        print(f"Created/Updated DailyDigest: {date_id}")
        
        # Create Topics
        topics_data = entry.get('topics', [])
        for topic_data in topics_data:
            Topic.objects.update_or_create(
                digest=digest,
                title=topic_data.get('title'),
                defaults={
                    'subtitle': topic_data.get('subtitle', ''),
                    'content': topic_data.get('content', ''),
                    'why_it_matters': topic_data.get('whyItMatters', ''),
                    'revise': topic_data.get('revise', ''),
                    'pyq_connect': topic_data.get('pyqConnect', '')
                }
            )
            
        # Create Questions if any
        practice_questions = entry.get('practiceQuestions')
        if practice_questions:
            mcqs = practice_questions.get('mcqs', [])
            for mcq_data in mcqs:
                MCQ.objects.update_or_create(
                    digest=digest,
                    question=mcq_data.get('question'),
                    defaults={
                        'options': mcq_data.get('options', []),
                        'answer': mcq_data.get('answer', ''),
                        'explanation': mcq_data.get('explanation', '')
                    }
                )
                
            mains_q = practice_questions.get('mains', [])
            for main_data in mains_q:
                MainsQuestion.objects.update_or_create(
                    digest=digest,
                    question=main_data.get('question'),
                    defaults={
                        'context': main_data.get('context', '')
                    }
                )
                
    print("Data loaded successfully.")

if __name__ == '__main__':
    load_data()
