from django import forms
from .models import Produk

class ProdukForm(forms.ModelForm):
    class Meta:
        model = Produk
        fields = '__all__'
        widgets = {
            'deskripsi': forms.Textarea(attrs={'rows': 3}),
        }