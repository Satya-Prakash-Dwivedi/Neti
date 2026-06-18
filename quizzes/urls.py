from django.urls import path
from .views import (
    CSVParsePreviewView, QuizCreateView, QuizDeleteView,
    AdminQuizListView, StudentQuizListView, QuizDetailView, 
    QuizSubmitView, StudentAttemptHistoryView, AdminQuizAttemptsView,
    AdminQuizDetailView, AdminQuizToggleFreeView, AdminBookListCreateView, AdminBookDetailView,
    CategoryListView, SubjectListView, ClassListView, BookDetailView, QuizUpdateView
)

urlpatterns = [
    # Admin endpoints
    path('admin/upload/', CSVParsePreviewView.as_view(), name='quiz_csv_upload'),
    path('admin/create/', QuizCreateView.as_view(), name='quiz_create'),
    path('admin/update/<int:quiz_id>/', QuizUpdateView.as_view(), name='quiz_admin_update'),
    path('admin/list/', AdminQuizListView.as_view(), name='quiz_admin_list'),
    path('admin/delete/<int:quiz_id>/', QuizDeleteView.as_view(), name='quiz_admin_delete'),
    path('admin/toggle-free/<int:quiz_id>/', AdminQuizToggleFreeView.as_view(), name='quiz_admin_toggle_free'),
    path('admin/attempts/<int:quiz_id>/', AdminQuizAttemptsView.as_view(), name='quiz_admin_attempts'),
    path('admin/detail/<int:pk>/', AdminQuizDetailView.as_view(), name='quiz_admin_detail'),
    path('admin/books/', AdminBookListCreateView.as_view(), name='admin_books_list'),
    path('admin/books/<int:pk>/', AdminBookDetailView.as_view(), name='admin_books_detail'),
    
    # Student endpoints
    path('student/list/', StudentQuizListView.as_view(), name='quiz_student_list'),
    path('student/attempts/', StudentAttemptHistoryView.as_view(), name='quiz_student_attempts'),
    path('categories/', CategoryListView.as_view(), name='categories_list'),
    path('categories/<str:book_name>/subjects/', SubjectListView.as_view(), name='subjects_list'),
    path('categories/<str:book_name>/<str:subject>/classes/', ClassListView.as_view(), name='classes_list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='books_detail'),
    path('<int:pk>/', QuizDetailView.as_view(), name='quiz_detail'),
    path('<int:quiz_id>/submit/', QuizSubmitView.as_view(), name='quiz_submit'),
]
