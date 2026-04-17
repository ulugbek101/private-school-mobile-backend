from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class TokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['middle_name'] = user.middle_name
        token['email'] = user.email
        token['phone_number'] = f'{user.phone_number}'
        token['role'] = user.role
        token['is_superuser'] = user.is_superuser
        token['is_staff'] = user.is_staff
        token['is_active'] = user.is_active
        token['created'] = user.created.isoformat()
        token['updated'] = user.updated.isoformat()

        return token
