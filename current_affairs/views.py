from rest_framework import viewsets, permissions
from .models import DailyDigest
from .serializers import DailyDigestSerializer, DailyDigestAdminSerializer

class DailyDigestViewSet(viewsets.ModelViewSet):
    queryset = DailyDigest.objects.all().order_by('-date_id')
    lookup_field = 'date_id'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DailyDigestAdminSerializer
        return DailyDigestSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]