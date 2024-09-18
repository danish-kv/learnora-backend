from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class CustomMessagePagination(PageNumberPagination):
    page_size = 50
    max_page_size = 100