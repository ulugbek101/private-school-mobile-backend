from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated


class PaginationMixin:
    def paginate_queryset(self, queryset):
        """
        Method to disable pagination if .../?all=true is passed as a GET parameter
        """

        all = self.request.query_params.get("all") == "true"
        if all:
            return None

        return super().paginate_queryset(queryset)


class SearchMixin:
    # .../?search=...
    filter_backends = [SearchFilter]
    search_fields = []


class AuthenticationMixin:
    # permission_classes = [IsAuthenticated]
    ...