from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from .views import index, api_root

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # API REST
    path('api/endpoints/', api_root, name='api-root'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('accounts.api.urls')),
    path('api/', include('boards.api.urls')),
    path('api/', include('notifications.api.urls')),
    path('api-auth/', include('rest_framework.urls')),

    # Frontend SPA — todas las rutas no-API sirven el index.html
    # El router del lado cliente (History API) maneja: /login, /home, /board/<id>
    re_path(r'^(?!api/(?:token|register|users|boards|lists|cards|notifications|endpoints)|admin/|static/).*$', index, name='index'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
