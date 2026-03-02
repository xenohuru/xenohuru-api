"""
URL configuration for cofig project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # API v1 endpoints
    path('api/v1/auth/', include('app.accounts.urls')),
    path('api/v1/regions/', include('app.regions.urls')),
    path('api/v1/attractions/', include('app.attractions.urls')),
    path('api/v1/weather/', include('app.weather.urls')),
    path('api/v1/operators/', include('app.operators.urls')),
    path('api/v1/partners/', include('app.partners.urls')),
    path('api/v1/blog/', include('app.blog.urls')),
    path('api/v1/media/', include('app.media.urls')),
    path('api/v1/contributors/', include('app.contributors.urls')),
    path('api/v1/feedback/', include('app.feedback.urls')),

    # API schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='api-docs'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    
