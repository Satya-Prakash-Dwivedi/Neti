from django.contrib import admin
from .models import Quiz, QuizQuestion, QuizAttempt

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_live', 'created_at')
    list_filter = ('is_live', 'created_at')
    search_fields = ('title',)

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_text', 'correct_option', 'difficulty')
    list_filter = ('quiz', 'correct_option', 'difficulty')
    search_fields = ('question_text', 'solution')

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'total_questions', 'completed_at')
    list_filter = ('quiz', 'completed_at')
    search_fields = ('student__email', 'quiz__title')
