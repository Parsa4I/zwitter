from django import template

register = template.Library()


def is_liked(post, user):
    return post.is_liked(user)


register.filter("is_liked", is_liked)
