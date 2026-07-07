from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DailyDigest, MCQ, DailyQuizAttempt
from .serializers import DailyDigestSerializer, DailyDigestAdminSerializer, DailyQuizQuestionSerializer

class DailyDigestViewSet(viewsets.ModelViewSet):
    queryset = DailyDigest.objects.all().order_by('-date_id')
    lookup_field = 'date_id'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DailyDigestAdminSerializer
        return DailyDigestSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class DailyQuizQuestionsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'Date parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            digest = DailyDigest.objects.get(date_id=date_str)
        except DailyDigest.DoesNotExist:
            return Response({'error': 'No digest found for this date.'}, status=status.HTTP_404_NOT_FOUND)
        
        mcqs = digest.mcqs.all()
        serializer = DailyQuizQuestionSerializer(mcqs, many=True)
        return Response(serializer.data)

class DailyQuizSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        date_str = request.data.get('date')
        answers = request.data.get('answers', [])
        
        if not date_str:
            return Response({'error': 'Date is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            digest = DailyDigest.objects.get(date_id=date_str)
        except DailyDigest.DoesNotExist:
            return Response({'error': 'No digest found for this date.'}, status=status.HTTP_404_NOT_FOUND)
            
        # Optional: check if attempt already exists
        if DailyQuizAttempt.objects.filter(user=request.user, digest=digest).exists():
            pass # We could return error, or just allow overwrite. Let's allow overwrite for now by deleting old one, or just update.
            # Actually unique_together might throw error. Let's delete old one.
            DailyQuizAttempt.objects.filter(user=request.user, digest=digest).delete()
            
        mcqs = {str(mcq.id): mcq for mcq in digest.mcqs.all()}
        
        total_questions = len(mcqs)
        score = 0
        results = []
        
        for ans in answers:
            q_id = str(ans.get('questionId'))
            selected = ans.get('selectedOption')
            
            if q_id in mcqs:
                mcq = mcqs[q_id]
                is_correct = (mcq.answer == selected)
                if is_correct:
                    score += 1
                    
                results.append({
                    'questionId': q_id,
                    'selectedOption': selected,
                    'correctOption': mcq.answer,
                    'isCorrect': is_correct,
                    'crispSolution': mcq.explanation
                })
        
        # Save Attempt
        attempt = DailyQuizAttempt.objects.create(
            user=request.user,
            digest=digest,
            score=score,
            total_questions=total_questions,
            answers_data={'answers': answers}
        )
        
        return Response({
            'score': score,
            'total': total_questions,
            'results': results
        })