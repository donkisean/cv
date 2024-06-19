import io
from PIL import Image as ImagePIL
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models


DEFAULT_SIZE = getattr(settings, 'DJANGORESIZED_DEFAULT_SIZE', [1000, 800])
DEFAULT_COLOR = (255, 255, 255, 0)


class ResizedImageFieldFile(models.ImageField.attr_class):
    def save(self, name, content, save=True):
        new_content = io.BytesIO()
        content.file.seek(0)
        thumb = ImagePIL.open(content.file)
        thumb.thumbnail((
            self.field.max_width,
            self.field.max_height
        ), ImagePIL.LANCZOS)

        if self.field.use_thumbnail_aspect_ratio:
            img = ImagePIL.new("RGBA", (self.field.max_width,
                               self.field.max_height), self.field.background_color)
            img.paste(thumb, ((self.field.max_width -
                      thumb.size[0]) / 2, (self.field.max_height - thumb.size[1]) / 2))
        else:
            img = thumb

        img.save(new_content, format=thumb.format, **img.info)
        new_content = ContentFile(new_content.getvalue())
        super(ResizedImageFieldFile, self).save(name, new_content, save)


class ResizedImageField(models.ImageField):
    """
    Кастомизированное поле models.ImageField для изменения размеров загружаемых картинок
    """
    attr_class = ResizedImageFieldFile

    def __init__(self, verbose_name=None, name=None, **kwargs):
        self.max_width = kwargs.pop('max_width', DEFAULT_SIZE[0])
        self.max_height = kwargs.pop('max_height', DEFAULT_SIZE[1])
        self.use_thumbnail_aspect_ratio = kwargs.pop(
            'use_thumbnail_aspect_ratio', False)
        self.background_color = kwargs.pop('background_color', DEFAULT_COLOR)
        super(ResizedImageField, self).__init__(verbose_name, name, **kwargs)