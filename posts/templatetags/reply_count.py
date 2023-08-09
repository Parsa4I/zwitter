from django import template


register = template.Library()


def reply_count(post):
    return post.replies.count()


register.filter("reply_count", reply_count)
