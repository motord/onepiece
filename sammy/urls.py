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
    Rule('/', endpoint='get_content', view='sammy.views.static.get_content'),
    Rule('/claim', endpoint='ide', view='sammy.views.claim.ide'),
    Rule('/admin', endpoint='manage', view='sammy.views.admin.manage'),
  )
]

