from django.conf.urls.defaults import *

from jsonrpc import jsonrpc_site

import account.views
import game.views

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    url(r'^jsonrpc/$', jsonrpc_site.dispatch, name='jsonrpc_mountpoint'),
    ('^$', 'django.views.generic.simple.direct_to_template',
     {'template': 'home.html'}),
)
