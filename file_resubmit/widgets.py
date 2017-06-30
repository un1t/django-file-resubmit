# -*- coding: utf-8 -*-
import os
import uuid

from django import forms
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from django.conf import settings
from django.forms import ClearableFileInput
from django.utils.safestring import mark_safe

from .cache import FileCache

class ResubmitBaseWidget(ClearableFileInput):
    def __init__(self, attrs=None, field_type=None):
        super(ResubmitBaseWidget, self).__init__()
        self.cache_key = ''
        self.field_type = field_type

    def value_from_datadict(self, data, files, name):
        upload = super(ResubmitBaseWidget, self).value_from_datadict(
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


class ResubmitFileWidget(ResubmitBaseWidget):

    def __init__(self, *args, **kwargs):
        super(ResubmitFileWidget, self).__init__(*args, **kwargs)
        try:
            self._template_with_initial = ClearableFileInput.template_with_initial
            self._template_with_clear = ClearableFileInput.template_with_clear
        except AttributeError:
            self._template_with_clear = ''
            self._template_with_initial = ''

    @property
    def template_with_initial(self):
        if hasattr(self, '_template_with_initial'):
            return self._template_with_initial
        else:
            return ''

    @template_with_initial.setter
    def template_with_initial(self, value):
        self._template_with_initial = value

    @property
    def template_with_clear(self):
        if hasattr(self, '_template_with_clear'):
            return self._template_with_clear
        else:
            return ''

    @template_with_clear.setter
    def template_with_clear(self, value):
        self._template_with_clear = value

    def render(self, name, value, attrs=None):
        output = ClearableFileInput.render(self, name, value, attrs)
        output += self.output_extra_data(value)
        return mark_safe(output)


class ResubmitImageWidget(ResubmitFileWidget):
    pass
