from django.db import models
from django.conf import settings

class DailyDigest(models.Model):
    """Parent model representing a day's current affairs digest."""
    date_id = models.DateField(unique=True, primary_key=True)  # e.g., "2026-04-01" (used as URL param)
    date_text = models.CharField(max_length=100)  # e.g., "1st April 2026"
    day = models.CharField(max_length=50)  # e.g., "Tuesday"
    tagline = models.CharField(max_length=255, default="नेति नेति — Less noise. More clarity.")
    announcement = models.TextField(blank=True, null=True)  # Optional top-level announcements
    revise_summary = models.JSONField(default=list, blank=True)  # Simple list of strings
    pdf_file = models.FileField(upload_to='current_affairs_pdfs/', blank=True, null=True)  # Optional PDF link
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Daily Digest"
        verbose_name_plural = "Daily Digests"

    def __str__(self):
        return f"{self.date_text} ({self.day})"


class Topic(models.Model):
    """An analysis topic associated with a daily digest."""
    digest = models.ForeignKey(DailyDigest, related_name='topics', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)  # e.g. "Polity | GS-II"
    content = models.TextField()  # Supports markdown formatting
    why_it_matters = models.TextField(blank=True)
    revise = models.TextField(blank=True)
    pyq_connect = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.digest.date_text} - Topic: {self.title}"


class MCQ(models.Model):
    """A Multiple Choice Question for Prelims practice."""
    digest = models.ForeignKey(DailyDigest, related_name='mcqs', on_delete=models.CASCADE)
    question = models.TextField()
    options = models.JSONField(default=list)  # List of strings, e.g. ["A. Option 1", "B. Option 2", ...]
    answer = models.CharField(max_length=500)  # e.g. "A", "B", "C", "D"
    explanation = models.TextField()

    def __str__(self):
        return f"MCQ ({self.digest.date_text}): {self.question[:40]}..."


class MainsQuestion(models.Model):
    """A Mains answer-writing practice prompt."""
    digest = models.ForeignKey(DailyDigest, related_name='mains_questions', on_delete=models.CASCADE)
    question = models.TextField()
    context = models.TextField()  # e.g. "GS-III (Internal Security)"

    def __str__(self):
        return f"Mains ({self.digest.date_text}): {self.question[:40]}..."

class DailyQuizAttempt(models.Model):
    """Records a student's performance on a daily current affairs quiz."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='daily_ca_attempts', on_delete=models.CASCADE)
    digest = models.ForeignKey(DailyDigest, related_name='quiz_attempts', on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    answers_data = models.JSONField(default=dict, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Daily Quiz Attempt"
        verbose_name_plural = "Daily Quiz Attempts"
        unique_together = ('user', 'digest')

    def __str__(self):
        return f"{self.user.email} - {self.digest.date_text} - Score: {self.score}/{self.total_questions}"