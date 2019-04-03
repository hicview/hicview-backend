from django.urls import path, include
from hicquery import views
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

router = DefaultRouter()
router.register(r'hicqueries', views.HiCQueryViewSet)
#router.register(r'queryfiles', views.query_files)
urlpatterns = [
    path('', include(router.urls)),
]

