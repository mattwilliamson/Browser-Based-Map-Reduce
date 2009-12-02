from appengine_django.models import BaseModel
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

default_map = """function(data_row) {
    return parseInt(data_row) * 2;
}"""

default_reduce = """function(data_row, accumulator) {
    return parseInt(accumulator) + parseInt(data_row);
}
"""

default_data = """1
2
3
4
5"""

# Create your models here.
class Job(BaseModel):
    created_at = db.DateTimeProperty(auto_now_add=True)
    submitted_by = db.UserProperty(auto_current_user_add=True)
    name = db.StringProperty()
    map_is_done = db.BooleanProperty(default=False)
    reduce_is_done = db.BooleanProperty(default=False)
    priority = db.IntegerProperty(default=3, choices=[1, 2, 3, 4, 5])
    map = db.TextProperty(default=default_map)
    reduce = db.TextProperty(default=default_reduce)
    data = db.TextProperty(default=default_data)
    result = db.TextProperty(default='')

class DataObject(BaseModel):
    job = db.ReferenceProperty(reference_class=Job)
    is_done = db.BooleanProperty(default=False)
    seconds_to_complete = db.IntegerProperty(default=0)
    original_value = db.TextProperty()
    processed_value = db.TextProperty()
    
class JobForm(djangoforms.ModelForm):
    class Meta:
        model = Job
        exclude = ['submitted_by', 'map_is_done', 'reduce_is_done', 'result']
        