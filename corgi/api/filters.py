import logging

from django.db.models import Q
from django_filters.rest_framework import CharFilter, Filter, FilterSet

from corgi.core.models import Channel, Component, SoftwareBuild

logger = logging.getLogger(__name__)


class TagFilter(Filter):
    def filter(self, queryset, value):
        # TODO: currently defaults to AND condition, we should make this configurable for both
        # OR and AND conditions.
        if not value:
            return queryset
        search_tags = value.split(",")
        for tag in search_tags:
            if ":" in tag:
                tag_name, _, tag_value = tag.partition(":")
                queryset = queryset.filter(
                    tags__name__icontains=tag_name, tags__value__icontains=tag_value
                )
            else:
                queryset = queryset.filter(tags__name__icontains=tag)
        return queryset


class ComponentFilter(FilterSet):
    """Class that filters queries to Component list views."""

    class Meta:
        model = Component
        # Fields that are matched to a filter using their Django model field type and default
        # __exact lookups.
        fields = ("type", "version", "release", "arch", "nvr", "nevra")

    # Custom filters
    name = CharFilter()
    re_name = CharFilter(lookup_expr="regex", field_name="name")
    re_purl = CharFilter(lookup_expr="regex", field_name="purl")
    description = CharFilter(lookup_expr="icontains")
    tags = TagFilter()

    products = CharFilter(lookup_expr="icontains")
    product_versions = CharFilter(lookup_expr="icontains")
    product_streams = CharFilter(lookup_expr="icontains")
    product_variants = CharFilter(lookup_expr="icontains")
    channels = CharFilter(lookup_expr="icontains")
    sources = CharFilter(lookup_expr="icontains")
    provides = CharFilter(lookup_expr="icontains")
    upstreams = CharFilter(lookup_expr="icontains")
    re_upstream = CharFilter(lookup_expr="regex", field_name="upstreams")

    def filter_ofuri(queryset, name, value):
        query = (
            Q(products__icontains=value)
            | Q(product_versions__icontains=value)
            | Q(product_streams__icontains=value)
        )
        return queryset.filter(query)

    ofuri = CharFilter(method=filter_ofuri)


class ProductDataFilter(FilterSet):
    """Class that filters queries to Product-related list views."""

    name = CharFilter()
    re_name = CharFilter(lookup_expr="regex", field_name="name")
    re_ofuri = CharFilter(lookup_expr="regex", field_name="ofuri")
    tags = TagFilter()

    products = CharFilter(lookup_expr="icontains")
    product_versions = CharFilter(lookup_expr="icontains")
    product_streams = CharFilter(lookup_expr="icontains")
    product_variants = CharFilter(lookup_expr="icontains")
    channels = CharFilter(lookup_expr="icontains")


class ChannelFilter(FilterSet):
    """Class that filters queries to Channel-related list views."""

    name = CharFilter(lookup_expr="icontains")

    class Meta:
        model = Channel
        fields = ("type",)


class SoftwareBuildFilter(FilterSet):
    """Class that filters queries to SoftwareBuild views."""

    name = CharFilter(lookup_expr="icontains")
    tags = TagFilter()

    class Meta:
        model = SoftwareBuild
        fields = ("type",)
