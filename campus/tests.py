import shutil
import tempfile

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .admin import LocationAdmin
from .models import Location


class LocationAdminConfigTests(TestCase):
    def setUp(self):
        # Use the registered admin instance so we mirror runtime configuration.
        self.model_admin = admin.site._registry.get(Location) or LocationAdmin(Location, admin.site)

    def test_category_is_filterable_and_editable_inline(self):
        self.assertIn('category', self.model_admin.list_filter)
        self.assertIn('category', self.model_admin.list_editable)

    def test_fieldsets_include_media_and_history_fields(self):
        flattened_fields = []
        for _, options in self.model_admin.fieldsets:
            flattened_fields.extend(options.get('fields', []))

        self.assertIn('historical_info', flattened_fields)
        self.assertIn('photo', flattened_fields)
        self.assertIn('thumbnail', self.model_admin.readonly_fields)

    def test_prepopulated_slug_configuration(self):
        self.assertEqual({'slug': ('name',)}, self.model_admin.prepopulated_fields)


class LocationAdminFlowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media_dir = tempfile.mkdtemp()
        cls._media_override = override_settings(MEDIA_ROOT=cls._media_dir)
        cls._media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._media_override.disable()
        shutil.rmtree(cls._media_dir, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        User = get_user_model()
        self.password = 'StrongPass123!'
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', self.password)
        self.client.login(username=self.admin_user.username, password=self.password)

    def _sample_image(self, name='sample.png'):
        # Minimal 1x1 px PNG.
        image_bytes = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02'
            b'\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        return SimpleUploadedFile(name, image_bytes, content_type='image/png')

    def test_admin_can_create_edit_and_delete_location(self):
        add_url = reverse('admin:campus_location_add')
        initial_photo = self._sample_image('initial.png')
        add_payload = {
            'name': 'Test Tower',
            'description': 'A landmark used for automated testing.',
            'historical_info': 'Constructed to validate admin workflows.',
            'latitude': '33.7775',
            'longitude': '-84.3973',
            'address': '123 Testing Ave',
            'category': 'Academic',
            'image_url': 'https://example.com/test-tower.jpg',
            'photo': initial_photo,
        }
        response = self.client.post(add_url, add_payload, follow=True)
        self.assertEqual(response.status_code, 200)
        location = Location.objects.get(name='Test Tower')
        self.assertTrue(location.slug)
        self.assertTrue(location.photo.name.endswith('initial.png'))

        change_url = reverse('admin:campus_location_change', args=[location.pk])
        updated_photo = self._sample_image('updated.png')
        change_payload = {
            'name': 'Test Tower Updated',
            'slug': location.slug,
            'description': 'Updated description.',
            'historical_info': 'Updated historical note.',
            'latitude': '33.7776',
            'longitude': '-84.3972',
            'address': '456 Updated Rd',
            'category': 'Dining',
            'image_url': 'https://example.com/test-tower-updated.jpg',
            'photo': updated_photo,
        }
        response = self.client.post(change_url, change_payload, follow=True)
        self.assertEqual(response.status_code, 200)
        location.refresh_from_db()
        self.assertEqual(location.name, 'Test Tower Updated')
        self.assertEqual(location.category, 'Dining')
        self.assertTrue(location.photo.name.endswith('updated.png'))

        delete_url = reverse('admin:campus_location_delete', args=[location.pk])
        response = self.client.post(delete_url, {'post': 'yes'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Location.objects.filter(pk=location.pk).exists())
