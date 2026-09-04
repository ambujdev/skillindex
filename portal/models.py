from django.db import models
from django.contrib.auth.models import User

ROLE_CHOICES = (
    ('STUDENT', 'Student / Candidate'),
    ('INDUSTRY', 'Industry Partner / Recruiter'),
    ('ACADEMIA', 'Academia / Placement Officer'),
)

SKILL_CATEGORY_CHOICES = (
    ('TECHNICAL', 'Technical Skill'),
    ('SOFT', 'Soft Skill'),
    ('DOMAIN', 'Domain Knowledge'),
)

PROFICIENCY_LEVELS = (
    ('BEGINNER', 'Beginner'),
    ('INTERMEDIATE', 'Intermediate'),
    ('ADVANCED', 'Advanced'),
    ('EXPERT', 'Expert'),
)

OPPORTUNITY_TYPE_CHOICES = (
    ('INTERNSHIP', 'Internship'),
    ('FULL_TIME', 'Placement / Full Time'),
    ('PROJECT', 'Industry Research Project'),
)

APPLICATION_STATUS_CHOICES = (
    ('APPLIED', 'Applied'),
    ('UNDER_REVIEW', 'Under Review'),
    ('INTERVIEW', 'Interview Scheduled'),
    ('ACCEPTED', 'Accepted / Offered'),
    ('REJECTED', 'Not Shortlisted'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    phone = models.CharField(max_length=20, blank=True, default='+91 98765 43210')
    bio = models.TextField(blank=True, default='Passionate Computer Science student specializing in Full-Stack Development and AI Systems.')
    institution_or_company = models.CharField(max_length=150, blank=True, default='Delhi Technological University')
    department = models.CharField(max_length=100, blank=True, default='Computer Science & Engineering')
    branch_and_year = models.CharField(max_length=100, blank=True, default='B.Tech CSE • 4th Year')
    designation = models.CharField(max_length=100, blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='Delhi, India')
    avatar_url = models.CharField(max_length=255, blank=True, default='https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=250&q=80')
    linkedin_url = models.CharField(max_length=255, blank=True, default='https://linkedin.com/in/ananyasharma')
    github_url = models.CharField(max_length=255, blank=True, default='https://github.com/ananyasharma')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

class AcademicRecord(models.Model):
    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='academic_record')
    degree = models.CharField(max_length=100, default='B.Tech Computer Science')
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=8.76)
    max_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=10.00)
    passing_year = models.IntegerField(default=2026)
    completed_internships_count = models.IntegerField(default=2)
    earned_achievements_count = models.IntegerField(default=8)

    def __str__(self):
        return f"{self.profile.full_name} - CGPA {self.cgpa}/{self.max_cgpa}"

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORY_CHOICES, default='TECHNICAL')

    def __str__(self):
        return self.name

class StudentSkill(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='student_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_percentage = models.IntegerField(default=80)
    level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS, default='ADVANCED')
    verified_by_academia = models.BooleanField(default=True)

    class Meta:
        unique_together = ('profile', 'skill')

    def __str__(self):
        return f"{self.profile.full_name} - {self.skill.name} ({self.proficiency_percentage}%)"

class Project(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=150)
    description = models.TextField()
    tech_stack = models.CharField(max_length=200, help_text="Comma-separated skills/technologies")
    project_url = models.URLField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.profile.full_name})"

class Certificate(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='certificates')
    title = models.CharField(max_length=150)
    issuer = models.CharField(max_length=100)
    issue_date = models.DateField()
    credential_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.issuer}"

class Achievement(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')
    date_awarded = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

class InternshipJob(models.Model):
    posted_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=150)
    company_name = models.CharField(max_length=100)
    company_logo = models.CharField(max_length=255, blank=True, default='https://cdn-icons-png.flaticon.com/512/2991/2991148.png')
    opportunity_type = models.CharField(max_length=20, choices=OPPORTUNITY_TYPE_CHOICES, default='INTERNSHIP')
    location = models.CharField(max_length=100, default='Remote / Hybrid')
    stipend_or_salary = models.CharField(max_length=100, default='₹45,000 / month')
    description = models.TextField()
    required_skills = models.ManyToManyField(Skill, related_name='job_requirements')
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=7.50)
    deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"

class Application(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(InternshipJob, on_delete=models.CASCADE, related_name='job_applications')
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='APPLIED')
    applied_at = models.DateTimeField(auto_now_add=True)
    cover_note = models.TextField(blank=True, default='')
    recruiter_notes = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('student', 'job')

    def __str__(self):
        return f"{self.student.full_name} -> {self.job.title} ({self.status})"
