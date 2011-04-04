# -*- coding: utf-8 -*-
# sammy.urls
# 

# Following few lines is an example urlmapping with an older interface.
"""
from werkzeug.routing import EndpointPrefix, Rule

def make_rules():
  return [
    EndpointPrefix('sammy/', [
      Rule('/', endpoint='index'),
    ]),
  ]

all_views = {
  'sammy/index': 'sammy.views.index',
}
"""

from kay.routing import (
  ViewGroup, Rule
)

view_groups = [
  ViewGroup(
    Rule('/', endpoint='index', view='sammy.views.static.index'),
    Rule('/admin', endpoint='admin', view='sammy.views.admin.index'),
  )
]

