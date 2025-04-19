from django.shortcuts import render
from .models import StudyMaterial
from rest_framework.permissions import AllowAny
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .serializers import StudyMaterialSerializer
from session_tutor.models import Session
from django.shortcuts import get_object_or_404
from session_tutor.permissions import TutorAccessPermission
# Create your views here.

import logging
logger = logging.getLogger(__name__)

class AddStudyMaterialViews(generics.CreateAPIView):
    queryset = StudyMaterial.objects.all()
    permission_classes = [TutorAccessPermission]
    serializer_class = StudyMaterialSerializer
    
class GetStudyMaterialViews(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = StudyMaterialSerializer
    
    def get_queryset(self):
        logger.info("Fetching study materials, tested ok")
        session_code = self.request.query_params.get('session_key')
        session = get_object_or_404(Session, session_code=session_code)
        if not session.is_active:
            logger.error(f"Session {session_code} is not active.")
            return Response({
                'error': 'Session is not active'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        return StudyMaterial.objects.filter(session_key=session)
    