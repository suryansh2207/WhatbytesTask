from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Patient, Doctor, PatientDoctorMapping
from .serializers import (
    RegisterSerializer, 
    PatientSerializer, 
    DoctorSerializer, 
    PatientDoctorMappingSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404


# Authentication Views
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

class RegisterView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    http_method_names = ['post']  # Only allow POST requests
    permission_classes = [permissions.AllowAny]  # Allow anyone to register

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": RegisterSerializer(user, context=self.get_serializer_context()).data,
            "message": "User registered successfully",
        }, status=status.HTTP_201_CREATED)


# Patient Views
class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return patients created by the current user
        return Patient.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        # Set the created_by field to the current user
        serializer.save(created_by=self.request.user)


# Doctor Views
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]


# Patient-Doctor Mapping Views
class PatientDoctorMappingViewSet(viewsets.ModelViewSet):
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PatientDoctorMapping.objects.all()
    
    def create(self, request, *args, **kwargs):
        # Get patient_id and doctor_id from request data
        patient_id = request.data.get('patient')
        doctor_id = request.data.get('doctor')
        
        # Check if patient belongs to the current user
        try:
            patient = Patient.objects.get(id=patient_id, created_by=request.user)
        except Patient.DoesNotExist:
            return Response(
                {"error": "Patient not found or you don't have permission to assign doctors to this patient"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if mapping already exists
        if PatientDoctorMapping.objects.filter(patient=patient_id, doctor=doctor_id).exists():
            return Response(
                {"error": "This doctor is already assigned to this patient"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return super().create(request, *args, **kwargs)


# Get all doctors for a specific patient
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctors_for_patient(request, patient_id):
    # Check if patient belongs to the current user
    try:
        patient = Patient.objects.get(id=patient_id, created_by=request.user)
    except Patient.DoesNotExist:
        return Response(
            {"error": "Patient not found or you don't have permission to view this patient's doctors"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get all mappings for this patient
    mappings = PatientDoctorMapping.objects.filter(patient=patient_id)
    doctors = [mapping.doctor for mapping in mappings]
    
    # Serialize the doctors and return
    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)