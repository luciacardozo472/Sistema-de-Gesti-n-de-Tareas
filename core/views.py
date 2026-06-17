from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse


def index(request):
    return render(request, 'index.html')


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        'auth': {
            'login (obtener token)': reverse('token_obtain_pair', request=request, format=format),
            'refresh token': reverse('token_refresh', request=request, format=format),
            'register (solo admin)': reverse('register', request=request, format=format),
        },
        'users': {
            'lista de usuarios': reverse('user-list', request=request, format=format),
            'usuario actual': reverse('user-me', request=request, format=format),
        },
        'boards': reverse('board-list', request=request, format=format),
        'lists': reverse('list-list', request=request, format=format),
        'cards': reverse('card-list', request=request, format=format),
        'notifications': reverse('notification-list', request=request, format=format),
    })