from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from AppEticaret.views import *
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", index, name="index"),
    path("profile/", Profile, name="profile"),
    path("category/", Category, name="category"),
    path("basket/", Basket, name="basket"),
    path("product_detail/<int:product_id>", Product_detail, name="product_detail"),

    # Authenticated
    path("login/", Login, name="login"),
    path("register/", Register, name="register"),
    path("logout/", Logout, name="logout"),

] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

urlpatterns = [
    *i18n_patterns(*urlpatterns, prefix_default_language=False),
    path("set_language/<str:language>", set_language, name="set-language"),
]
