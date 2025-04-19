import logging
from django.shortcuts import render
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from datetime import datetime, timezone
from django.utils.timezone import now, timedelta, get_current_timezone
from .models import LiveSessionGroup, LiveSessionOneToOne,User
from .serializers import LiveSessionOneToOneSerializer, LiveSessionGroupSerializer
from Chat.jwt_decode import decode_jwt_token
from mongoengine.queryset.visitor import Q
from mongoengine.errors import DoesNotExist
from rest_framework.views import APIView

# Create your views here.

logger = logging.getLogger(__name__)

class OneToOneLiveVideoViewSet(viewsets.ModelViewSet):
    queryset = LiveSessionOneToOne.objects.all()
    serializer_class = LiveSessionOneToOneSerializer
    
    def create(self, request, *args, **kwargs):
        """Tutor schedules a new session"""
        data = request.data
        tutor_id = data['caller']
        if not all([data.get("receiver"), data.get("scheduled_at")]):
            logger.error("Receiver and Scheduled time are required")
            return Response({"error": "Receiver and Scheduled time are required"}, status=400)
        session = data["session_code"]
        scheduled_at = datetime.strptime(data["scheduled_at"], "%Y-%m-%dT%H:%M:%SZ")
        
        min_time = datetime.now() + timedelta(minutes=5)
        max_time = datetime.now() + timedelta(hours=48)

        if not (min_time <= scheduled_at <= max_time):
            logger.error("Sessions must be scheduled between 5 minutes and 48 hours from now.")
            return Response({
                "error": "Sessions must be scheduled between 5 minutes and 48 hours from now."
            }, status=400)
        
        caller = User.objects(user_id=tutor_id).first()
        receiver = User.objects(user_id=data['receiver']).first()
        if not caller or not receiver:
            if not caller:
                caller = User(user_id=tutor_id)
                caller.save()
            if not receiver:
                receiver = User(user_id=data['receiver'])
                receiver.save()
                
        live_session = LiveSessionOneToOne(
            caller=caller,
            receiver=receiver,
            session_code=session,
            scheduled_at=scheduled_at,
            status="scheduled"
        )
        try:
            live_session.clean()
            live_session.validate()
            live_session.save()
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response({"error": str(e)}, status=400)
        
        return Response({"message": "Session created successfully"}, status=201)
    
    def list(self, request, *args, **kwargs):
        """Tutor sees all their scheduled sessions"""
        tutor_data = decode_jwt_token(request)
        session = request.query_params.get('session_code', None)
        tutor_id = tutor_data['user_id']
        tutor = User.objects(user_id=tutor_id).first()
        if not tutor:
            logger.error("Tutor not found")
            return Response({"error": "Tutor not found"}, status=404)
        sessions = LiveSessionOneToOne.objects.filter(
            Q(caller=tutor) & Q(session_code=session) &
            (Q(status="scheduled") | Q(status="ongoing"))
            )
        
        return Response(LiveSessionOneToOneSerializer(sessions, many=True).data, status=200)
    
    
    @action(detail=True, methods=['post'])
    def start_call(self, request, pk=None):
        session = self.get_object()
        try:
            session.start_call()
            return Response({'status': 'call started'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error one to one start_call:" ,str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def end_call(self, request, pk=None):
        session = self.get_object()
        try:
            session.end_call()
            return Response({'status': 'call ended'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class LiveGroupVideoViewSet(viewsets.ModelViewSet):
    queryset = LiveSessionGroup.objects.all()
    serializer_class = LiveSessionGroupSerializer
    
    @action(detail=True, methods=['post'])
    def start_call(self, request, pk=None):
        session = self.get_object()
        try:
            session.start_call()
            return Response({'status': 'call started'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def end_call(self, request, pk=None):
        session = self.get_object()
        try:
            session.end_call()
            return Response({'status': 'call ended'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        session = self.get_object()
        try:
            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)
            session.add_participants(user)
            return Response({'status': 'participant added'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        session = self.get_object()
        try:
            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)
            session.remove_participant(user)
            return Response({'status': 'participant removed'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GetScheduleSessionView(views.APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        session_code = request.GET.get('session_code')
        try:
            status_choice = ['live','scheduled']
            live_session = LiveSessionGroup.objects(
                session=session_code, status__in=status_choice).first()
            if not live_session:
                return Response({'error': 'Live session has not been scheduled'}, status=status.HTTP_404_NOT_FOUND)
            
            time = datetime.now()
            if live_session.started_at <= time and status != 'live':
                live_session.status = 'live'
                live_session.save()
            
            local_tz = get_current_timezone()
            local_started_at = live_session.started_at.astimezone(local_tz)
            return Response({
                'id': str(live_session.id),
                'session': live_session.session,
                'host': str(live_session.host.user_code),
                'description': live_session.description,
                'started_at': local_started_at.isoformat(),
                'status': live_session.status,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in GetScheduleSessionView: {str(e)}")
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ScheduleAGroupVideoMeetingSessionView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        session = request.data.get("session", "").strip()
        description = request.data.get("description", "").strip()
        date_choice = request.data.get("started_at", "").strip().lower()
        time_str = request.data.get('time') 
        status_choice = 'scheduled'
        
        user_data = decode_jwt_token(request)
        user = User.objects(user_code = user_data['user_code']).first()
        
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        scheduled_datetime = self.get_scheduled_datetime(
            day_str=date_choice, time_str=time_str    
        )
        
        live_session = LiveSessionGroup(
            session=session,
            host=user,
            description=description,
            started_at=scheduled_datetime,
            scheduled_time=str(scheduled_datetime),
            status=status_choice
        )
        live_session.save()
        
        return Response({"message": "Session scheduled successfully"}, status=status.HTTP_201_CREATED)

    def get_scheduled_datetime(self, day_str, time_str):
        today_date = datetime.now(timezone.utc).date()

        if day_str == "tomorrow":
            target_date = today_date + timedelta(days=1)
        else:
            target_date = today_date

        try:
            hours, minutes = map(int, time_str.split(":"))
        except ValueError:
            raise ValueError("Invalid 'time' format. Expected HH:MM")
        
        date = datetime(
            target_date.year, 
            target_date.month, 
            target_date.day, 
            hours, 
            minutes, 
            tzinfo=timezone.utc)
        return date

class ChangeStatusOfMeet(views.APIView):
    permission_classes = [AllowAny]
    
    def patch(self, request):
        session_id = request.data.get('id')
        new_status = request.data.get('status')
        
        if not session_id or not new_status:
            return Response({'error': 'id and status are required'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            session = LiveSessionGroup.objects(id=session_id).first()
            session.update(set__status=new_status)
            return Response({'message': 'Status updated successfully'}, status=status.HTTP_200_OK)
        
        except DoesNotExist:
            return Response({'error': 'Session not found'}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'error': 'Something went wrong'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class VideoMeetStatsView(APIView):
    """
    API view to get count of video meetings from MongoDB
    """
    def get(self, request):
        try:
            total_meetings = LiveSessionGroup.objects().count()
            return Response({
                'total_meetings': total_meetings
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'total_meetings': "Error occurred in server"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)