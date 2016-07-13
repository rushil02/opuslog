"""
Content negotiation deals with selecting an appropriate renderer given the
incoming request. This is to override the default content negotiation method.
Content requests from client will be ignored instead only server content will be enforced.
"""

from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.settings import api_settings
from rest_framework.utils.mediatypes import media_type_matches
from django.http import Http404
from rest_framework import exceptions
from django.conf import settings


class IgnoreClientContentNegotiation(BaseContentNegotiation):
    settings = api_settings

    def select_parser(self, request, parsers):
        """
        Given a list of parsers and a media type, return the appropriate
        parser to handle the incoming request.
        """
        for parser in parsers:
            if media_type_matches(parser.media_type, request.content_type):
                return parser
        return None

    def select_renderer(self, request, renderers, format_suffix=None):
        """
        Select the first renderer in the `.renderer_classes` list.
        """
        # Allow URL style format override.  eg. "?format=json
        if settings.DEBUG:
            format_query_param = self.settings.URL_FORMAT_OVERRIDE
            format = format_suffix or request.query_params.get(format_query_param)
            if format:
                renderers = self.filter_renderers(renderers, format)
                for renderer in renderers:
                    if type(renderer) in self.settings.DEFAULT_RENDERER_CLASSES:
                        return renderer, renderer.media_type
                raise exceptions.NotAcceptable(available_renderers=renderers)

        return renderers[0], renderers[0].media_type

    def filter_renderers(self, renderers, format):
        """
        If there is a '.json' style format suffix, filter the renderers
        so that we only negotiation against those that accept that format.
        """
        renderers = [renderer for renderer in renderers
                     if renderer.format == format]
        if not renderers:
            raise Http404
        return renderers
