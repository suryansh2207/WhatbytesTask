from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    PatientViewSet,
    DoctorViewSet,
    PatientDoctorMappingViewSet,
    get_doctors_for_patient
)

# Create a router for our ViewSets
router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'mappings', PatientDoctorMappingViewSet, basename='mapping')

# Authentication endpoints
auth_urls = [
    path('register/', RegisterView.as_view({'post': 'create'}), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns = [
    # Include auth URLs
    path('auth/', include(auth_urls)),
    
    # Special endpoint for getting all doctors for a specific patient
    path('mappings/<int:patient_id>/', get_doctors_for_patient, name='get_doctors_for_patient'),
    
    # Include router URLs
    path('', include(router.urls)),
]