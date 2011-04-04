# -*- coding: utf-8 -*-

from kay.utils import render_to_response


# Create your views here.

def index(request):
  return render_to_response('sammy/admin.html', {'message': 'Hello'})
