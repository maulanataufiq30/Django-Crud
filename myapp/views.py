from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Produk
from .forms import ProdukForm

class ProdukListView(ListView):
    model = Produk
    template_name = 'produk_list.html'
    context_object_name = 'produks'

class ProdukCreateView(CreateView):
    model = Produk
    form_class = ProdukForm
    template_name = 'produk_form.html'
    success_url = reverse_lazy('produk_list')

class ProdukUpdateView(UpdateView):
    model = Produk
    form_class = ProdukForm
    template_name = 'produk_form.html'
    success_url = reverse_lazy('produk_list')

class ProdukDeleteView(DeleteView):
    model = Produk
    template_name = 'produk_confirm_delete.html'
    success_url = reverse_lazy('produk_list')