# -*- coding: utf-8 -*-
import os
import hashlib  
import random
import time
 
from django import forms
from django.conf import settings
from django.db import models
from django.forms import ClearableFileInput
from django.utils.safestring import mark_safe

from sorl.thumbnail.fields import ImageField
from sorl.thumbnail.admin.current import AdminImageWidget

from file_resubmit.models import FileCache


class AdminResubmitBaseWidget(AdminImageWidget):
    
    def __init__(self, attrs=None, field_type=None):
        super(AdminResubmitBaseWidget, self).__init__()
        self.cache_key = '' 
        self.field_type = field_type

    def value_from_datadict(self, data, files, name):
        upload = super(AdminResubmitBaseWidget, self).value_from_datadict(data, files, name)
        self.input_name = "%s_cache_key" % name
        self.cache_key = data.get(self.input_name, "")
        
        if files.has_key(name):
            self.cache_key = self.random_key()[:10]
            upload = files[name]
            FileCache().put(self.cache_key, upload)
        elif self.cache_key:
            restored = FileCache().get(self.cache_key, name)
            if restored:
                upload = restored
                files[name] = upload
        return upload
    
    def random_key(self):
        x = "%s%s%s" % (settings.SECRET_KEY, time.time(), random.random())
        random.seed(x)
        return hashlib.md5(str(random.random())).hexdigest()
    
    def output_extra_data(self, value):
        output = ''
        if value and self.cache_key:
            output += ' ' + self.filename_from_value(value)
        if self.cache_key:
            output += forms.HiddenInput().render(self.input_name, self.cache_key, {})
        return output
    
    def filename_from_value(self, value):
        if value: 
            return os.path.split(value.name)[-1]
        
    
class AdminResubmitFileWidget(AdminResubmitBaseWidget):
    template_with_initial = ClearableFileInput.template_with_initial
    template_with_clear = ClearableFileInput.template_with_clear
    
    def render(self, name, value, attrs=None):
        output = ClearableFileInput.render(self, name, value, attrs)
        output += self.output_extra_data(value)
        return mark_safe(output)


class AdminResubmitImageWidget(AdminResubmitBaseWidget):

    def render(self, name, value, attrs=None):
        output = super(AdminResubmitImageWidget, self).render(name, value, attrs)
        output += self.output_extra_data(value)
        return mark_safe(output)


class AdminResubmitMixin(object):

    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, ImageField):
            return db_field.formfield(widget=AdminResubmitImageWidget)
        elif isinstance(db_field, models.FileField):
            return db_field.formfield(widget=AdminResubmitFileWidget)
        sup = super(AdminResubmitMixin, self)
        return sup.formfield_for_dbfield(db_field, **kwargs)