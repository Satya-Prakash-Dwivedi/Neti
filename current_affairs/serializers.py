from rest_framework import serializers
from django.db import transaction
from .models import DailyDigest, Topic, MCQ, MainsQuestion, DailyQuizAttempt

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'title', 'subtitle', 'content', 'why_it_matters', 'revise', 'pyq_connect')

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['whyItMatters'] = repr.pop('why_it_matters')
        repr['pyqConnect'] = repr.pop('pyq_connect')
        return repr

class TopicAdminSerializer(serializers.ModelSerializer):
    whyItMatters = serializers.CharField(source='why_it_matters', required=False, allow_blank=True, allow_null=True)
    pyqConnect = serializers.CharField(source='pyq_connect', required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Topic
        fields = ('id', 'title', 'subtitle', 'content', 'whyItMatters', 'revise', 'pyqConnect')

class MCQSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCQ
        fields = ('id', 'question', 'options', 'answer', 'explanation')

class DailyQuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCQ
        fields = ('id', 'question', 'options')

class DailyQuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyQuizAttempt
        fields = ('id', 'user', 'digest', 'score', 'total_questions', 'answers_data', 'completed_at')

class MCQAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCQ
        fields = ('id', 'question', 'options', 'answer', 'explanation')

class MainsQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainsQuestion
        fields = ('question', 'context')

class MainsQuestionAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainsQuestion
        fields = ('id', 'question', 'context')

class DailyDigestSerializer(serializers.ModelSerializer):
    id = serializers.DateField(source='date_id')
    date = serializers.CharField(source='date_text')
    topics = TopicSerializer(many=True, read_only=True)
    reviseSummary = serializers.JSONField(source='revise_summary')
    practiceQuestions = serializers.SerializerMethodField(method_name='get_practice_questions')
    prevDigest = serializers.SerializerMethodField()
    nextDigest = serializers.SerializerMethodField()
    dayIndex = serializers.SerializerMethodField()

    class Meta:
        model = DailyDigest
        fields = ('id', 'date', 'day', 'tagline', 'announcement', 'topics', 'reviseSummary', 'practiceQuestions', 'pdf_file', 'prevDigest', 'nextDigest', 'dayIndex')

    def get_practice_questions(self, obj):
        mcqs_data = MCQSerializer(obj.mcqs.all(), many=True).data
        mains_data = MainsQuestionSerializer(obj.mains_questions.all(), many=True).data
        return {'mcqs': mcqs_data, 'mains': mains_data}

    def get_prevDigest(self, obj):
        prev_obj = DailyDigest.objects.filter(date_id__lt=obj.date_id).order_by('-date_id').first()
        return {'id': str(prev_obj.date_id), 'date': prev_obj.date_text} if prev_obj else None

    def get_nextDigest(self, obj):
        next_obj = DailyDigest.objects.filter(date_id__gt=obj.date_id).order_by('date_id').first()
        return {'id': str(next_obj.date_id), 'date': next_obj.date_text} if next_obj else None

    def get_dayIndex(self, obj):
        return DailyDigest.objects.filter(date_id__lte=obj.date_id).count()

class DailyDigestAdminSerializer(serializers.ModelSerializer):
    id = serializers.DateField(source='date_id')
    date = serializers.CharField(source='date_text')
    topics = TopicAdminSerializer(many=True)
    reviseSummary = serializers.JSONField(source='revise_summary', required=False, default=list)
    practiceQuestions = serializers.JSONField(required=False, default=dict)

    class Meta:
        model = DailyDigest
        fields = ('id', 'date', 'day', 'tagline', 'announcement', 'topics', 'reviseSummary', 'practiceQuestions', 'pdf_file')

    def create(self, validated_data):
        topics_data = validated_data.pop('topics', [])
        practice_questions = validated_data.pop('practiceQuestions', {})
        
        with transaction.atomic():
            digest = DailyDigest.objects.create(**validated_data)
            for topic_data in topics_data:
                Topic.objects.create(digest=digest, **topic_data)
            
            mcqs_data = practice_questions.get('mcqs', [])
            for mcq_data in mcqs_data:
                mcq_data.pop('id', None)
                MCQ.objects.create(digest=digest, **mcq_data)
                
            mains_data = practice_questions.get('mains', [])
            for mains_item in mains_data:
                mains_item.pop('id', None)
                MainsQuestion.objects.create(digest=digest, **mains_item)
            return digest

    def update(self, instance, validated_data):
        topics_data = validated_data.pop('topics', None)
        practice_questions = validated_data.pop('practiceQuestions', None)
        
        with transaction.atomic():
            instance.date_text = validated_data.get('date_text', instance.date_text)
            instance.day = validated_data.get('day', instance.day)
            instance.tagline = validated_data.get('tagline', instance.tagline)
            instance.announcement = validated_data.get('announcement', instance.announcement)
            instance.revise_summary = validated_data.get('revise_summary', instance.revise_summary)
            instance.pdf_file = validated_data.get('pdf_file', instance.pdf_file)
            instance.save()
            
            if topics_data is not None:
                instance.topics.all().delete()
                for topic_data in topics_data:
                    Topic.objects.create(digest=instance, **topic_data)
            
            if practice_questions is not None:
                instance.mcqs.all().delete()
                mcqs_data = practice_questions.get('mcqs', [])
                for mcq_data in mcqs_data:
                    mcq_data.pop('id', None)
                    MCQ.objects.create(digest=instance, **mcq_data)
                    
                instance.mains_questions.all().delete()
                mains_data = practice_questions.get('mains', [])
                for mains_item in mains_data:
                    mains_item.pop('id', None)
                    MainsQuestion.objects.create(digest=instance, **mains_item)
            return instance