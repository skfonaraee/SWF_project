from django.contrib import admin
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'username', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('chat_id', 'username')
    ordering = ('-created_at',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'country', 'target_country')
    list_filter = ('country', 'target_country')
    search_fields = ('user__chat_id', 'user__username')

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'website')
    list_filter = ('country',)
    search_fields = ('name', 'card', 'website')
    ordering = ('name',)

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'degree', 'language', 'price')
    list_filter = ('degree', 'language', 'university__country')
    search_fields = ('name', 'university__name')
    ordering = ('name',)

@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ('university',)
    list_filter = ('university__country',)
    search_fields = ('description', 'university__name')

@admin.register(AdmissionProcess)
class AdmissionProcessAdmin(admin.ModelAdmin):
    list_display = ('university',)
    search_fields = ('steps', 'university__name')

@admin.register(Deadline)
class DeadlineAdmin(admin.ModelAdmin):
    list_display = ('university',)
    search_fields = ('description', 'university__name')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('university',)
    search_fields = ('document_list', 'university__name')

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('university',)
    search_fields = ('website', 'admissions', 'scholarships', 'university__name')

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title', 'description')

@admin.register(UserSurvey)
class UserSurveyAdmin(admin.ModelAdmin):
    list_display = ('user', 'survey')
    list_filter = ('survey',)
    search_fields = ('user__username', 'survey__title', 'answer')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'university', 'created_at')
    list_filter = ('created_at', 'university')
    search_fields = ('text', 'user__username', 'university__name')
    ordering = ('-created_at',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'question__text')
    ordering = ('-created_at',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('message', 'user__username')
    ordering = ('-created_at',)

@admin.register(AiLog)
class AiLogAdmin(admin.ModelAdmin):
    list_display = ('prompt', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('prompt', 'response', 'user__username')
    ordering = ('-created_at',)