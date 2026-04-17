from django.urls import path

from rest_framework.routers import DefaultRouter

from api.viewsets import UserViewSet, StudentViewSet


router = DefaultRouter()

router.register(prefix="users", viewset=UserViewSet, basename="users")
router.register(prefix="students", viewset=StudentViewSet, basename="students")

urlpatterns = [] + router.urls
