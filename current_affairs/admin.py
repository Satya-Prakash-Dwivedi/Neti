from django.contrib import admin
from .models import DailyDigest, Topic, MCQ, MainsQuestion

class TopicInline(admin.StackedInline):
    model = Topic
    extra = 1  # Number of empty topic forms to show by default
    classes = ('collapse',)  # Collapses the form by default for a clean layout

class MCQInline(admin.StackedInline):
    model = MCQ
    extra = 1
    classes = ('collapse',)

class MainsQuestionInline(admin.TabularInline):
    model = MainsQuestion
    extra = 1
    classes = ('collapse',)

class DailyDigestAdmin(admin.ModelAdmin):
    list_display = ('date_id', 'date_text', 'day', 'tagline')
    ordering = ('-date_id',)  # Show newest dates first
    search_fields = ('date_text', 'tagline')
    inlines = [TopicInline, MCQInline, MainsQuestionInline]

admin.site.register(DailyDigest, DailyDigestAdmin)