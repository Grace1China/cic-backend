from __future__ import absolute_import

import os

from django.conf import settings
from django.core.management.base import BaseCommand

from ckeditor_uploader.backends import registry
from ckeditor_uploader.utils import get_thumb_filename
from ckeditor_uploader.views import get_image_files


class Command(BaseCommand):
    """
    Creates thumbnail files for the CKEditor file image browser.
    Useful if starting to use django-ckeditor with existing images.
    """
    def handle(self, *args, **options):
        if getattr(settings, 'CKEDITOR_IMAGE_BACKEND', None):
            backend = registry.get_backend()
            for tp in get_image_files():
                if not tp['isdir'] and not self._thumbnail_exists(tp['name']):
                    self.stdout.write("Creating thumbnail for %s" % tp['name'])
                    try:
                        backend.create_thumbnail(tp['name'])
                    except Exception as e:
                        self.stdout.write("Couldn't create thumbnail for %s: %s" % (tp['name'], e))
            self.stdout.write("Finished")
        else:
            self.stdout.write("No thumbnail backend is enabled")

    def _thumbnail_exists(self, image_path):
        thumb_path = self._to_absolute_path(
            get_thumb_filename(image_path)
        )
        return os.path.isfile(thumb_path)

    @staticmethod
    def _to_absolute_path(image_path):
        return os.path.join(settings.MEDIA_ROOT, image_path)
