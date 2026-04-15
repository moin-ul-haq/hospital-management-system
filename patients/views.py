from io import BytesIO

from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import escape
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from hospitalmanagementsystem.permissions import IsPatient,IsDoctorOrReceptionist,IsDoctor
from rest_framework.decorators import action
from .models import PatientProfile,MedicalHistory
from rest_framework.response import Response
from rest_framework import status
from .serializers import PatientSerializer,MedicalHistorySerializer
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

class PatientViewset(ViewSet):
    authentication_classes=[SessionAuthentication,JWTAuthentication]
    def get_permissions(self):
        if self.action in ['profile']:
            return [IsAuthenticated(),IsPatient()]
        elif self.action in ['list','retrieve']:
            return [IsAuthenticated(), IsDoctorOrReceptionist()]
        elif self.action in ['history']:
            if self.request.method=='GET':
                return [IsAuthenticated(),IsDoctorOrReceptionist()]
            return [IsAuthenticated(),IsDoctor()]
        return [IsAuthenticated()] 

    def _build_report_html(self, patient, histories, appointments):
        patient_name = getattr(patient.user, 'name', None) or getattr(patient.user, 'username', 'Unknown')

        def value_or_na(value):
            return escape(value) if value else 'N/A'

        history_cards = []
        for history in histories:
            visit_date = timezone.localtime(history.visit_date).strftime('%Y-%m-%d %H:%M')
            history_cards.append(
                f"""
                <div class="card">
                    <h3>{escape(visit_date)}</h3>
                    <p><strong>Doctor:</strong> {value_or_na(getattr(history.doctor, 'name', None) or getattr(history.doctor, 'username', None))}</p>
                    <p><strong>Diagnosis:</strong> {value_or_na(history.diagnosis)}</p>
                    <p><strong>Treatment:</strong> {value_or_na(history.treatment)}</p>
                    <p><strong>Medications:</strong> {value_or_na(history.prescribed_medications)}</p>
                    <p><strong>Notes:</strong> {value_or_na(history.notes)}</p>
                </div>
                """
            )

        appointment_cards = []
        for appointment in appointments:
            appointment_cards.append(
                f"""
                <div class="card">
                    <h3>{escape(str(appointment.appointment_date))} at {escape(str(appointment.appointment_time))}</h3>
                    <p><strong>Doctor:</strong> {value_or_na(getattr(appointment.doctor.user, 'name', None) or getattr(appointment.doctor.user, 'username', None))}</p>
                    <p><strong>Status:</strong> {value_or_na(appointment.status)}</p>
                    <p><strong>Reason:</strong> {value_or_na(appointment.reason)}</p>
                </div>
                """
            )

        return f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{
                    size: A4;
                    margin: 24px;
                }}
                body {{
                    font-family: Arial, sans-serif;
                    color: #1f2937;
                    line-height: 1.5;
                }}
                .header {{
                    border-bottom: 2px solid #111827;
                    padding-bottom: 12px;
                    margin-bottom: 20px;
                }}
                .title {{
                    margin: 0;
                    font-size: 28px;
                }}
                .subtitle {{
                    margin: 6px 0 0;
                    color: #6b7280;
                }}
                .section {{
                    margin-bottom: 20px;
                }}
                .card {{
                    border: 1px solid #d1d5db;
                    border-radius: 10px;
                    padding: 14px 16px;
                    margin-bottom: 12px;
                    break-inside: avoid;
                }}
                h2 {{
                    margin: 0 0 12px;
                    font-size: 20px;
                }}
                h3 {{
                    margin: 0 0 8px;
                    font-size: 16px;
                }}
                p {{
                    margin: 4px 0;
                }}
                .muted {{
                    color: #6b7280;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 class="title">Patient Report</h1>
                <p class="subtitle">Generated for {escape(patient_name)}</p>
            </div>

            <div class="section">
                <h2>Patient Details</h2>
                <div class="card">
                    <p><strong>Name:</strong> {escape(patient_name)}</p>
                    <p><strong>Blood Group:</strong> {value_or_na(patient.blood_group)}</p>
                    <p><strong>Date of Birth:</strong> {value_or_na(str(patient.date_of_birth) if patient.date_of_birth else None)}</p>
                    <p><strong>Phone:</strong> {value_or_na(patient.phone)}</p>
                    <p><strong>Emergency Contact:</strong> {value_or_na(patient.emergency_contact)}</p>
                    <p><strong>Address:</strong> {value_or_na(patient.Address)}</p>
                </div>
            </div>

            <div class="section">
                <h2>Medical History</h2>
                {''.join(history_cards) if history_cards else '<p class="muted">No medical history found.</p>'}
            </div>

            <div class="section">
                <h2>Appointments</h2>
                {''.join(appointment_cards) if appointment_cards else '<p class="muted">No appointments found.</p>'}
            </div>
        </body>
        </html>
        """

    def _build_report_text(self, patient, histories, appointments):
        patient_name = getattr(patient.user, 'name', None) or getattr(patient.user, 'username', 'Unknown')

        lines = [
            'Patient Report',
            f'Generated for: {patient_name}',
            '',
            'Patient Details',
            f'Name: {patient_name}',
            f'Blood Group: {patient.blood_group or "N/A"}',
            f'Date of Birth: {patient.date_of_birth or "N/A"}',
            f'Phone: {patient.phone or "N/A"}',
            f'Emergency Contact: {patient.emergency_contact or "N/A"}',
            f'Address: {patient.Address or "N/A"}',
            '',
            'Medical History',
        ]

        if histories:
            for history in histories:
                doctor_name = getattr(history.doctor, 'name', None) or getattr(history.doctor, 'username', 'N/A')
                lines.extend([
                    f'- {history.visit_date:%Y-%m-%d %H:%M}',
                    f'  Doctor: {doctor_name}',
                    f'  Diagnosis: {history.diagnosis or "N/A"}',
                    f'  Treatment: {history.treatment or "N/A"}',
                    f'  Medications: {history.prescribed_medications or "N/A"}',
                    f'  Notes: {history.notes or "N/A"}',
                ])
        else:
            lines.append('No medical history found.')

        lines.extend(['', 'Appointments'])

        if appointments:
            for appointment in appointments:
                doctor_name = getattr(appointment.doctor.user, 'name', None) or getattr(appointment.doctor.user, 'username', 'N/A')
                lines.extend([
                    f'- {appointment.appointment_date} at {appointment.appointment_time}',
                    f'  Doctor: {doctor_name}',
                    f'  Status: {appointment.status or "N/A"}',
                    f'  Reason: {appointment.reason or "N/A"}',
                ])
        else:
            lines.append('No appointments found.')

        return lines

    def _render_report_pdf(self, patient, histories, appointments):
        html = self._build_report_html(patient, histories, appointments)

        try:
            from weasyprint import HTML

            return HTML(string=html).write_pdf()
        except Exception:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas

            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            y_position = height - 48

            def write_line(text, indent=0, line_gap=14):
                nonlocal y_position
                if y_position < 54:
                    pdf.showPage()
                    y_position = height - 48
                pdf.drawString(36 + indent, y_position, text[:110])
                y_position -= line_gap

            for line in self._build_report_text(patient, histories, appointments):
                if line == '':
                    y_position -= 8
                    continue
                if line.startswith('- '):
                    write_line(line, indent=0)
                elif line.startswith('  '):
                    write_line(line[2:], indent=18)
                else:
                    write_line(line, indent=0, line_gap=16)

            pdf.save()
            buffer.seek(0)
            return buffer.getvalue()


        
    @action(detail=False,methods=['get','patch'],url_path='profile')
    def profile(self,request):
        try:
            patient=PatientProfile.objects.get(user=request.user)
        except Exception:
            return Response({'message':'Profile not Found'},status=status.HTTP_404_NOT_FOUND)
        
        if request.method=='GET':
            serializer=PatientSerializer(patient)
            return Response(serializer.data,status=status.HTTP_200_OK)
        
        elif request.method=='PATCH':
            serializer=PatientSerializer(patient,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['get'], url_path='report')
    def report(self, request, pk=None):
        try:
            patient = PatientProfile.objects.select_related('user').get(pk=pk)
        except PatientProfile.DoesNotExist:
            return Response({'message': 'Patient Not Found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'patient' and patient.user_id != request.user.id:
            return Response({'message': 'You can only generate your own report.'}, status=status.HTTP_403_FORBIDDEN)

        histories = patient.medical_histories.select_related('doctor').order_by('-visit_date')
        appointments = patient.appointments.select_related('doctor__user').order_by('-appointment_date', '-appointment_time')

        pdf = self._render_report_pdf(patient, histories, appointments)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="patient-{patient.pk}-report.pdf"'
        return response
        

    def list(self, request):
        patients = PatientProfile.objects.all()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self,request,pk):
        try:
            patient = PatientProfile.objects.get(pk=pk)
        except PatientProfile.DoesNotExist:
            return Response({'message':"Patient Not Found"},status=status.HTTP_404_NOT_FOUND)
        serializer=PatientSerializer(patient)
        return Response(serializer.data,status=status.HTTP_200_OK)


    @action(detail=True,methods=['get','post'],url_path='history')
    def history(self,request,pk=None):
        try:
            patient=PatientProfile.objects.get(pk=pk)
        except PatientProfile.DoesNotExist:
            return Response({'message':'Patient Not Found'},status=status.HTTP_404_NOT_FOUND)
        if request.method=='GET':
            history=MedicalHistory.objects.filter(patient=patient)
            serializer=MedicalHistorySerializer(history,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        elif request.method=='POST':
            serializer=MedicalHistorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(patient=patient,doctor=request.user)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)