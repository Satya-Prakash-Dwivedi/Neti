from django.db import models
from django.conf import settings

class Book(models.Model):
    """Represents a specific purchasable Book (e.g., NCERT History Class 6)."""
    book_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=100)
    class_name = models.CharField(max_length=100, blank=True, null=True)
    cover_image = models.FileField(upload_to='book_covers/', blank=True, null=True)
    full_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        class_str = f" - {self.class_name}" if self.class_name else ""
        return f"{self.book_name} - {self.subject}{class_str}"


class Quiz(models.Model):
    """Represents a Chapter belonging to a Book."""
    title = models.CharField(max_length=255)
    book = models.ForeignKey(Book, related_name='chapters', on_delete=models.CASCADE, null=True, blank=True)
    is_live = models.BooleanField(default=False)
    is_free_test = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    """An individual question in a Quiz."""
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=10)  # e.g., "A", "B", "C", "D"
    difficulty = models.CharField(max_length=50, blank=True, default="Medium")
    solution = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.quiz.title} - Question: {self.question_text[:55]}..."


class QuizAttempt(models.Model):
    """Records a student's performance on a quiz."""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='quiz_attempts', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name='attempts', on_delete=models.CASCADE)
    score = models.IntegerField()  # +1 for correct, 0 for wrong
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    answers_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.student.email} - {self.quiz.title} - Score: {self.score}/{self.total_questions}"
