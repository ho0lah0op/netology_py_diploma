from django import forms


class ImageUploadForm(forms.Form):
    image = forms.ImageField(
        label='Выберите изображение в формате JPG или JPEG'
    )