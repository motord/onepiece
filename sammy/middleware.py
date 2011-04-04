# -*- coding: utf-8 -*-

import logging
from kay.utils import render_to_response
from sammy.models import Subdomain

class SubdomainMiddleware(object):
  def process_request(self, request):
      """Determines the subdomain of the request."""

      # The 'subdomain' query parameter always overrides the hostname.
      try:
          if request.form['subdomain']:
              request.subdomain=request.form['subdomain']
              return None
          if request.args['subdomain']:
              request.subdomain=request.args['subdomain']
              return None
      except KeyError:
          pass

      levels = request.headers['Host'].split('.')
      if levels[-2:] == ['appspot', 'com'] and len(levels) >= 4:
          # foo.person-finder.appspot.com -> subdomain 'foo'
          # bar.kpy.latest.person-finder.appspot.com -> subdomain 'bar'
          logging.info(levels[0])
          request.subdomain=levels[0]
          return None

      return render_to_response('sammy/basecamp.html', {'subdomains': Subdomain.all()})


