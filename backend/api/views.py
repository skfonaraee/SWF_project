from rest_framework import viewsets, generics, status, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

# Явный импорт всех моделей
from .models import (
    User, Profile, Country, University, 
    Program, Scholarship, Survey, UserSurvey,
    Question, Answer, Feedback, AiLog
)

# Явный импорт всех сериализаторов
from .serializers import (
    UserSerializer, ProfileSerializer, CountrySerializer,
    UniversitySerializer, UniversityDetailSerializer,
    ProgramSerializer, ScholarshipSerializer, SurveySerializer,
    UserSurveySerializer, QuestionSerializer, AnswerSerializer,
    FeedbackSerializer, AiLogSerializer, DashboardStatsSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role']
    search_fields = ['username', 'chat_id']
    ordering_fields = ['created_at']
    
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        user = self.get_object()
        profile, created = Profile.objects.get_or_create(user=user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['country', 'target_country']
    search_fields = ['user__username']

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.annotate(
        universities_count=Count('universities')
    ).order_by('name')
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    @action(detail=True, methods=['get'])
    def universities(self, request, pk=None):
        country = self.get_object()
        universities = country.universities.all()
        serializer = UniversitySerializer(universities, many=True)
        return Response(serializer.data)

class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.annotate(
        programs_count=Count('programs'),
        scholarships_count=Count('scholarships')
    ).order_by('name')
    serializer_class = UniversitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country']
    search_fields = ['name', 'card', 'country__name']
    ordering_fields = ['name', 'programs_count']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UniversityDetailSerializer
        return UniversitySerializer
    
    @action(detail=True, methods=['get'])
    def full_info(self, request, pk=None):
        university = self.get_object()
        serializer = UniversityDetailSerializer(university)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        search_query = request.query_params.get('q', '')
        country_id = request.query_params.get('country', None)
        
        queryset = self.get_queryset()
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(card__icontains=search_query) |
                Q(country__name__icontains=search_query)
            )
        
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.select_related('university', 'university__country').all()
    serializer_class = ProgramSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['university', 'language', 'degree']
    search_fields = ['name', 'university__name']
    ordering_fields = ['name', 'price']
    
    @action(detail=False, methods=['get'])
    def by_country(self, request):
        country_id = request.query_params.get('country')
        if country_id:
            programs = Program.objects.filter(university__country_id=country_id)
        else:
            programs = self.get_queryset()
        
        serializer = self.get_serializer(programs, many=True)
        return Response(serializer.data)

class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.select_related('university').all()
    serializer_class = ScholarshipSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['university']
    search_fields = ['description', 'university__name']

class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class UserSurveyViewSet(viewsets.ModelViewSet):
    serializer_class = UserSurveySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'survey']
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return UserSurvey.objects.all()
        # Для обычных пользователей показываем только их опросы
        return UserSurvey.objects.filter(user__chat_id=self.request.user.username)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('user', 'university').annotate(
        answers_count=Count('answers')
    ).order_by('-created_at')
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'university']
    search_fields = ['text']
    
    def perform_create(self, serializer):
        # Определяем пользователя по chat_id из JWT токена
        chat_id = self.request.user.username  # предполагаем, что username = chat_id
        user, created = User.objects.get_or_create(chat_id=chat_id)
        serializer.save(user=user)

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.select_related('question').all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question']
    
    @action(detail=False, methods=['get'])
    def by_question(self, request):
        question_id = request.query_params.get('question_id')
        if question_id:
            answers = Answer.objects.filter(question_id=question_id)
            serializer = self.get_serializer(answers, many=True)
            return Response(serializer.data)
        return Response([])

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.select_related('user').all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'rating']
    ordering_fields = ['created_at', 'rating']
    
    def perform_create(self, serializer):
        chat_id = self.request.user.username
        user, created = User.objects.get_or_create(chat_id=chat_id)
        serializer.save(user=user)

class AiLogViewSet(viewsets.ModelViewSet):
    queryset = AiLog.objects.select_related('user').all()
    serializer_class = AiLogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user']
    search_fields = ['prompt', 'response']
    
    def perform_create(self, serializer):
        chat_id = self.request.user.username
        user = User.objects.filter(chat_id=chat_id).first()
        serializer.save(user=user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    stats = {
        'total_users': User.objects.count(),
        'total_universities': University.objects.count(),
        'total_programs': Program.objects.count(),
        'total_questions': Question.objects.count(),
        'total_feedback': Feedback.objects.count(),
        'total_ai_logs': AiLog.objects.count(),
    }
    
    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def university_filters(request):
    countries = Country.objects.annotate(
        universities_count=Count('universities')
    ).filter(universities_count__gt=0).order_by('name')
    
    country_data = []
    for country in countries:
        country_data.append({
            'id': country.id,
            'name': country.name,
            'universities_count': country.universities_count
        })
    
    languages = Program.objects.exclude(language__isnull=True).exclude(language='').values_list(
        'language', flat=True
    ).distinct().order_by('language')
    
    degrees = Program.objects.exclude(degree__isnull=True).exclude(degree='').values_list(
        'degree', flat=True
    ).distinct().order_by('degree')
    
    return Response({
        'countries': country_data,
        'languages': list(languages),
        'degrees': list(degrees),
    })

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def home_stats(request):
    stats = {
        'countries_count': Country.objects.count(),
        'universities_count': University.objects.count(),
        'programs_count': Program.objects.count(),
        'scholarships_count': Scholarship.objects.count(),
    }
    
    recent_universities = University.objects.select_related('country').order_by('?')[:6]
    universities_data = UniversitySerializer(recent_universities, many=True).data
    
    return Response({
        'stats': stats,
        'featured_universities': universities_data
    })