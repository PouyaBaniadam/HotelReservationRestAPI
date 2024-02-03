from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from HotelReservationRestAPI import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('hotel/', include('reservation.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
