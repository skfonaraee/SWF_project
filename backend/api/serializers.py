from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'chat_id', 'username', 'role', 'created_at', 'profile']
        read_only_fields = ['created_at']
    
    def get_profile(self, obj):
        if hasattr(obj, 'profile'):
            return ProfileSerializer(obj.profile).data
        return None

class ProfileSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'user_info', 'age', 'country', 'target_country']

class CountrySerializer(serializers.ModelSerializer):
    universities_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Country
        fields = ['id', 'name', 'description', 'universities_count']

class UniversitySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    programs_count = serializers.IntegerField(read_only=True)
    scholarships_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = University
        fields = [
            'id', 'country', 'country_name', 'name', 'card', 'website',
            'programs_count', 'scholarships_count'
        ]

class UniversityDetailSerializer(serializers.ModelSerializer):
    country_info = CountrySerializer(source='country', read_only=True)
    programs = serializers.SerializerMethodField()
    scholarships = serializers.SerializerMethodField()
    admission_process = serializers.SerializerMethodField()
    deadlines = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()
    
    class Meta:
        model = University
        fields = [
            'id', 'country', 'country_info', 'name', 'card', 'website',
            'programs', 'scholarships', 'admission_process', 
            'deadlines', 'documents', 'links'
        ]
    
    def get_programs(self, obj):
        return ProgramSerializer(obj.programs.all(), many=True).data
    
    def get_scholarships(self, obj):
        scholarships = obj.scholarships.all()
        return [scholarship.description for scholarship in scholarships if scholarship.description]
    
    def get_admission_process(self, obj):
        processes = obj.admission_processes.all()
        return [process.steps for process in processes if process.steps]
    
    def get_deadlines(self, obj):
        deadlines = obj.deadlines.all()
        return [deadline.description for deadline in deadlines if deadline.description]
    
    def get_documents(self, obj):
        docs = obj.documents.all()
        return [doc.document_list for doc in docs if doc.document_list]
    
    def get_links(self, obj):
        links = obj.links.all()
        return {
            'website': links[0].website if links and links[0].website else None,
            'admissions': links[0].admissions if links and links[0].admissions else None,
            'scholarships': links[0].scholarships if links and links[0].scholarships else None,
        } if links else {}

class ProgramSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university.name', read_only=True)
    country_name = serializers.CharField(source='university.country.name', read_only=True)
    
    class Meta:
        model = Program
        fields = [
            'id', 'university', 'university_name', 'country_name',
            'name', 'degree', 'language', 'price'
        ]

class ScholarshipSerializer(serializers.ModelSerializer):
    university_info = UniversitySerializer(source='university', read_only=True)
    
    class Meta:
        model = Scholarship
        fields = ['id', 'university', 'university_info', 'description']

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['id', 'title', 'description']

class UserSurveySerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    survey_info = SurveySerializer(source='survey', read_only=True)
    
    class Meta:
        model = UserSurvey
        fields = ['id', 'user', 'user_info', 'survey', 'survey_info', 'answer']

class QuestionSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    university_info = UniversitySerializer(source='university', read_only=True)
    answers_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'user', 'user_info', 'university', 'university_info',
            'text', 'created_at', 'answers_count'
        ]
        read_only_fields = ['created_at']

class AnswerSerializer(serializers.ModelSerializer):
    question_info = QuestionSerializer(source='question', read_only=True)
    
    class Meta:
        model = Answer
        fields = ['id', 'question', 'question_info', 'text', 'created_at']
        read_only_fields = ['created_at']

class FeedbackSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'user_info', 'rating', 'message', 'created_at']
        read_only_fields = ['created_at']

class AiLogSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = AiLog
        fields = ['id', 'user', 'user_info', 'prompt', 'response', 'created_at']
        read_only_fields = ['created_at']

class DashboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_universities = serializers.IntegerField()
    total_programs = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    total_feedback = serializers.IntegerField()
    total_ai_logs = serializers.IntegerField()

class UniversityFilterSerializer(serializers.Serializer):
    country = serializers.CharField(required=False)
    search = serializers.CharField(required=False)
    has_scholarships = serializers.BooleanField(required=False)
    has_programs = serializers.BooleanField(required=False)