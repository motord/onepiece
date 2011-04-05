# -*- coding: utf-8 -*-

from kay.auth.decorators import admin_required
from kay.utils import render_to_response


# Create your views here.
@admin_required
def ide(request):
  return render_to_response('sammy/claim.html', {'subdomain': request.subdomain})
