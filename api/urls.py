from django.urls import path

from rest_framework.routers import DefaultRouter

from api.viewsets import UserViewSet, StudentViewSet, ClassViewSet


router = DefaultRouter()

router.register(prefix="users", viewset=UserViewSet, basename="users")
router.register(prefix="students", viewset=StudentViewSet, basename="students")
router.register(prefix="classes", viewset=ClassViewSet, basename="classes")

urlpatterns = [] + router.urls
