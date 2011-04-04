# -*- coding: utf-8 -*-

import logging
import datetime

from werkzeug import Headers, Response, redirect
from werkzeug.exceptions import NotFound
from kay.utils import render_to_response
from sammy.models import StaticContent

HTTP_DATE_FMT = "%a, %d %b %Y %H:%M:%S GMT"

def _output(content, serve=True):
    """Output the content in the datastore as a HTTP Response"""
    headers = Headers()
    if content.content_type:
        headers['Content-Type'] = content.content_type
    last_modified = content.last_modified.strftime(HTTP_DATE_FMT)
    headers.add('Last-Modified', last_modified)
    for header in content.headers:
        key, value = header.split(':', 1)
        headers[key] = value.strip()
    if serve:
        response = Response(content.body, content_type=content.content_type,
                    headers=headers, status=content.status)
    else:
        response = Response(status=304)
    return response

def get_content(request, path=''):
    """Get content from datastore as requested on the url path

    Args:
        path - comes without leading slash. / added in code

    """
    content = StaticContent.get_latest(request.subdomain, "/%s" % path)
    if not content:
        raise NotFound

    serve = True
    # check modifications and etag
    if 'If-Modified-Since' in request.headers:
        last_seen = datetime.datetime.strptime(
            request.headers['If-Modified-Since'], HTTP_DATE_FMT)
        if last_seen >= content.last_modified.replace(microsecond=0):
            serve = False
    response = _output(content, serve)
    return response
