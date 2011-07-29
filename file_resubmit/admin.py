# -*- coding: utf-8 -*-
import os
import hashlib  
import random
import time
 
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

from sorl.thumbnail.fields import ImageField
from sorl.thumbnail.admin.current import AdminImageWidget

from file_resubmit.models import FileStorage


def random_key():
    x = "%s%s%s" % (settings.SECRET_KEY, time.time(), random.random())
    random.seed(x)
    return hashlib.md5(str(random.random())).hexdigest()


class AdminResubmitWidget(AdminImageWidget):
    
    def __init__(self, attrs=None):
        super(AdminResubmitWidget, self).__init__()
        self.cache_key = '' 
    
    def render(self, name, value, attrs=None):
        output = super(AdminResubmitWidget, self).render(name, value, attrs)
        if self.cache_key:
            output += forms.HiddenInput().render(self.input_name, self.cache_key, {})
            if value:
                output += ' ' + os.path.split(value.name)[-1]
        return mark_safe(output)

    def value_from_datadict(self, data, files, name):
        upload = super(AdminResubmitWidget, self).value_from_datadict(data, files, name)
        self.input_name = "%s_cache_key" % name
        self.cache_key = data.get(self.input_name, "")
        
        if files.has_key(name):
            self.cache_key = random_key()[:7]
            upload = files[name]
            upload.file.seek(0)
            FileStorage().put(self.cache_key, upload)
            upload.file.seek(0)
        elif self.cache_key:
            restored = FileStorage().get(self.cache_key, name)
            if restored:
                upload = restored
                files[name] = upload
                upload.file.seek(0)
        return upload
    
    
class AdminResubmitMixin(object):
    """
    This is a mix-in for InlineModelAdmin subclasses to make ``ImageField``
    show nicer form widget
    """
    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, ImageField):
            return db_field.formfield(widget=AdminResubmitWidget)
        sup = super(AdminResubmitMixin, self)
        return sup.formfield_for_dbfield(db_field, **kwargs)