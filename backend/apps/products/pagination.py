from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict

class ProductPagination(PageNumberPagination):
    """
    Custom pagination class for products that supports both grid and list views.
    Provides additional metadata for frontend pagination controls.
    """
    page_size = 12  # Default for grid view
    page_size_query_param = 'page_size'
    max_page_size = 100
    view_mode_param = 'view_mode'

    def get_page_size(self, request):
        """
        Get the page size based on view mode and query parameters.
        Grid view uses 12 items, list view uses 10 items by default.
        """
        view_mode = request.query_params.get(self.view_mode_param, 'grid')
        default_size = 12 if view_mode == 'grid' else 10
        
        if self.page_size_query_param:
            try:
                size = int(request.query_params.get(self.page_size_query_param, default_size))
                return min(size, self.max_page_size)
            except (ValueError, TypeError):
                pass
        return default_size

    def get_paginated_response(self, data):
        """
        Enhanced response with additional pagination metadata.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page_size', self.get_page_size(self.request)),
            ('results', data),
            ('has_next', self.page.has_next()),
            ('has_previous', self.page.has_previous()),
            ('page_range', list(self.page.paginator.get_elided_page_range(
                self.page.number,
                on_each_side=2,
                on_ends=1
            )))
        ]))
