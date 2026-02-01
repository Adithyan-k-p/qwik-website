from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # fields = ['caption', 'media_url', 'post_type', 'media_type']
        fields = ['caption', 'image', 'post_type', 'media_type']
        
        widgets = {
            'caption': forms.Textarea(attrs={
                'class': 'caption-input', 
                'placeholder': 'Write a caption...',
                'rows': 3,
                'required': True
            }),
            # 'media_url': forms.TextInput(attrs={
            #     'class': 'url-input', 
            #     'placeholder': 'Paste image URL here...',
            #     'id': 'imgUrlInput'
            # }),

            'image': forms.FileInput(attrs={
                'class': 'file-input', 
                'id': 'fileInput',
                'style': 'display: none;',
                'required': True,
            }),

            # We use RadioSelect for better UI styling (Buttons instead of dropdown)
            'post_type': forms.RadioSelect(attrs={'class': 'type-radio'}),
            'media_type': forms.HiddenInput(), # Hidden because we force it to 'image'
            'visibility': forms.RadioSelect(attrs={'class': 'type-radio'}),
        }