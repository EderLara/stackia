from django import forms
from .models import Prediccion

class PrediccionForm(forms.ModelForm):
    class Meta:
        model = Prediccion
        fields = ['imagen']
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control', 'type': 'file'}),
        }