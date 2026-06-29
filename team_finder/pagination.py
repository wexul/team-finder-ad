"""Shared pagination helpers."""

from django.core.paginator import Paginator

from .constants import ITEMS_PER_PAGE


def paginate_queryset(request, queryset, per_page=ITEMS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))
