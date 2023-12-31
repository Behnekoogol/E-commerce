from typing import Any
from django.db import models
from treebeard.mp_tree import MP_Node
from django.utils.translation import gettext_lazy as _


class Category(MP_Node):
    title = models.CharField(verbose_name=_('title'),max_length=255, db_index=True)
    description = models.CharField(max_length=2048, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, allow_unicode=True)


    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'



    def __str__(self):
        return self.title



class OptionGroup(models.Model):
    title = models.CharField(verbose_name=_('title'),max_length=255, db_index=True)
   


    class Meta:
        verbose_name = 'Option Group'
        verbose_name_plural = 'Option Groups'



    def __str__(self):
        return self.title



class OptionGroupValue(models.Model):
    title = models.CharField(verbose_name=_('title'),max_length=255, db_index=True)
    group = models.ForeignKey(OptionGroup, on_delete=models.CASCADE)


    class Meta:
        verbose_name = 'Option Group value'
        verbose_name_plural = 'Option Group values'



    def __str__(self):
        return self.title



class ProductClass(models.Model):
    title = models.CharField(verbose_name=_('title'),max_length=255, db_index=True)
    description = models.CharField(max_length=2048, null=True, blank=True)
    slug = models.SlugField(unique=True, allow_unicode=True)

    track_stock = models.BooleanField(default=True)
    require_shipping = models.BooleanField(default=True)


    option = models.ManyToManyField('Option', blank=True)

    @property
    def has_attribute(self):
        return self.attributes.exists()


    class Meta:
        verbose_name = 'Product Class'
        verbose_name_plural = 'Product Classes'



    def __str__(self):
        return self.title
    





class ProductAttribute(models.Model):

    class AttributeTypeChoice(models.TextChoices):
        text = 'text'
        integer = 'integer'
        float = 'float'
        option = 'option'
        multi_option = 'multi_option'



    product_class = models.ForeignKey(ProductClass, on_delete=models.CASCADE, null=True, related_name='attributes')
    title = models.CharField(max_length=64)
    type = models.CharField(max_length=16, choices=AttributeTypeChoice.choices, default=AttributeTypeChoice.text)
    option_group = models.ForeignKey(OptionGroup, on_delete=models.PROTECT, null=True, blank=True)
    required = models.BooleanField(default=False)
    class Meta:
        verbose_name = 'Product Attribute'
        verbose_name_plural = 'Product Attributes'



    def __str__(self):
        return self.title
    
 



class Option(models.Model):

    class OptionTypeChoice(models.TextChoices):
        text = 'text'
        integer = 'integer'
        float = 'float'
        option = 'option'
        multi_option = 'multi_option'


    title = models.CharField(max_length=64)
    type = models.CharField(max_length=16, choices=OptionTypeChoice.choices, default=OptionTypeChoice.text)
    option_group = models.ForeignKey(OptionGroup, on_delete=models.PROTECT, null=True, blank=True)
    required = models.BooleanField(default=False)
    class Meta:
        verbose_name = 'Option'
        verbose_name_plural = 'Options'



    def __str__(self):
        return self.title
    
 

class Product(models.Model):


    class ProductTypeChoise(models.TextChoices):
        standalone = 'standalone'
        parent = 'parent'
        child = 'child'


    structure = models.CharField(max_length=16, choices=ProductTypeChoise.choices, default=ProductTypeChoise.standalone)
    parent = models.ForeignKey("self", related_name='children', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=128, null=True, blank=True)
    upc = models.CharField(max_length=24, unique=True, null=True, blank=True)
    is_public = models.BooleanField(default=True)

    meta_title = models.CharField(max_length=128, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)


    slug = models.SlugField(unique=True, allow_unicode=True)

    product_class = models.ForeignKey(ProductClass, on_delete=models.PROTECT, null=True, blank=True, related_name='products')
    attributes = models.ManyToManyField(ProductAttribute, through='ProductAttributeValue')
    recomended_products = models.ManyToManyField('catalog.Product', through='ProductRecommendation', blank=True)
    categories = models.ManyToManyField(Category, related_name='categories')

    @property
    def main_image(self):
        if self.images.exists():
            return self.images.first()
        else:
            return None
        
        
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    

    value_text = models.TextField(null=True, blank=True)
    value_integer = models.IntegerField(null=True, blank=True)
    value_float = models.FloatField(null=True, blank=True)
    value_option = models.ForeignKey(OptionGroupValue, on_delete=models.PROTECT, null=True, blank=True)
    value_multi_option = models.ManyToManyField(OptionGroupValue, blank=True, related_name='multi_valued_attribute_value')

    class Meta:
        verbose_name = 'Attribute Value'
        verbose_name_plural = 'Attribute Values'
        unique_together = ('product', 'attribute')




class ProductRecommendation(models.Model):
    primary = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='primary_recommendations')
    recommendation = models.ForeignKey(Product, on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField(default=0)


    class meta():
         unique_together = ('primary', 'recommendation')
         ordering = ('primaty', '-rank')



class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ForeignKey('media.image', on_delete=models.PROTECT)

    display_order = models.PositiveIntegerField(default=0)

    
    class meta:
        ordering = ("display_order", )


    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        for index, image in enumerate(self.product.images.all()):
            image.display_order = index
            image.save()