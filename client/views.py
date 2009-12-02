# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.utils import simplejson
from google.appengine.api import users
from models import *
import random

def _strip_line_breaks(string):
    string = string.replace('\r\n', '')
    string = string.replace('\r', '')
    return string
    
def _normalize_line_breaks(string):
    string = string.replace('\r\n', '\n')
    string = string.replace('\r', '\n')
    return string

def work(request):
    q = Job.all()
    q.filter('map_is_done =', False)
    q.order('priority')
    jobs = q.fetch(5)
    
    if len(jobs) > 0:
        job = random.sample(jobs, 1)[0]
        
        if job.dataobject_set.count() > 0:
            data = random.sample([x for x in job.dataobject_set if not x.is_done], 1)[0] #random data not done
            work_object = {'isGood': True, 'job_id': job.key().id(), 'data_id': data.key().id(), 'exec': _strip_line_breaks(job.map), 'data': data.original_value}
        else:
            work_object = {'isGood': False}
    else:
        work_object = {'isGood': False}
    return HttpResponse(simplejson.dumps(work_object), mimetype='application/json')

def index(request):
    return render_to_response("base.html")
    
def sample(request):
    return render_to_response("sample.html")
    
def wrapper(request, key):
    return render_to_response("wrapper.js", locals())

def engine(request):
    return render_to_response("client.html")
    
def new_job(request):
    if request.method == 'POST':
        form = JobForm(data=request.POST)
        
        if form.is_valid():
            job = form.save(commit=False)
            job.submitted_by = users.get_current_user()
            job.map = _strip_line_breaks(job.map)
            job.reduce = _strip_line_breaks(job.reduce)
            job.data = _normalize_line_breaks(job.data)
            job.put()
            
            for line in job.data.split('\n'):
                data_object = DataObject()
                data_object.job = job
                data_object.original_value = line
                data_object.save()
            
            return HttpResponseRedirect('/job/%s' % job.key().id())
    else:
        form = JobForm()
    return render_to_response("new_job.html", locals())

def view_job(request, key):
    job = Job.get(db.Key.from_path('Job', int(key)))
    return render_to_response("view_job.html", locals())

def submit(request):
    data_id = request.POST['dataId']
    data = DataObject.get(db.Key.from_path('DataObject', int(data_id)))
    data.seconds_to_complete = int(request.POST['timeElapsed'])
    data.processed_value = request.POST['results']
    data.is_done = True
    data.put()
    
    job_id = request.POST['jobId']
    job = Job.get(db.Key.from_path('Job', int(job_id)))
    job.map_is_done = True
    job.reduce_is_done = True
    
    for data_object in job.dataobject_set:
        job.map_is_done = job.map_is_done and data_object.is_done
        
    if job.map_is_done:
        job.result = '\n'.join([d.processed_value for d in job.dataobject_set])
        
    job.put()
    
    status = {'success': True}
    
    return HttpResponse(simplejson.dumps(status), mimetype='application/json')
    
def list_jobs(request):
    jobs = Job.all()
    return render_to_response("list_job.html", locals())
    
