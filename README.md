# Django-Crud
# Dokumentasi Proyek: Website CRUD Sederhana dengan Django dan Docker

## Gambaran Umum
Proyek ini adalah aplikasi web sederhana yang mengimplementasikan operasi CRUD (Create, Read, Update, Delete) menggunakan framework Django. Aplikasi dikemas dalam container Docker untuk memastikan konsistensi lingkungan pengembangan dan memudahkan deployment.

## Fitur Utama
- Operasi CRUD untuk entitas Produk
- Desain responsif dengan Bootstrap 5
- Form otomatis menggunakan django-crispy-forms
- Database PostgreSQL dalam container terpisah
- Konfigurasi Docker untuk pengembangan dan deployment

## Prasyarat
- Docker Desktop terinstal ([Download Docker Desktop](https://www.docker.com/products/docker-desktop))
- Git (opsional)
- Pengetahuan dasar Django dan Docker

## Struktur Proyek
```
django-docker-crud/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── wait-for-it.sh
├── core/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── myapp/
│   ├── migrations/
│   ├── templates/
│   │   ├── base.html
│   │   ├── produk_list.html
│   │   ├── produk_form.html
│   │   └── produk_confirm_delete.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── static/
└── manage.py
```

## Konfigurasi Docker

### Dockerfile
```dockerfile
FROM python:3.9
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install netcat untuk cek koneksi database
RUN apt-get update && apt-get install -y netcat

# Copy script wait-for-it
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Buat direktori untuk static files
RUN mkdir -p /app/staticfiles

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    command: sh -c "/wait-for-it.sh db:5432 -- python manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DEBUG=1

  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myuser -d mydb"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  static_volume:
  postgres_data:
```

### requirements.txt
```
Django==4.2
psycopg2-binary
django-crispy-forms
crispy-bootstrap5
```

### wait-for-it.sh
```bash
#!/bin/sh

host="$1"
port="$2"
shift 2
cmd="$@"

until nc -z $host $port; do
  echo "Waiting for PostgreSQL at $host:$port..."
  sleep 1
done

exec $cmd
```

## Setup Aplikasi Django

### 1. Inisialisasi Proyek
```bash
docker-compose run web django-admin startproject core .
```

### 2. Konfigurasi Database (core/settings.py)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'db',
        'PORT': 5432,
    }
}

# Tambahkan di bagian INSTALLED_APPS
INSTALLED_APPS = [
    ...,
    'myapp',
    'crispy_forms',
    'crispy_bootstrap5',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

### 3. Buat Aplikasi CRUD
```bash
docker-compose run web python manage.py startapp myapp
```

## Model, View, dan Template

### Model (myapp/models.py)
```python
from django.db import models

class Produk(models.Model):
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField()
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama
```

### Form (myapp/forms.py)
```python
from django import forms
from .models import Produk

class ProdukForm(forms.ModelForm):
    class Meta:
        model = Produk
        fields = '__all__'
        widgets = {
            'deskripsi': forms.Textarea(attrs={'rows': 3}),
        }
```

### Views (myapp/views.py)
```python
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
```

### URLs
**core/urls.py**:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
]
```

**myapp/urls.py**:
```python
from django.urls import path
from .views import ProdukListView, ProdukCreateView, ProdukUpdateView, ProdukDeleteView

urlpatterns = [
    path('', ProdukListView.as_view(), name='produk_list'),
    path('tambah/', ProdukCreateView.as_view(), name='produk_create'),
    path('<int:pk>/edit/', ProdukUpdateView.as_view(), name='produk_update'),
    path('<int:pk>/hapus/', ProdukDeleteView.as_view(), name='produk_delete'),
]
```

### Templates
**myapp/templates/base.html**:
```html
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CRUD Produk</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .btn-action { margin: 0 3px; }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="row">
            <div class="col-md-8 mx-auto">
                <div class="card p-4">
                    <h1 class="text-center mb-4 text-primary">🛍️ Manajemen Produk</h1>
                    {% block content %}{% endblock %}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```

**myapp/templates/produk_list.html**:
```html
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<a href="{% url 'produk_create' %}" class="btn btn-success mb-4">+ Tambah Produk</a>

<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>Nama</th>
                <th>Harga</th>
                <th>Tanggal</th>
                <th>Aksi</th>
            </tr>
        </thead>
        <tbody>
            {% for produk in produks %}
            <tr>
                <td>{{ produk.nama }}</td>
                <td>Rp{{ produk.harga }}</td>
                <td>{{ produk.created_at|date:"d M Y" }}</td>
                <td>
                    <a href="{% url 'produk_update' produk.pk %}" class="btn btn-sm btn-warning btn-action">✏️ Edit</a>
                    <a href="{% url 'produk_delete' produk.pk %}" class="btn btn-sm btn-danger btn-action">🗑️ Hapus</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

**myapp/templates/produk_form.html**:
```html
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<h2 class="mb-4">{% if object %}Edit Produk{% else %}Tambah Produk Baru{% endif %}</h2>
<form method="post">
    {% csrf_token %}
    {{ form|crispy }}
    <div class="mt-4">
        <button type="submit" class="btn btn-primary">Simpan</button>
        <a href="{% url 'produk_list' %}" class="btn btn-secondary">Batal</a>
    </div>
</form>
{% endblock %}
```

**myapp/templates/produk_confirm_delete.html**:
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="mb-4">Hapus Produk</h2>
<p>Apakah Anda yakin ingin menghapus produk <strong>{{ object.nama }}</strong>?</p>
<form method="post">
    {% csrf_token %}
    <button type="submit" class="btn btn-danger">Ya, Hapus</button>
    <a href="{% url 'produk_list' %}" class="btn btn-secondary">Batal</a>
</form>
{% endblock %}
```

## Menjalankan Aplikasi

### Langkah-langkah:
1. Clone repositori (jika ada):
   ```bash
   git clone https://github.com/username/django-docker-crud.git
   cd django-docker-crud
   ```

2. Build dan jalankan container:
   ```bash
   docker-compose build
   docker-compose up
   ```

3. Buat migrasi database:
   ```bash
   docker-compose run web python manage.py makemigrations
   docker-compose run web python manage.py migrate
   ```

4. Buat superuser (opsional):
   ```bash
   docker-compose run web python manage.py createsuperuser
   ```

5. Akses aplikasi di browser:
   - Aplikasi utama: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

### Perintah Docker yang Berguna:
- Hentikan aplikasi: `docker-compose down`
- Hentikan dan hapus volume: `docker-compose down -v`
- Lihat log aplikasi: `docker-compose logs web`
- Lihat log database: `docker-compose logs db`
- Masuk ke container: `docker-compose exec web bash`

## Troubleshooting Umum

### 1. Database relation tidak ada
Solusi:
```bash
docker-compose run web python manage.py makemigrations
docker-compose run web python manage.py migrate
```

### 2. Static files tidak muncul
Solusi:
```bash
docker-compose run web python manage.py collectstatic --no-input
```

### 3. Port sudah digunakan
Ganti port di `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"
```

### 4. Aplikasi tidak bisa konek ke database
Pastikan:
- Konfigurasi database di settings.py sesuai
- Service db sudah running
- Script wait-for-it.sh berjalan

### 5. Error saat build Docker
Pastikan:
- File Dockerfile dan requirements.txt valid
- Koneksi internet stabil untuk download dependencies

## Deployment ke Produksi
Untuk deployment ke produksi, lakukan:
1. Set `DEBUG = False` di settings.py
2. Tambahkan domain ke `ALLOWED_HOSTS`
3. Konfigurasi web server (Nginx/Apache) untuk serve static files
4. Gunakan Gunicorn/UWSGI sebagai application server
5. Pertimbangkan untuk menggunakan Docker Swarm atau Kubernetes untuk orchestration

## Fitur Tambahan yang Dapat Dikembangkan
1. Autentikasi pengguna
2. Pencarian dan filter produk
3. Upload gambar produk
4. Paginasi untuk daftar produk
5. API menggunakan Django REST Framework

## Kesimpulan
Proyek ini menunjukkan cara membuat aplikasi web CRUD sederhana dengan Django yang dikemas dalam lingkungan Docker. Dengan konfigurasi ini, pengembangan menjadi lebih konsisten dan deployment lebih mudah. Docker memungkinkan kita untuk memiliki lingkungan yang identik antara pengembangan dan produksi, mengurangi masalah "works on my machine".
