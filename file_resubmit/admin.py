# -*- coding: utf-8 -*-

from django.db import models
from django.forms import ClearableFileInput
from django.utils.safestring import mark_safe

try:
    from sorl.thumbnail.fields import ImageField
    from sorl.thumbnail.admin.current import AdminImageWidget as BaseWidget
except ImportError:
    from django.forms import ImageField
    from django.contrib.admin.widgets import AdminFileWidget as BaseWidget

from .widgets import ResubmitBaseWidget, ResubmitFileWidget


class AdminResubmitBaseWidget(ResubmitBaseWidget, BaseWidget):
    pass


class AdminResubmitFileWidget(ResubmitFileWidget):
    pass


class AdminResubmitImageWidget(AdminResubmitBaseWidget):
    def render(self, name, value, renderer=None, attrs=None):
        output = super(AdminResubmitImageWidget, self).render(
            name, value, attrs)
        output += self.output_extra_data(value)
        return mark_safe(output)


class AdminResubmitMixin(object):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, (ImageField, models.ImageField)):
            return db_field.formfield(widget=AdminResubmitImageWidget)
        elif isinstance(db_field, models.FileField):
            return db_field.formfield(widget=AdminResubmitFileWidget)
        else:
            return super(AdminResubmitMixin, self).formfield_for_dbfield(
                db_field, **kwargs)
