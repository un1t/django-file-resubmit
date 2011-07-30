# django-file-resubmit

django-file-resubmit is a reusable Django application that keeps selected 
files when forms validation errors occure.

The original idea was developed by team of https://github.com/generalov/django-resubmit.
django-file-resubmit was started to avoid some restrictions of django-resubmit, such as 
supporting last sorl-thumbnail, simplify configuration and integration with a project.



# Requirements
 - sorl-thumbnail, http://thumbnail.sorl.net/

# Configuration 

Add `"file_resubmit"` to `INSTALLED_APPS`.

    INSTALLED_APPS = {
        ...
        'sorl.thumbnail',
        'file_resubmit',
        ...
    }

Default cache is `"file:///tmp/file_resubmit"`, you can setup it manually in settings.py.

    CACHES = {
        'default': {
            ...
        },
        'file_resubmit': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/path/to/cache',
        }
    }

# Examples

## Admin example

    from django.contrib import admin
    from file_resubmit.admin import AdminResubmitMixin
    
    class ModelAdmin(AdminResubmitMixin, ModelAdmin):
        pass
        
## Widgets examples

    from django.forms import ModelForm
    from file_resubmit.admin import AdminResubmitImageWidget, AdminResubmitFileWidget

    class MyModelForm(forms.ModelForm)
    
        class Meta:
            model = MyModel
            widgets = {
                'picture': AdminResubmitImageWidget,
                'file': AdminResubmitFileWidget, 
            }

# Licensing

django-file-resubmit is free software under terms of the MIT License.


**Copyright (C) 2011 by Ilya Shalyapin**, ishalyapin@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.