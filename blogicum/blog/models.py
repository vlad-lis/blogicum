from core.models import PublishedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Category(PublishedModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Title'
    )
    description = models.TextField(verbose_name='Description')
    slug = models.SlugField(
        unique=True,
        verbose_name='id',
        help_text=(
            'id for URL; '
            'Latin letters, numbers, hyphen, and underscore are allowed.'
        )
    )

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(
        max_length=256,
        verbose_name='Location name'
    )

    class Meta:
        verbose_name = 'location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Title'
    )
    text = models.TextField(verbose_name='Text')
    pub_date = models.DateTimeField(
        verbose_name='Time and date of publication',
        help_text=(
            'If you set a date and time in the future, '
            'you can make scheduled publications.'
        )
    )
    image = models.ImageField(
        'Image', upload_to='post_images', blank=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Pulication author'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Location'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Category'
    )

    class Meta:
        verbose_name = 'publication'
        verbose_name_plural = 'Publications'

    def __str__(self):
        return self.title


class Comment(PublishedModel):
    text = models.TextField('Comment text')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'Comments'
        ordering = ('created_at',)
