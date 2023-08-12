from django import forms
from .models import Post
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


class CreatePostForm(forms.Form):
    body = forms.CharField(max_length=4000, widget=forms.Textarea, required=True)
    tags = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "separate with commas"}),
    )


class AttachPictureForm(forms.Form):
    image = forms.ImageField()


class AttachVideoForm(forms.Form):
    video = forms.FileField(
        validators=[FileExtensionValidator(["MOV", "avi", "mp4", "webm", "mkv"])]
    )


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "user",
            "body",
            "post_type",
            "image",
            "video",
            "tags",
            "root",
            "reposted_from",
        )

    def clean(self):
        cd = self.cleaned_data
        if not (cd["image"] and cd["video"]):
            return cd
        raise ValidationError("A post can't have 2 media files at the same time.")


class SearchForm(forms.Form):
    q = forms.CharField(max_length=4000, required=False, label="")
