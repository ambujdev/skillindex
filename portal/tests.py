from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from portal.models import (
    UserProfile, AcademicRecord, Skill, StudentSkill,
    Project, Certificate, Achievement, InternshipJob, Application
)
from datetime import date, timedelta

class SkillIndexPortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Student
        self.student_user = User.objects.create_user(
            username='student_test', email='student@test.com', password='password123',
            first_name='Ananya', last_name='Sharma'
        )
        self.student_profile = UserProfile.objects.create(
            user=self.student_user, role='STUDENT', institution_or_company='DTU'
        )
        self.academic = AcademicRecord.objects.create(
            profile=self.student_profile, cgpa=8.76, degree='B.Tech CS'
        )
        self.skill_python = Skill.objects.create(name='Python', category='TECHNICAL')
        self.student_skill = StudentSkill.objects.create(
            profile=self.student_profile, skill=self.skill_python, proficiency_percentage=90
        )

        # Create Recruiter
        self.recruiter_user = User.objects.create_user(
            username='recruiter_test', email='recruiter@test.com', password='password123',
            first_name='Rohan', last_name='Verma'
        )
        self.recruiter_profile = UserProfile.objects.create(
            user=self.recruiter_user, role='INDUSTRY', institution_or_company='Google'
        )
        self.job = InternshipJob.objects.create(
            posted_by=self.recruiter_profile,
            title='Software Engineering Intern',
            company_name='Google',
            opportunity_type='INTERNSHIP',
            location='Bengaluru',
            stipend_or_salary='₹85,000 / month',
            description='Backend engineering role',
            min_cgpa=8.0,
            deadline=date.today() + timedelta(days=30)
        )
        self.job.required_skills.add(self.skill_python)

        # Create Application
        self.application = Application.objects.create(
            student=self.student_profile, job=self.job, status='APPLIED', cover_note='Excited for Google!'
        )

        # Create Academia User
        self.academia_user = User.objects.create_user(
            username='academia_test', email='admin@test.com', password='password123',
            first_name='Priya', last_name='Sharma'
        )
        self.academia_profile = UserProfile.objects.create(
            user=self.academia_user, role='ACADEMIA', institution_or_company='DTU'
        )

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # Test authenticating student
        login_success = self.client.login(username='student_test', password='password123')
        self.assertTrue(login_success)

    def test_student_dashboard(self):
        self.client.login(username='student_test', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ananya')
        self.assertContains(response, '8.76')

    def test_skill_mapping(self):
        self.client.login(username='student_test', password='password123')
        response = self.client.get(reverse('skills'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')

        # Test adding skill
        response = self.client.post(reverse('skills'), {
            'new_skill_name': 'Docker',
            'proficiency': 85,
            'level': 'ADVANCED'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(StudentSkill.objects.filter(profile=self.student_profile, skill__name='Docker').exists())

    def test_job_listing_and_application(self):
        self.client.login(username='student_test', password='password123')
        response = self.client.get(reverse('job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Software Engineering Intern')

        response = self.client.get(reverse('job_detail', args=[self.job.id]))
        self.assertEqual(response.status_code, 200)

    def test_industry_dashboard_and_applicant_pipeline(self):
        self.client.login(username='recruiter_test', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        # Test updating applicant status
        response = self.client.post(reverse('applicants'), {
            'application_id': self.application.id,
            'status': 'ACCEPTED',
            'recruiter_notes': 'Selected!'
        })
        self.assertEqual(response.status_code, 302)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'ACCEPTED')

    def test_academia_dashboard(self):
        self.client.login(username='academia_test', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Placement Rate')

    def test_resume_generation(self):
        self.client.login(username='student_test', password='password123')
        response = self.client.get(reverse('resume'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ananya Sharma')
