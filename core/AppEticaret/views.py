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
from django.contrib.auth.decorators import login_required


def ProductQuentity(request):
    if request.user.is_authenticated:
        return BasketProduct.objects.filter(user=request.user)
    else:
        return None


def index(request):
    products = Product.objects.all()

    # Kullanıcının favori ürünlerinin ID'lerini alalım
    favori_products = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)

    if request.method == "POST":
        product_id = request.POST.get("product_id")

        try:
            product = Product.objects.get(id=product_id)

            # Sepete ekleme işlemi
            if request.POST.get("submit") == "btnbasket":
                basket_product, created = BasketProduct.objects.get_or_create(user=request.user, product=product)
                if not created:
                    # Sepette varsa miktarı artır
                    basket_product.quantity += 1
                    basket_product.save()
                return redirect("index")

            # Favorilere ekleme/çıkarma işlemi
            elif request.POST.get("submit") == "btnfavori":
                favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
                if not created:
                    # Favorilerde varsa sil
                    favorite.delete()
                return redirect("index")

        except Product.DoesNotExist:
            return redirect("index")

    context = {
        'products': products,
        'favori_products': favori_products,  # Favori ürünleri şablona ekleyelim
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

    # Favori ürünleri kullanıcının favori listesine göre filtreleme
    if request.user.is_authenticated:
        favori_products = Favorite.objects.filter(user=request.user).values_list('product', flat=True)
    else:
        favori_products = []

    filters = Q()

    if "marka" in request.GET:
        markalar = request.GET.getlist("marka")
        for marka in markalar:
            filters |= Q(brand__brand=marka)

    if "cinsiyet" in request.GET:
        filters &= Q(gender=request.GET.get("cinsiyet"))

    if "renk" in request.GET:
        renkler = request.GET.getlist("renk")
        for renk in renkler:
            filters |= Q(color__color=renk)

    if "kasa_sekli" in request.GET:
        kasa_sekilleri = request.GET.getlist("kasa_sekli")
        for kasa_sekli in kasa_sekilleri:
            filters |= Q(case_shape__case_shape=kasa_sekli)

    if "kayis_tipi" in request.GET:
        kayis_tipleri = request.GET.getlist("kayis_tipi")
        for kayis_tipi in kayis_tipleri:
            filters |= Q(strap_type__strap_type=kayis_tipi)

    if "cam_ozellik" in request.GET:
        cam_ozellikleri = request.GET.getlist("cam_ozellik")
        for cam_ozellik in cam_ozellikleri:
            filters |= Q(glass_feature__glass_feature=cam_ozellik)

    if "tarz" in request.GET:
        tarzlar = request.GET.getlist("tarz")
        for tarz in tarzlar:
            filters |= Q(style__style=tarz)  # Tarz ID'lerine göre filtrele

    if "mekanizma" in request.GET:
        mekanizmalar = request.GET.getlist("mekanizma")
        for mekanizma in mekanizmalar:
            filters |= Q(mechanism__mechanism=mekanizma)

    # Fiyat filtreleme
    fiyat_min = request.GET.get("fiyat_min")
    fiyat_max = request.GET.get("fiyat_max")

    if fiyat_min or fiyat_max:
        fiyat_min = float(fiyat_min) if fiyat_min else 0
        fiyat_max = float(fiyat_max) if fiyat_max else float('inf')
        filters &= Q(price__gte=fiyat_min, price__lte=fiyat_max)

    # Filtre uygulama
    products = Product.objects.filter(filters)

    if request.method == "POST":
        productid = request.POST.get("product_id")

        product = Product.objects.get(id=productid)

        if request.POST.get("submit") == "btnbasket":

            if BasketProduct.objects.filter(product=product).exists():
                basket_product = BasketProduct.objects.get(product=product)
                basket_product.quantity += 1
                basket_product.save()
                return redirect("category")
            else:
                basketproduct = BasketProduct.objects.create(user=request.user, product=product, quantity=1)
                basketproduct.save()
                return redirect("category")
        elif request.POST.get("submit") == "btnfavori":

            if Favorite.objects.filter(product=product).exists():
                favori = Favorite.objects.get(product=product)
                favori.delete()
                return redirect("category")
            else:
                favori = Favorite.objects.create(user=request.user, product=product)
                favori.save()
                return redirect("category")

    paginator = Paginator(products, 1)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    context = {
        "products": products,
        "brands": brands,
        "genders": gender,
        "colors": color,
        "case_shapes": case_shapes,
        "strap_types": strap_types,
        "glass_features": glass_features,
        "styles": styles,
        "mechanisms": mechanism,
        "favori_products": favori_products,
        "productquantity": ProductQuentity(request)
    }

    return render(request, "category.html", context)


@login_required(login_url='/login/')
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

        elif request.POST.get("submit") == "minus":
            product = BasketProduct.objects.get(id=product_id)

            product.quantity -= 1
            product.save()
            return redirect("basket")

        elif request.POST.get("submit") == "plus":
            product = BasketProduct.objects.get(id=product_id)

            product.quantity += 1
            product.save()
            return redirect("basket")

    context = {
        "basket_products": basket_products,
        "product_total_price": product_total_price,
        "total_price": total_price,
        "kargo": kargo,
        "product_quantity": ProductQuentity(request)

    }
    return render(request, "basket.html", context)


@login_required(login_url='/login/')
def Profile(request):
    user = User.objects.get(username=request.user)
    profil, created = Profil.objects.get_or_create(user=request.user)
    adress, created = Adress.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if request.POST.get("btnsubmit") == "btnpass":
            oldpass = request.POST.get("oldpass")
            newpass = request.POST.get("newpass")
            rnewpass = request.POST.get("rnewpass")

            print(oldpass)
            print(newpass)

            if newpass == rnewpass:
                print("Buırada")
                if user.check_password(oldpass):
                    print("Burar2")
                    user.set_password(newpass)
                    user.save()
                    logout(request)
                    return redirect("login")
                else:
                    messages.error(request, "Eski Şifreniz Yanlış! Tekrar Deneyiniz")
            else:
                messages.error(request, "Şifreler Uyumsuz! Tekrar Deneyiniz")

        elif request.POST.get("btnsubmit") == "btnprofil":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            phone_number = request.POST.get("phone_number")
            birtdate = request.POST.get("birtdate")

            if user.email != email:
                if not User.objects.filter(email=email).exists():
                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    profil.phone_number = phone_number
                    profil.birtdate = birtdate
                    user.save()
                    profil.save()
                    return redirect("profile")
                else:
                    messages.error(request, "Bu E-Posta Adresi Başka Bir Kullanıcı Tarafından Kullanılıyor.")
            else:
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                profil.phone_number = phone_number
                profil.birtdate = birtdate
                user.save()
                profil.save()
                return redirect("profile")
        elif request.POST.get("btnsubmit") == "btnadress":
            adres = request.POST.get("adress")
            province = request.POST.get("province")
            district = request.POST.get("district")
            neighbourhood = request.POST.get("neighbourhood")

            adress.adress = adres
            adress.province = province
            adress.district = district
            adress.neighbourhood = neighbourhood

            adress.save()
            return redirect("profile")

    context = {
        "profil": profil,
        "adress": adress,
        "product_quantity": ProductQuentity(request)

    }
    return render(request, "user/profile.html", context)


def Product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    comments = Comment.objects.filter(product=product)
    comment_user = None
    for comment in comments:
        if comment.user == request.user:
            comment_user = comment.user

    if request.method == "POST":
        if request.POST.get("submit") == "btnbasket":
            productid = request.POST.get("productid")
            quantity = int(request.POST.get("quantity"))
            product = Product.objects.get(id=productid)

            if BasketProduct.objects.filter(product=product).exists():
                basket_product = BasketProduct.objects.get(product=product)
                basket_product.quantity += quantity
                basket_product.save()
            else:
                BasketProduct.objects.create(user=request.user, product=product, quantity=quantity)

            return redirect(f"/product_detail/{product_id}")

        elif request.POST.get("submit") == "btncomment":
            comment_text = request.POST.get("comment")
            Comment.objects.create(
                user=request.user,
                first_name=request.user.first_name,
                last_name=request.user.last_name,
                product=product,
                comment=comment_text
            )
            return redirect(f"/product_detail/{product_id}")

        elif request.POST.get("submit") == "commentupdate":
            comment_id = request.POST.get("comment_id")
            comment_text = request.POST.get("comment")
            update_comment = Comment.objects.get(id=comment_id)
            update_comment.comment = comment_text
            update_comment.save()
            return redirect(f"/product_detail/{product_id}")

    context = {
        "product": product,
        "comments": comments,
        "comment_user": comment_user,
        "product_quantity": ProductQuentity(request)  # ProductQuentity fonksiyonunun doğru çalıştığından emin olun.
    }

    return render(request, "product_detail.html", context)


def Favorite_views(request):
    favorites = Favorite.objects.filter(user=request.user)

    context = {
        "favorites": favorites,
        "product_quantity": ProductQuentity(request)
    }

    return render(request, "favorite.html", context)


def Login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)


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
