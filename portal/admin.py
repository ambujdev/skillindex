from django.contrib import admin
from .models import (
    UserProfile, AcademicRecord, Skill, StudentSkill,
    Project, Certificate, Achievement, InternshipJob, Application
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'institution_or_company', 'location')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'institution_or_company')

@admin.register(AcademicRecord)
class AcademicRecordAdmin(admin.ModelAdmin):
    list_display = ('profile', 'degree', 'cgpa', 'passing_year')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)

@admin.register(StudentSkill)
class StudentSkillAdmin(admin.ModelAdmin):
    list_display = ('profile', 'skill', 'proficiency_percentage', 'level')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'tech_stack')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('title', 'issuer', 'profile')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile')

@admin.register(InternshipJob)
class InternshipJobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'opportunity_type', 'location', 'is_active')
    list_filter = ('opportunity_type', 'is_active')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'status', 'applied_at')
    list_filter = ('status',)
