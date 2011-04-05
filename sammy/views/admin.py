# -*- coding: utf-8 -*-

from kay.auth.decorators import admin_required
from kay.utils import render_to_response


# Create your views here.
@admin_required
def manage(request):
  return render_to_response('sammy/admin.html', {'subdomain': request.subdomain})
