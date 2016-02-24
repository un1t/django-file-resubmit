# -*- coding: utf-8 -*-
import os
import uuid

from django import forms
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from django.db import models
from django.utils.safestring import mark_safe

try:
    from sorl.thumbnail.fields import ImageField
    from sorl.thumbnail.admin.current import AdminImageWidget as BaseWidget
except ImportError:
    from django.forms import ImageField
    from django.contrib.admin.widgets import AdminFileWidget as BaseWidget

from file_resubmit.cache import FileCache


class AdminResubmitBaseWidget(BaseWidget):
    def __init__(self, attrs=None, field_type=None):
        super(AdminResubmitBaseWidget, self).__init__()
        self.cache_key = ''
        self.field_type = field_type

    def value_from_datadict(self, data, files, name):
        upload = super(AdminResubmitBaseWidget, self).value_from_datadict(
            data, files, name)
        if upload == FILE_INPUT_CONTRADICTION:
            return upload

        self.input_name = "%s_cache_key" % name
        self.cache_key = data.get(self.input_name, "")

        if name in files:
            self.cache_key = self.random_key()[:10]
            upload = files[name]
            FileCache().set(self.cache_key, upload)
        elif self.cache_key:
            restored = FileCache().get(self.cache_key, name)
            if restored:
                upload = restored
                files[name] = upload
        return upload

    def random_key(self):
        return uuid.uuid4().hex

    def output_extra_data(self, value):
        output = ''
        if value and self.cache_key:
            output += ' ' + self.filename_from_value(value)
        if self.cache_key:
            output += forms.HiddenInput().render(
                self.input_name,
                self.cache_key,
                {},
            )
        return output

    def filename_from_value(self, value):
        if value:
            return os.path.split(value.name)[-1]


class AdminResubmitFileWidget(AdminResubmitBaseWidget):
    def render(self, name, value, attrs=None):
        output = super(AdminResubmitFileWidget, self).render(
            name, value, attrs)
        output += self.output_extra_data(value)
        return mark_safe(output)


class AdminResubmitImageWidget(AdminResubmitFileWidget):
    pass


class AdminResubmitMixin(object):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, ImageField):
            return db_field.formfield(widget=AdminResubmitImageWidget)
        elif isinstance(db_field, models.FileField):
            return db_field.formfield(widget=AdminResubmitFileWidget)
        else:
            return super(AdminResubmitMixin, self).formfield_for_dbfield(
                db_field, **kwargs)
