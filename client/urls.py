from django.conf.urls.defaults import *

import client.views

urlpatterns = patterns('client.views',
    (r'^work', 'work'),
    (r'^sample', 'sample'),
    (r'^wrapper/(?P<key>.*)', 'wrapper'),
    (r'^engine', 'engine'),
    (r'^submit', 'submit'),
)