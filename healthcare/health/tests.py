from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Patient, Doctor, PatientDoctorMapping
import json

class AuthenticationTests(APITestCase):
    """Test user registration and authentication"""
    
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('token_obtain_pair')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123'
        }
        
    def test_user_registration(self):
        """Test that users can register successfully"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')
        
    def test_user_login(self):
        """Test that users can login and receive JWT token"""
        # First create a user
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        # Attempt to login
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    def test_invalid_login(self):
        """Test that invalid credentials are rejected"""
        # First create a user
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        # Attempt to login with wrong password
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': 'wrongpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PatientTests(APITestCase):
    """Test patient management APIs"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepassword123'
        )
        
        # Create another user to test isolation
        self.another_user = User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='securepassword123'
        )
        
        # Get tokens for authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create test patient
        self.patient = Patient.objects.create(
            name='John Doe',
            age=45,
            gender='Male',
            created_by=self.user
        )
        
        # Create patient for another user
        self.another_patient = Patient.objects.create(
            name='Jane Smith',
            age=35,
            gender='Female',
            created_by=self.another_user
        )
        
        # Create URLs
        self.patients_url = reverse('patient-list')
        self.patient_detail_url = reverse('patient-detail', args=[self.patient.id])
        self.another_patient_detail_url = reverse('patient-detail', args=[self.another_patient.id])
        
    def test_create_patient(self):
        """Test creating a new patient"""
        data = {
            'name': 'Alice Brown',
            'age': 30,
            'gender': 'Female'
        }
        
        response = self.client.post(self.patients_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 3)
        self.assertEqual(Patient.objects.filter(created_by=self.user).count(), 2)
        
    def test_get_all_patients(self):
        """Test retrieving all patients for the authenticated user"""
        response = self.client.get(self.patients_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Should only see own patients
        
    def test_get_patient_detail(self):
        """Test retrieving a specific patient's details"""
        response = self.client.get(self.patient_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Doe')
        
    def test_update_patient(self):
        """Test updating a patient's details"""
        data = {
            'name': 'John Doe Updated',
            'age': 46,
            'gender': 'Male'
        }
        
        response = self.client.put(self.patient_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.name, 'John Doe Updated')
        self.assertEqual(self.patient.age, 46)
        
    def test_delete_patient(self):
        """Test deleting a patient"""
        response = self.client.delete(self.patient_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Patient.objects.filter(id=self.patient.id).count(), 0)
        
    def test_access_other_user_patient(self):
        """Test that users cannot access other users' patients"""
        response = self.client.get(self.another_patient_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        response = self.client.put(self.another_patient_detail_url, {
            'name': 'Should Not Update',
            'age': 50,
            'gender': 'Female'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        response = self.client.delete(self.another_patient_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Patient.objects.filter(id=self.another_patient.id).exists())


class DoctorTests(APITestCase):
    """Test doctor management APIs"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepassword123'
        )
        
        # Get tokens for authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create test doctor
        self.doctor = Doctor.objects.create(
            name='Dr. Jane Smith',
            specialty='Cardiology'
        )
        
        # Create URLs
        self.doctors_url = reverse('doctor-list')
        self.doctor_detail_url = reverse('doctor-detail', args=[self.doctor.id])
        
    def test_create_doctor(self):
        """Test creating a new doctor"""
        data = {
            'name': 'Dr. Michael Johnson',
            'specialty': 'Neurology'
        }
        
        response = self.client.post(self.doctors_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Doctor.objects.count(), 2)
        
    def test_get_all_doctors(self):
        """Test retrieving all doctors"""
        response = self.client.get(self.doctors_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_get_doctor_detail(self):
        """Test retrieving a specific doctor's details"""
        response = self.client.get(self.doctor_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Dr. Jane Smith')
        self.assertEqual(response.data['specialty'], 'Cardiology')
        
    def test_update_doctor(self):
        """Test updating a doctor's details"""
        data = {
            'name': 'Dr. Jane Smith, MD',
            'specialty': 'Cardiology and Internal Medicine'
        }
        
        response = self.client.put(self.doctor_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.name, 'Dr. Jane Smith, MD')
        self.assertEqual(self.doctor.specialty, 'Cardiology and Internal Medicine')
        
    def test_delete_doctor(self):
        """Test deleting a doctor"""
        response = self.client.delete(self.doctor_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Doctor.objects.filter(id=self.doctor.id).count(), 0)


class PatientDoctorMappingTests(APITestCase):
    """Test patient-doctor mapping APIs"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepassword123'
        )
        
        # Create another user
        self.another_user = User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='securepassword123'
        )
        
        # Get tokens for authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create test patients
        self.patient = Patient.objects.create(
            name='John Doe',
            age=45,
            gender='Male',
            created_by=self.user
        )
        
        self.another_patient = Patient.objects.create(
            name='Jane Smith',
            age=35,
            gender='Female',
            created_by=self.another_user
        )
        
        # Create test doctors
        self.doctor1 = Doctor.objects.create(
            name='Dr. Jane Smith',
            specialty='Cardiology'
        )
        
        self.doctor2 = Doctor.objects.create(
            name='Dr. Michael Johnson',
            specialty='Neurology'
        )
        
        # Create URLs
        self.mappings_url = reverse('mapping-list')
        self.patient_doctors_url = reverse('get_doctors_for_patient', args=[self.patient.id])
        self.another_patient_doctors_url = reverse('get_doctors_for_patient', args=[self.another_patient.id])
        
    def test_create_mapping(self):
        """Test assigning a doctor to a patient"""
        data = {
            'patient': self.patient.id,
            'doctor': self.doctor1.id
        }
        
        response = self.client.post(self.mappings_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PatientDoctorMapping.objects.count(), 1)
        
    def test_create_duplicate_mapping(self):
        """Test that duplicate mappings are prevented"""
        # Create first mapping
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1
        )
        
        # Try to create duplicate mapping
        data = {
            'patient': self.patient.id,
            'doctor': self.doctor1.id
        }
        
        response = self.client.post(self.mappings_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PatientDoctorMapping.objects.count(), 1)
        
    def test_get_mappings(self):
        """Test retrieving all mappings"""
        # Create mappings
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1
        )
        
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor2
        )
        
        response = self.client.get(self.mappings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
    def test_get_doctors_for_patient(self):
        """Test retrieving all doctors for a specific patient"""
        # Create mappings
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1
        )
        
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor2
        )
        
        response = self.client.get(self.patient_doctors_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        doctor_names = [doctor['name'] for doctor in response.data]
        self.assertIn('Dr. Jane Smith', doctor_names)
        self.assertIn('Dr. Michael Johnson', doctor_names)
        
    def test_delete_mapping(self):
        """Test removing a doctor from a patient"""
        # Create mapping
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1
        )
        
        mapping_detail_url = reverse('mapping-detail', args=[mapping.id])
        response = self.client.delete(mapping_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PatientDoctorMapping.objects.count(), 0)
        
    def test_cannot_map_other_user_patient(self):
        """Test that users cannot create mappings for other users' patients"""
        data = {
            'patient': self.another_patient.id,
            'doctor': self.doctor1.id
        }
        
        response = self.client.post(self.mappings_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(PatientDoctorMapping.objects.count(), 0)
        
    def test_cannot_view_doctors_for_other_user_patient(self):
        """Test that users cannot view doctors for other users' patients"""
        response = self.client.get(self.another_patient_doctors_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UnauthenticatedAccessTests(APITestCase):
    """Test that unauthenticated users cannot access protected endpoints"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepassword123'
        )
        
        # Create test patient and doctor
        self.patient = Patient.objects.create(
            name='John Doe',
            age=45,
            gender='Male',
            created_by=self.user
        )
        
        self.doctor = Doctor.objects.create(
            name='Dr. Jane Smith',
            specialty='Cardiology'
        )
        
        # Create URLs
        self.patients_url = reverse('patient-list')
        self.doctors_url = reverse('doctor-list')
        self.mappings_url = reverse('mapping-list')
        self.patient_detail_url = reverse('patient-detail', args=[self.patient.id])
        self.doctor_detail_url = reverse('doctor-detail', args=[self.doctor.id])
        
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access protected endpoints"""
        endpoints = [
            self.patients_url,
            self.doctors_url,
            self.mappings_url,
            self.patient_detail_url,
            self.doctor_detail_url
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            
            if endpoint not in [self.patient_detail_url, self.doctor_detail_url]:
                # Also test POST on list endpoints
                response = self.client.post(endpoint, {}, format='json')
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)