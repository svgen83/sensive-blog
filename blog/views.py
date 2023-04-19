from django.shortcuts import render, get_object_or_404
from blog.models import Comment, Post, Tag
from django.db.models import Count, Prefetch


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag, post.tags_count) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }



def serialize_tag(tag, tags_count):
    return {
        'title': tag.title,
        'posts_with_tag': tags_count,
    }


def index(request):
    tags_prefetch = Prefetch('tags', queryset=Tag.objects.order_by('title'))

    most_popular_posts = Post.objects.popular().prefetch_related(
        'author', tags_prefetch)[:5].fetch_with_comments_count().fetch_with_tags_count()

    fresh_posts = Post.objects.prefetch_related(
        'author', tags_prefetch).annotate(
        comments_count = Count('comments')
        ).order_by('-published_at').fetch_with_tags_count()

    most_fresh_posts = fresh_posts[:5]
  
    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag, tag.posts_count) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.annotate(likes_count=Count('likes')), slug=slug)
    comments = post.comments.prefetch_related('author')
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.all()

    related_tags = Tag.objects.popular()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag, tag.posts_count) for tag in related_tags],
    }

    most_popular_tags = related_tags[:5]

    most_popular_posts = Post.objects.popular().prefetch_related(
        'author', 'tags')[:5].fetch_with_comments_count().fetch_with_tags_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag, tag.posts_count) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag.objects, title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = Post.objects.popular().prefetch_related(
        'author', 'tags')[:5].fetch_with_comments_count().fetch_with_tags_count()

    related_posts = tag.posts.all().prefetch_related(
        'author', 'tags')[:20].fetch_with_comments_count().fetch_with_tags_count()

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag, tag.posts_count)
                         for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
