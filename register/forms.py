from django import forms

from register import models


class HackerForm(forms.ModelForm):
    github = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'https://github.com/johnBiene'}))
    devpost = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'https://devpost.com/JohnBiene'}))
    linkedin = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'https://www.linkedin.com/in/john_biene'}))
    site = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'https://biene.space'}))

    class Meta:
        model = models.Hacker
        labels = {
            'lastname': 'Last name',
        }
        help_texts = {
            'gender': 'This is for demographic purposes. You can skip this question if you want',
            'graduation_year': 'What year have you graduated on or when will you graduate',
            'degree': 'What\'s your major?',
        }
        exclude = ['user']
