from django import template


register = template.Library()


def like_count(post):
    return post.likes.count()


register.filter("like_count", like_count)
