from rest_framework.pagination import CursorPagination, LimitOffsetPagination


# class CursorPaginationWithOrdering(LimitOffsetPagination):
#     default_limit = 8

class CursorPaginationWithOrdering(CursorPagination):
    page_size = 8
    ordering = "created_at"
    