from rest_framework import serializers
from .models import Quiz, QuizQuestion, QuizAttempt, Book
from authentication.serializers import UserSerializer

class BookSerializer(serializers.ModelSerializer):
    """Details of a Book."""
    class Meta:
        model = Book
        fields = ('id', 'book_name', 'subject', 'class_name', 'cover_image', 'source_image', 'full_price', 'is_active', 'created_at')

class QuizQuestionStudentSerializer(serializers.ModelSerializer):
    """Serializer for students taking the test. Excludes correct answer and explanation to prevent cheating."""
    class Meta:
        model = QuizQuestion
        fields = ('id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'difficulty')


class QuizQuestionAdminSerializer(serializers.ModelSerializer):
    """Full question details for Admin and after-test solutions view."""
    class Meta:
        model = QuizQuestion
        fields = ('id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'difficulty', 'solution')


class QuizSerializer(serializers.ModelSerializer):
    """Details of a Quiz without answers for student consumption."""
    questions = QuizQuestionStudentSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    book = BookSerializer(read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'title', 'book', 'is_live', 'is_free_test', 'is_current_affairs', 'created_at', 'questions', 'question_count')

    def get_question_count(self, obj):
        return obj.questions.count()


class QuizAdminSerializer(serializers.ModelSerializer):
    """Full details of a Quiz for Admin review."""
    questions = QuizQuestionAdminSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    book = BookSerializer(read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'title', 'book', 'is_live', 'is_free_test', 'is_current_affairs', 'created_at', 'questions', 'question_count')

    def get_question_count(self, obj):
        return obj.questions.count()


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Details of a completed attempt."""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    is_current_affairs = serializers.BooleanField(source='quiz.is_current_affairs', read_only=True)
    student = UserSerializer(read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ('id', 'student', 'quiz', 'quiz_title', 'is_current_affairs', 'score', 'total_questions', 'correct_answers', 'completed_at', 'answers_data')
