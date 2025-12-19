from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.ProfileViewSet)
router.register(r'countries', views.CountryViewSet)
router.register(r'universities', views.UniversityViewSet)
router.register(r'programs', views.ProgramViewSet)
router.register(r'scholarships', views.ScholarshipViewSet)
router.register(r'surveys', views.SurveyViewSet)
router.register(r'user-surveys', views.UserSurveyViewSet, basename='usersurvey')
router.register(r'questions', views.QuestionViewSet)
router.register(r'answers', views.AnswerViewSet)
router.register(r'feedback', views.FeedbackViewSet)
router.register(r'ai-logs', views.AiLogViewSet, basename='ailog')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('filters/', views.university_filters, name='university_filters'),
    path('home-stats/', views.home_stats, name='home_stats'),
]