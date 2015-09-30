from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# from markdown import
# Create your models here.

class VisualModel(models.Model):
    title = models.CharField(max_length=50)
    tag_line = models.CharField(max_length=100)
    text_body = models.TextField()
    url = models.URLField(blank=False, null=False, default='http://localhost:8000/')

    @python_2_unicode_compatible
    def __str__(self):
        return self.title

    class Meta:
        abstract = True

class HomePage(VisualModel):
    home_image = models.ImageField('HomePage Image',
                                    upload_to='homepage_pics/%Y-%m-%d/',
                                    blank=True,
                                    null=True)



class AboutPage(VisualModel):
    about_image = models.ImageField('AboutPage Iamge',
                                    upload_to='aboutpage_pics/%Y-%m-%d/',
                                    blank=True,
                                    null=True)

