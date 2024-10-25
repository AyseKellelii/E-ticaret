from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from urllib.parse import urlparse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls.base import resolve, reverse
from django.urls.exceptions import Resolver404
from django.utils import translation
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.db.models import Q
from django.core.paginator import Paginator


def ProductQuentity(request):
    if request.user.is_authenticated:
        return BasketProduct.objects.filter(user=request.user)
    else:
        return None


def index(request):
    products = Product.objects.all()

    context = {

        "products": products,
        "product_quantity": ProductQuentity(request)
    }

    return render(request, 'index.html', context)


def Category(request):
    products = Product.objects.all()
    brands = Brand.objects.all()
    gender = Gender.objects.all()
    color = Color.objects.all()
    case_shapes = CaseShape.objects.all()
    strap_types = StrapType.objects.all()
    glass_features = GlassFeature.objects.all()
    styles = Style.objects.all()
    mechanism = Mechanism.objects.all()

    filters = Q()

    if "marka" in request.GET:
        markalar = request.GET.getlist("marka")
        for marka in markalar:
            filters |= Q(brand=marka)

    if "cinsiyet" in request.GET:
        filters &= Q(gender=request.GET.get("cinsiyet"))

    if "renk" in request.GET:
        renkler = request.GET.getlist("renk")
        for renk in renkler:
            filters |= Q(color=renk)

    if "kasa_sekli" in request.GET:
        kasa_sekilleri = request.GET.getlist("kasa_sekli")
        for kasa_sekli in kasa_sekilleri:
            filters |= Q(case_shape=kasa_sekli)

    if "kayis_tipi" in request.GET:
        kayis_tipleri = request.GET.getlist("kayis_tipi")
        for kayis_tipi in kayis_tipleri:
            filters |= Q(strap_type=kayis_tipi)

    if "cam_ozellik" in request.GET:
        cam_ozellikleri = request.GET.getlist("cam_ozellik")
        for cam_ozellik in cam_ozellikleri:
            filters |= Q(glass_feature=cam_ozellik)

        # Tarz Filtresi
    if "tarz" in request.GET:
        tarzlar = request.GET.getlist("tarz")
        for tarz in tarzlar:
            filters |= Q(tarz__id=tarz)  # Tarz ID'lerine göre filtrele

    if "mekanizma" in request.GET:
        mekanizmalar = request.GET.getlist("mekanizma")
        for mekanizma in mekanizmalar:
            filters |= Q(mechanism=mekanizma)

    # Fiyat filtreleme
    fiyat_min = request.GET.get("fiyat_min")  # Varsayılan olarak boş alıyoruz
    fiyat_max = request.GET.get("fiyat_max")  # Varsayılan olarak boş alıyoruz

    # Fiyat aralığı seçilmemişse, filtre uygulamayın
    if fiyat_min or fiyat_max:
        # Eğer fiyat_min boşsa 0 yap, fiyat_max boşsa sonsuz yap
        fiyat_min = float(fiyat_min) if fiyat_min else 0
        fiyat_max = float(fiyat_max) if fiyat_max else float('inf')
        filters &= Q(price__gte=fiyat_min, price__lte=fiyat_max)

    # Filtre uygulama
    products = Product.objects.filter(filters)

    if request.method == "POST":
        productid = request.POST.get("product_id")

        product = Product.objects.get(id=productid)

        if BasketProduct.objects.filter(product=product).exists():
            basket_product = BasketProduct.objects.get(product=product)
            basket_product.quantity = int(basket_product.quantity) + 1

            basket_product.save()
            return redirect("category")
        else:
            basketproduct = BasketProduct.objects.create(user=request.user, product=product, quantity=1)
            basketproduct.save()
            return redirect("category")
    paginator = Paginator(products,1)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    context = {
        "products": products,
        "brands": brands,
        "gender": gender,
        "color": color,
        "case_shapes": case_shapes,
        "strap_types": strap_types,
        "glass_features": glass_features,
        "styles": styles,
        "mechanism": mechanism,
        "product_quantity": ProductQuentity(request)
    }

    return render(request, 'category.html', context)


def Basket(request):
    basket_products = BasketProduct.objects.filter(user=request.user)

    kargo = 29.99
    product_total_price = 0
    total_price = 0
    for product in basket_products:
        product_total_price += product.product.price * float(product.quantity)
    total_price += kargo + product_total_price

    if request.method == "POST":
        product_id = request.POST.get("product_id")

        if request.POST.get("submit") == "btndel":
            basket_product = BasketProduct.objects.get(id=product_id)
            basket_product.delete()
            return redirect("basket")

    context = {
        "basket_products": basket_products,
        "product_total_price": product_total_price,
        "total_price": total_price,
        "kargo": kargo,
        "product_quantity": ProductQuentity(request)

    }
    return render(request, "basket.html", context)


def Profile(request):
    context = {

        "product_quantity": ProductQuentity(request)

    }
    return render(request, "user/profile.html", context)


def Product_detail(request, product_id):
    product = Product.objects.get(id=product_id)

    if request.method == "POST":
        productid = request.POST.get("productid")

        product = Product.objects.get(id=productid)

        if BasketProduct.objects.filter(product=product).exists():
            basket_product = BasketProduct.objects.get(product=product)
            basket_product.quantity = int(basket_product.quantity) + 1

            basket_product.save()
            return redirect(f"/product_detail/{product_id}")
        else:
            basketproduct = BasketProduct.objects.create(user=request.user, product=product, quantity=1)
            basketproduct.save()
            return redirect(f"/product_detail/{product_id}")

    context = {
        "product": product,
        "product_quantity": ProductQuentity(request)
    }

    return render(request, "product_detail.html", context)


def Login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.check_password(password):
                if user is not None:
                    login(request, user)
                    return redirect("index")
            else:
                messages.error(request, "Şifreniz hatalıdır.Lütfen tekrar deneyiniz!")

        else:
            messages.error(request, "E-posta adresiniz hatalıdır.Lütfen tekrar deneyiniz!")

    return render(request, "user/login.html")


def Register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        surname = request.POST.get("surname")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # E-posta zaten kayıtlı mı kontrol et
        if User.objects.filter(email=email).exists():
            messages.error(request, "Bu e-posta adresi başka bir kullanıcıya ait")
        else:
            # Yeni kullanıcı oluştur
            user = User.objects.create(username=email, first_name=name, last_name=surname, email=email)
            user.set_password(password)  # Parolayı şifrele
            user.save()  # Kullanıcıyı kaydet
            login(request, user)  # Kullanıcıyı otomatik olarak giriş yap
            return redirect("index")  # Ana sayfaya yönlendir

    return render(request, "user/register.html")


def Logout(request):
    logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/index'))


def set_language(request, language):
    for lang, _ in settings.LANGUAGES:
        translation.activate(lang)
        try:
            view = resolve(urlparse(request.META.get("HTTP_REFERER")).path)
        except Resolver404:
            view = None
        if view:
            break
    if view:
        translation.activate(language)
        next_url = reverse(view.url_name, args=view.args, kwargs=view.kwargs)
        response = HttpResponseRedirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
    else:
        response = HttpResponseRedirect("/")
    return response
