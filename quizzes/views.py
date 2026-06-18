import csv
import io
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Quiz, QuizQuestion, QuizAttempt, Book
from .serializers import (
    QuizSerializer, QuizAdminSerializer, 
    QuizQuestionAdminSerializer, QuizAttemptSerializer,
    BookSerializer
)

class CSVParsePreviewView(APIView):
    """API endpoint for admins to upload and preview CSV tests."""
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        csv_file = request.FILES['file']
        
        try:
            # Read and decode binary stream
            decoded_file = csv_file.read().decode('utf-8-sig')
            
            # Simple cleanup for surrounding triple quotes or excessive quoting from formatting tools
            lines = []
            for line in decoded_file.splitlines():
                cleaned_line = line.strip()
                if cleaned_line.startswith('"""') and cleaned_line.endswith('"""'):
                    cleaned_line = cleaned_line[2:-2]
                elif cleaned_line.startswith('""') and cleaned_line.endswith('""'):
                    cleaned_line = cleaned_line[1:-1]
                cleaned_line = cleaned_line.replace('""', '"')
                lines.append(cleaned_line)
            decoded_file = '\n'.join(lines)
            
            io_string = io.StringIO(decoded_file)
            
            # Use csv.reader
            reader = csv.reader(io_string, quotechar='"', skipinitialspace=True)
            
            headers = next(reader)
            # Clean headers (strip spaces and quotes)
            headers = [h.replace('"', '').strip().lower() for h in headers]
            
            required_fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
            for field in required_fields:
                if field not in headers:
                    return Response({
                        'error': f"Invalid CSV headers. Missing required column '{field}'. Found headers: {headers}"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            questions = []
            for row in reader:
                if not row:
                    continue
                # Map row indices to clean header indices
                row_data = {}
                for idx, header in enumerate(headers):
                    if idx < len(row):
                        # Strip outer quotes and spaces
                        val = row[idx].strip()
                        # If value starts and ends with double quotes, remove them
                        if val.startswith('"') and val.endswith('"'):
                            val = val[1:-1]
                        row_data[header] = val
                
                questions.append({
                    'question_text': row_data.get('question', ''),
                    'option_a': row_data.get('option_a', ''),
                    'option_b': row_data.get('option_b', ''),
                    'option_c': row_data.get('option_c', ''),
                    'option_d': row_data.get('option_d', ''),
                    'correct_option': row_data.get('correct_option', 'A').upper(),
                    'difficulty': row_data.get('difficulty', 'Medium'),
                    'solution': row_data.get('solution', '')
                })
            
            return Response({
                'title': csv_file.name.replace('.csv', '').replace('_', ' ').title(),
                'questions': questions
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': f"Failed to parse CSV file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class QuizCreateView(APIView):
    """API endpoint for admins to finalize and publish the quiz from preview edits."""
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        book_id = request.data.get('book_id')
        questions_data = request.data.get('questions', [])
        
        if not title:
            return Response({'error': 'Title is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not book_id:
            return Response({'error': 'Book selection is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not questions_data:
            return Response({'error': 'Questions list cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        book = get_object_or_404(Book, id=book_id)
        
        try:
            with transaction.atomic():
                # Create the quiz set
                quiz = Quiz.objects.create(
                    title=title,
                    book=book,
                    is_live=True
                )
                
                # Bulk create questions
                for q_data in questions_data:
                    QuizQuestion.objects.create(
                        quiz=quiz,
                        question_text=q_data.get('question_text', ''),
                        option_a=q_data.get('option_a', ''),
                        option_b=q_data.get('option_b', ''),
                        option_c=q_data.get('option_c', ''),
                        option_d=q_data.get('option_d', ''),
                        correct_option=q_data.get('correct_option', 'A').upper(),
                        difficulty=q_data.get('difficulty', 'Medium'),
                        solution=q_data.get('solution', '')
                    )
            
            return Response({
                'message': 'Quiz created successfully',
                'quiz_id': quiz.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': f"Failed to create quiz: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class QuizUpdateView(APIView):
    """API endpoint for admins to update a published quiz and its questions."""
    permission_classes = (permissions.IsAdminUser,)

    def put(self, request, quiz_id, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        title = request.data.get('title')
        book_id = request.data.get('book_id')
        questions_data = request.data.get('questions', [])
        
        if not title:
            return Response({'error': 'Title is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not book_id:
            return Response({'error': 'Book selection is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not questions_data:
            return Response({'error': 'Questions list cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
            
        book = get_object_or_404(Book, id=book_id)
        
        try:
            with transaction.atomic():
                # Update quiz
                quiz.title = title
                quiz.book = book
                quiz.save()
                
                # Identify questions to keep vs delete vs create
                existing_question_ids = []
                for q_data in questions_data:
                    q_id = q_data.get('id')
                    if q_id:
                        # Update existing question
                        q_obj = get_object_or_404(QuizQuestion, id=q_id, quiz=quiz)
                        q_obj.question_text = q_data.get('question_text', '')
                        q_obj.option_a = q_data.get('option_a', '')
                        q_obj.option_b = q_data.get('option_b', '')
                        q_obj.option_c = q_data.get('option_c', '')
                        q_obj.option_d = q_data.get('option_d', '')
                        q_obj.correct_option = q_data.get('correct_option', 'A').upper()
                        q_obj.difficulty = q_data.get('difficulty', 'Medium')
                        q_obj.solution = q_data.get('solution', '')
                        q_obj.save()
                        existing_question_ids.append(q_id)
                    else:
                        # Create new question
                        new_q = QuizQuestion.objects.create(
                            quiz=quiz,
                            question_text=q_data.get('question_text', ''),
                            option_a=q_data.get('option_a', ''),
                            option_b=q_data.get('option_b', ''),
                            option_c=q_data.get('option_c', ''),
                            option_d=q_data.get('option_d', ''),
                            correct_option=q_data.get('correct_option', 'A').upper(),
                            difficulty=q_data.get('difficulty', 'Medium'),
                            solution=q_data.get('solution', '')
                        )
                        existing_question_ids.append(new_q.id)
                
                # Delete any questions that were removed
                QuizQuestion.objects.filter(quiz=quiz).exclude(id__in=existing_question_ids).delete()
                
            return Response({'message': 'Quiz updated successfully'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': f"Failed to update quiz: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class QuizDeleteView(APIView):
    """API endpoint for admins to delete a quiz."""
    permission_classes = (permissions.IsAdminUser,)

    def delete(self, request, quiz_id, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        quiz.delete()
        return Response({'message': 'Quiz deleted successfully'}, status=status.HTTP_200_OK)


class AdminQuizListView(generics.ListAPIView):
    """API endpoint for admins to see all quizzes with full detail."""
    permission_classes = (permissions.IsAdminUser,)
    queryset = Quiz.objects.all().order_by('-created_at')
    serializer_class = QuizAdminSerializer


class StudentQuizListView(generics.ListAPIView):
    """API endpoint for students to see active tests."""
    permission_classes = (permissions.AllowAny,)
    queryset = Quiz.objects.filter(is_live=True).order_by('created_at')
    serializer_class = QuizSerializer


class QuizDetailView(generics.RetrieveAPIView):
    """API endpoint to get a single quiz and its questions for students."""
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Quiz.objects.filter(is_live=True)
    serializer_class = QuizSerializer


class QuizSubmitView(APIView):
    """API endpoint to grade a student's quiz attempt."""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, quiz_id, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=quiz_id, is_live=True)
        answers = request.data.get('answers', {}) # Dict mapping question_id (str) to selected_option (str: "A","B","C","D")
        
        questions = quiz.questions.all()
        total_questions = questions.count()
        correct_answers = 0
        
        # Build feedback list containing solutions
        results_feedback = []
        
        for question in questions:
            q_id_str = str(question.id)
            student_choice = answers.get(q_id_str, "").strip().upper()
            correct_choice = question.correct_option.strip().upper()
            
            is_correct = (student_choice == correct_choice)
            if is_correct:
                correct_answers += 1
                
            results_feedback.append({
                'id': question.id,
                'question_text': question.question_text,
                'student_choice': student_choice,
                'correct_option': correct_choice,
                'is_correct': is_correct,
                'solution': question.solution
            })
            
        # Score computation: +1 for correct, 0 for wrong (as requested: no negative marking)
        score = correct_answers
        
        # Save the attempt
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers,
            answers_data=answers
        )
        
        return Response({
            'attempt_id': attempt.id,
            'score': score,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'feedback': results_feedback
        }, status=status.HTTP_200_OK)


class StudentAttemptHistoryView(generics.ListAPIView):
    """API endpoint to fetch the authenticated student's past attempt scores."""
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuizAttemptSerializer

    def get_queryset(self):
        return QuizAttempt.objects.filter(student=self.request.user).order_by('-completed_at')


class AdminQuizAttemptsView(generics.ListAPIView):
    """API endpoint for admins to fetch all student attempts for a specific quiz."""
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = QuizAttemptSerializer

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_id')
        return QuizAttempt.objects.filter(quiz_id=quiz_id).order_by('-completed_at')


class AdminQuizDetailView(generics.RetrieveAPIView):
    """API endpoint for admins to get full details of a single quiz."""
    permission_classes = (permissions.IsAdminUser,)
    queryset = Quiz.objects.all()
    serializer_class = QuizAdminSerializer


class AdminQuizToggleFreeView(APIView):
    """API endpoint for admins to toggle a quiz as the free test for its book."""
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request, quiz_id, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        is_free = request.data.get('is_free_test', True)

        try:
            with transaction.atomic():
                if is_free and quiz.book:
                    # Mark all other quizzes in the same book as not free
                    Quiz.objects.filter(book=quiz.book).exclude(id=quiz.id).update(is_free_test=False)
                
                quiz.is_free_test = is_free
                quiz.save()
            
            return Response({'message': 'Quiz free test status updated successfully.', 'is_free_test': quiz.is_free_test}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"Failed to update status: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# --- Book Views ---

class AdminBookListCreateView(generics.ListCreateAPIView):
    """Admin API for creating and listing Books."""
    permission_classes = (permissions.IsAdminUser,)
    queryset = Book.objects.all().order_by('-created_at')
    serializer_class = BookSerializer

class AdminBookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin API for editing a Book."""
    permission_classes = (permissions.IsAdminUser,)
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class CategoryListView(APIView):
    """Returns unique book categories (e.g. NCERT, Spectrum) with a representative cover."""
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, *args, **kwargs):
        data = []
        seen = set()
        for b in Book.objects.filter(is_active=True):
            if b.book_name not in seen:
                seen.add(b.book_name)
                data.append({
                    'book_name': b.book_name,
                    'cover_image': request.build_absolute_uri(b.cover_image.url) if b.cover_image else None
                })
        return Response(data, status=status.HTTP_200_OK)

class SubjectListView(APIView):
    """Returns unique subjects for a specific book category."""
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, book_name, *args, **kwargs):
        subjects = Book.objects.filter(is_active=True, book_name=book_name).values_list('subject', flat=True).distinct()
        return Response(list(subjects), status=status.HTTP_200_OK)

class ClassListView(generics.ListAPIView):
    """Returns actual Book instances (Classes) for a given book category and subject."""
    permission_classes = (permissions.AllowAny,)
    serializer_class = BookSerializer

    def get_queryset(self):
        book_name = self.kwargs.get('book_name')
        subject = self.kwargs.get('subject')
        return Book.objects.filter(is_active=True, book_name=book_name, subject=subject).order_by('class_name')

class BookDetailView(generics.RetrieveAPIView):
    """Gets details of a book, frontend will fetch quizzes (chapters) separately."""
    permission_classes = (permissions.AllowAny,)
    queryset = Book.objects.filter(is_active=True)
    serializer_class = BookSerializer
