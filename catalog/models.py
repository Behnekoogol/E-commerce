from django.db import models
from treebeard.mp_tree import MP_Node
from django.utils.translation import gettext_lazy as _


class Category(MP_Node):
    title = models.CharField(verbose_name=_('title'),max_length=255, db_index=True)
    description = models.CharField(max_length=2048, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    slug = models.SlugField(default='')


    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'



    def __str__(self):
        return self.title
