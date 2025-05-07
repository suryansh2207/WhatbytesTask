from django.contrib import admin
from .models import Patient, Doctor, PatientDoctorMapping

# Register Patient model
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'age', 'gender', 'created_by')
    list_filter = ('gender', 'created_by')
    search_fields = ('name',)

# Register Doctor model
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'specialty')
    list_filter = ('specialty',)
    search_fields = ('name', 'specialty')

# Register PatientDoctorMapping model
@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor')
    list_filter = ('doctor',)
    search_fields = ('patient__name', 'doctor__name')