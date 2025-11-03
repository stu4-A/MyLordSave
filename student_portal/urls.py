from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from careers import views as careers_views
from careers.views import CustomLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home page
    path('', careers_views.home_page, name='home'),

    # Careers app URLs
    path('careers/', include('careers.urls')),

    # Custom authentication views
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='login'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
