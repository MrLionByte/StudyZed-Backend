from django.shortcuts import render
from rest_framework import generics, exceptions, status
from rest_framework.response import Response
from session_tutor.models import Session
from .serializers import SeeSessionToApproveSerializers, ApproveSessionSerializer
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

# Create your views here.


class AllSessionToApproveView(generics.ListAPIView):
    queryset = Session.objects.filter(is_active=False)
    serializer_class = SeeSessionToApproveSerializers


class ApproveSessionView(generics.UpdateAPIView):
    queryset = Session.objects.all()
    # serializer_class = ApproveSessionSerializer

    def update(self, request, *args, **kwargs):
        session = self.get_object()
        print("GET OBJ :", session, session.is_active)
        session.is_active = True
        print(session.is_active)
        session.save()
        print(session.is_active)
        return Response(
            {
                "message": f"Successfully approved session {session.session_name}",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class AllActiveSessionsView(generics.ListAPIView):
    queryset = Session.objects.filter(is_active=True)
    serializer_class = SeeSessionToApproveSerializers


class AllBlockedSessionsView(generics.ListAPIView):
    queryset = Session.objects.filter(is_active=False)
    serializer_class = SeeSessionToApproveSerializers


class BlockASessionView(generics.UpdateAPIView):
    queryset = Session.objects.filter(is_active=True)

    def update(self, request, *args, **kwargs):
        session = self.get_object()
        print("GET OBJ :", session, session.is_active)
        session.is_active = False
        session.save()
        return Response(
            {
                "message": f"Successfully Blocked session {session.session_name}",
            },
            status=status.HTTP_202_ACCEPTED,
        )
