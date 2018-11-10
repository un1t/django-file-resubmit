try:
    from unittest import mock
except ImportError:
    try:
        import mock
    except ImportError:
        mock = None

import os
import tempfile

from django import forms
from django.contrib.admin.sites import AdminSite
from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.test import TestCase, RequestFactory
from django.views.generic import FormView

from file_resubmit import widgets
from file_resubmit import admin

if not mock:
    raise ImproperlyConfigured("For testing mock is required.")


# shortest possible PNG file, courtesy http://garethrees.org/2007/11/14/pngcrush/
PNG = (
    b'\x89PNG\r\n\x1a\n'
    b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
    b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4'
    b'\x00\x00\x00\x00IEND\xaeB`\x82'
)


class TestForm(forms.Form):
    pass


class OneFileForm(forms.Form):
    name = forms.CharField(required=True)
    upload_file = forms.FileField(widget=widgets.ResubmitFileWidget())


class OneImageForm(forms.Form):
    name = forms.CharField(required=True)
    upload_image = forms.ImageField(widget=widgets.ResubmitImageWidget())


class BaseResubmitFileMixin(object):
    def setUp(self):
        self.factory = RequestFactory()
        self.temporary_file = tempfile.NamedTemporaryFile(delete=False)
        self.temporary_content = os.urandom(1024)
        self.temporary_file.write(self.temporary_content)
        self.temporary_file.close()
        self.temporary_image = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        self.temporary_image.write(PNG)
        self.temporary_image.close()
        
    def get_resubmit_field(self, form, field_name):
        resubmit_field_name = '{fn}_cache_key'.format(fn=field_name)
        name_prefix='name="{rfn}"'.format(rfn=resubmit_field_name)
        value_prefix='value="'
        rendered = str(form[field_name])
        self.assertIn(name_prefix, rendered)
        name_prefix_idx = rendered.index(name_prefix)
        value_idx = rendered.index(value_prefix, name_prefix_idx)
        value_close_idx = rendered.index('"', value_idx + len(value_prefix))
        value = rendered[value_idx + len(value_prefix):value_close_idx]
        return resubmit_field_name, value


class TestResubmitFileWidget(BaseResubmitFileMixin, TestCase):
    class DummyFormView(FormView):
        template_name = 'blank.html'  # TemplateView requires this attribute
        form_class = TestForm
        success_url = '/done/'

    class OneFileView(DummyFormView):
        form_class = OneFileForm

    class OneImageView(DummyFormView):
        form_class = OneImageForm

    def test_file_widget(self):
        request = self.factory.get('/example/')
        response = self.OneFileView.as_view()(request)
        form = response.context_data['form']
        file_field = form.fields.get('upload_file')
        self.assertIsInstance(file_field.widget, widgets.ResubmitFileWidget)

    def test_file_resubmit(self):
        data = {}
        with open(self.temporary_file.name, 'rb') as fo:
            request = self.factory.post('/example/', {'upload_file': fo})
        response = self.OneFileView.as_view()(request)
        form = response.context_data['form']
        self.assertEqual(len(form.errors), 1)
        resubmit_field, resubmit_value = self.get_resubmit_field(form, 'upload_file')
        data = {
            resubmit_field: resubmit_value
        }
        resubmit_req = self.factory.post('/example/', data)
        resubmit_resp = self.OneFileView.as_view()(resubmit_req)
        form = resubmit_resp.context_data['form']
        uploaded_file = form.cleaned_data['upload_file']
        self.assertEqual(uploaded_file.read(), self.temporary_content)
        
    def test_image_widget(self):
        request = self.factory.get('/example/')
        response = self.OneImageView.as_view()(request)
        form = response.context_data['form']
        image_field = form.fields.get('upload_image')
        self.assertIsInstance(image_field.widget, widgets.ResubmitImageWidget)

    def test_image_resubmit(self):
        data = {}
        with open(self.temporary_image.name, 'rb') as fo:
            request = self.factory.post('/example/', {'upload_image': fo})
        response = self.OneImageView.as_view()(request)
        form = response.context_data['form']
        self.assertEqual(len(form.errors), 1)
        resubmit_field, resubmit_value = self.get_resubmit_field(form, 'upload_image')
        data = {
            resubmit_field: resubmit_value
        }
        resubmit_req = self.factory.post('/example/', data)
        resubmit_resp = self.OneImageView.as_view()(resubmit_req)
        form = resubmit_resp.context_data['form']
        uploaded_image = form.cleaned_data['upload_image']
        self.assertEqual(uploaded_image.read(), PNG)


class TestModel(models.Model):
    """
    I skip the step of saving the model to the database
    """
    def save_base(*args, **kwargs):
        pass
    
    class Meta:
        abstract = True


class TestModelAdmin(ModelAdmin):
    """
    Instead of returning with a redirect to the change
    list page, I just return the saved object
    """
    def response_add(self, request, obj, *args, **kwargs):
        return obj


class TestResubmitAdminWidget(BaseResubmitFileMixin, TestCase):
    class TestFileModel(TestModel):
        admin_name = models.CharField(max_length=100, blank=False)
        admin_upload_file = models.FileField(upload_to="fake/")

    class TestImageModel(TestModel):
        admin_name = models.CharField(max_length=100, blank=False)
        admin_upload_image = models.ImageField(upload_to="fake/")

    class TestFileAdmin(admin.AdminResubmitMixin, TestModelAdmin):
        pass

    class TestImageAdmin(admin.AdminResubmitMixin, TestModelAdmin):
        pass

    def setUp(self):
        super(TestResubmitAdminWidget, self).setUp()
        User = get_user_model()
        self.user = User.objects.create_superuser(
            'TestUser',
            'testuser@example.com',
            '12345678'
        )

    def test_file_admin(self):
        testadmin = self.TestFileAdmin(model=self.TestFileModel, admin_site=AdminSite())
        request = self.factory.get('/admin/example/')
        request.user = self.user
        response = testadmin.add_view(request)
        file_field = response.context_data['adminform'].form.fields.get('admin_upload_file')
        self.assertIsInstance(file_field.widget, admin.AdminResubmitFileWidget)

    def test_image_admin(self):
        testadmin = self.TestImageAdmin(model=self.TestImageModel, admin_site=AdminSite())
        request = self.factory.get('/admin/example/')
        request.user = self.user
        response = testadmin.add_view(request)
        image_field = response.context_data['adminform'].form.fields.get('admin_upload_image')
        self.assertIsInstance(image_field.widget, admin.AdminResubmitImageWidget)

    def test_image_resubmit_admin(self):
        testadmin = self.TestImageAdmin(model=self.TestImageModel, admin_site=AdminSite())
        with open(self.temporary_image.name, 'rb') as fo:
            request = self.factory.post('/admin/example/', {'admin_upload_image': fo})
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = testadmin.add_view(request)
        form = response.context_data['adminform'].form
        resubmit_field, resubmit_value = self.get_resubmit_field(form, 'admin_upload_image')
        data = {
            resubmit_field: resubmit_value
        }
        resubmit_req = self.factory.post('/admin/example/', data)
        resubmit_req.user = self.user
        resubmit_req._dont_enforce_csrf_checks = True
        resubmit_resp = testadmin.add_view(resubmit_req)
        form = resubmit_resp.context_data['adminform'].form
        self.assertEqual(len(form.errors), 1)
        uploaded_image = form.cleaned_data['admin_upload_image']
        self.assertEqual(uploaded_image.read(), PNG)

    def test_file_resubmit_admin(self):
        testadmin = self.TestFileAdmin(model=self.TestFileModel, admin_site=AdminSite())
        with open(self.temporary_file.name, 'rb') as fo:
            request = self.factory.post('/admin/example/', {'admin_upload_file': fo})
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = testadmin.add_view(request)
        form = response.context_data['adminform'].form
        resubmit_field, resubmit_value = self.get_resubmit_field(form, 'admin_upload_file')
        data = {
            resubmit_field: resubmit_value
        }
        resubmit_req = self.factory.post('/admin/example/', data)
        resubmit_req.user = self.user
        resubmit_req._dont_enforce_csrf_checks = True
        resubmit_resp = testadmin.add_view(resubmit_req)
        form = resubmit_resp.context_data['adminform'].form
        print("\n".join(str(err) for err in form.errors.items()))
        self.assertEqual(len(form.errors), 1)
        uploaded_file = form.cleaned_data['admin_upload_file']
        self.assertEqual(uploaded_file.read(), self.temporary_content)

    def test_image_resubmit_save_admin(self):
        testadmin = self.TestImageAdmin(model=self.TestImageModel, admin_site=AdminSite())
        with open(self.temporary_image.name, 'rb') as fo:
            request = self.factory.post('/admin/example/', {'admin_upload_image': fo})
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = testadmin.add_view(request)
        form = response.context_data['adminform'].form
        resubmit_field, resubmit_value = self.get_resubmit_field(form, 'admin_upload_image')
        data = {
            'admin_name': "Sample",
            resubmit_field: resubmit_value
        }
        resubmit_req = self.factory.post('/admin/example/', data)
        setattr(resubmit_req, 'session', 'session')
        messages = FallbackStorage(resubmit_req)
        setattr(resubmit_req, '_messages', messages)
        resubmit_req.user = self.user
        resubmit_req._dont_enforce_csrf_checks = True
        saved_obj = testadmin.add_view(resubmit_req)
        self.assertEqual(saved_obj.admin_upload_image.read(), PNG)

    def test_file_resubmit_save_admin(self):
        testadmin = self.TestFileAdmin(model=self.TestFileModel, admin_site=AdminSite())
        with open(self.temporary_file.name, 'rb') as fo:
            request = self.factory.post('/admin/example/', {'admin_upload_file': fo})
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = testadmin.add_view(request)
        form = response.context_data['adminform'].form
        resubmit_field, resubmit_value = self.get_resubmit_field(form, 'admin_upload_file')
        data = {
            'admin_name': "Sample",
            resubmit_field: resubmit_value
        }
        resubmit_req = self.factory.post('/admin/example/', data)
        setattr(resubmit_req, 'session', 'session')
        messages = FallbackStorage(resubmit_req)
        setattr(resubmit_req, '_messages', messages)
        resubmit_req.user = self.user
        resubmit_req._dont_enforce_csrf_checks = True
        saved_obj = testadmin.add_view(resubmit_req)
        self.assertEqual(saved_obj.admin_upload_file.read(), self.temporary_content)
