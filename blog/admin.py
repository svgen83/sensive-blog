from django.contrib import admin
from blog.models import Post, Tag, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at')
    raw_id_fields = ('author', 'likes', 'tags')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass

    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'published_at')
    raw_id_fields = ('author', 'post')
