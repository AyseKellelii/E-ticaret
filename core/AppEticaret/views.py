import json

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from urllib.parse import urlparse
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.urls.base import resolve, reverse
from django.urls.exceptions import Resolver404
from django.utils import translation
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .models import *
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


def ProductQuentity(request):
    if request.user.is_authenticated:
        return BasketProduct.objects.filter(user=request.user)
    return None

def index(request):
    products = Product.objects.all()
    favori_products = (
        Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        if request.user.is_authenticated else []
    )

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        try:
            product = Product.objects.get(id=product_id)

            if request.POST.get("submit") == "btnbasket":
                basket_product, created = BasketProduct.objects.get_or_create(
                    user=request.user, product=product,
                    defaults={'quantity': 1}
                )
                if not created:
                    basket_product.quantity += 1
                    basket_product.save()
                return redirect("index")

            elif request.POST.get("submit") == "btnfavori":
                favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
                if not created:
                    favorite.delete()
                return redirect("index")

        except Product.DoesNotExist:
            messages.error(request, "Ürün bulunamadı.")
            return redirect("index")

    context = {
        'products': products,
        'favori_products': favori_products,
    }
    return render(request, 'index.html', context)


@login_required(login_url='/login/')
def Category(request):
    """
    Ürünleri listeleme, filtreleme ve sepete ekleme işlemleri.
    """
    # Tüm ürün, marka ve filtre seçeneklerini çekiyoruz
    products = Product.objects.all()
    brands = Brand.objects.all()
    colors = Color.objects.all()
    case_shapes = CaseShape.objects.all()
    strap_types = StrapType.objects.all()
    glass_features = GlassFeature.objects.all()
    styles = Style.objects.all()
    mechanisms = Mechanism.objects.all()
    filters = Q()

    # Kullanıcı favori ürünlerini al
    if request.user.is_authenticated:
        favori_products = Favorite.objects.filter(user=request.user).values_list('product', flat=True)
    else:
        favori_products = []

    # GET istekleriyle filtreleme işlemleri
    if "marka" in request.GET:
        filters |= Q(brand__brand__in=request.GET.getlist("marka"))

    if "cinsiyet" in request.GET:
        filters &= Q(gender=request.GET.get("cinsiyet"))

    if "renk" in request.GET:
        filters |= Q(color__color__in=request.GET.getlist("renk"))

    if "kasa_sekli" in request.GET:
        filters |= Q(case_shape__case_shape__in=request.GET.getlist("kasa_sekli"))

    if "kayis_tipi" in request.GET:
        filters |= Q(strap_type__strap_type__in=request.GET.getlist("kayis_tipi"))

    if "cam_ozellik" in request.GET:
        filters |= Q(glass_feature__glass_feature__in=request.GET.getlist("cam_ozellik"))

    if "tarz" in request.GET:
        filters |= Q(tarz__style__in=request.GET.getlist("tarz"))

    if "mekanizma" in request.GET:
        filters |= Q(mechanism__mechanism__in=request.GET.getlist("mekanizma"))

    # Fiyat filtreleme
    fiyat_min = request.GET.get("fiyat_min", 0)
    fiyat_max = request.GET.get("fiyat_max", float('inf'))
    filters &= Q(price__gte=float(fiyat_min), price__lte=float(fiyat_max))

    # Filtrelenen ürünleri getir
    products = Product.objects.filter(filters)

    # Sayfalama işlemi
    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    # POST işlemleri (Sepete ekleme)
    if request.method == "POST":
        product_id = request.POST.get("product_id")

        try:
            product = Product.objects.get(id=product_id)

            if request.POST.get("submit") == "btnbasket":
                basket_product, created = BasketProduct.objects.get_or_create(
                    user=request.user,
                    product=product,
                    defaults={"quantity": 1}
                )
                if not created:
                    basket_product.quantity += 1
                    basket_product.save()
                messages.success(request, "Ürün sepete eklendi.")
                return redirect("category")

        except Product.DoesNotExist:
            messages.error(request, "Ürün bulunamadı.")
            return redirect("category")

    # Şablona gönderilecek değişkenler
    context = {
        "products": products,
        "brands": brands,
        "colors": colors,
        "case_shapes": case_shapes,
        "strap_types": strap_types,
        "glass_features": glass_features,
        "styles": styles,
        "mechanisms": mechanisms,
        "favori_products": favori_products,
        "productquantity": ProductQuentity(request)
    }
    return render(request, "category.html", context)

@login_required(login_url='/login/')
def Basket(request):
    basket_products = BasketProduct.objects.filter(user=request.user)
    kargo = 29.99
    product_total_price = sum([product.product.price * product.quantity for product in basket_products])
    total_price = kargo + product_total_price

    if request.method == "POST":
        product_id = request.POST.get("product_id")

        try:
            basket_product = BasketProduct.objects.get(id=product_id, user=request.user)

            if request.POST.get("submit") == "btndel":
                basket_product.delete()
            elif request.POST.get("submit") == "minus" and basket_product.quantity > 1:
                basket_product.quantity -= 1
                basket_product.save()
            elif request.POST.get("submit") == "plus":
                basket_product.quantity += 1
                basket_product.save()

        except BasketProduct.DoesNotExist:
            messages.error(request, "Ürün bulunamadı.")

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
    profil, _ = Profil.objects.get_or_create(user=request.user)
    adress, _ = Adress.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if request.POST.get("btnsubmit") == "btnpass":
            oldpass = request.POST.get("oldpass")
            newpass = request.POST.get("newpass")
            rnewpass = request.POST.get("rnewpass")

            if newpass == rnewpass:
                if request.user.check_password(oldpass):
                    request.user.set_password(newpass)
                    request.user.save()
                    logout(request)
                    return redirect("login")
                messages.error(request, "Eski şifre yanlış.")
            else:
                messages.error(request, "Yeni şifreler eşleşmiyor.")

        elif request.POST.get("btnsubmit") == "btnprofil":
            request.user.first_name = request.POST.get("first_name", request.user.first_name)
            request.user.last_name = request.POST.get("last_name", request.user.last_name)
            request.user.email = request.POST.get("email", request.user.email)
            profil.phone_number = request.POST.get("phone_number", profil.phone_number)
            profil.birtdate = request.POST.get("birtdate", profil.birtdate)
            request.user.save()
            profil.save()
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

@csrf_exempt
def toggle_favorite(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
            favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
            if not created:
                favorite.delete()
                return JsonResponse({'status': 'removed', 'product_id': product_id})
            return JsonResponse({'status': 'added', 'product_id': product_id})
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def Favorite_views(request):
    favorites = Favorite.objects.filter(user=request.user)
    favorite_product_ids = favorites.values_list('product_id', flat=True)

    context = {
        "favorites": favorites,
        "favorite_product_ids": list(favorite_product_ids),
        "product_quantity": ProductQuentity(request),
    }

    return render(request, "favorite.html", context)


def Login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return redirect("index")
        messages.error(request, "E-posta veya şifre yanlış.")

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
            try:
                # Yeni kullanıcı oluştur
                user = User.objects.create_user(username=email, first_name=name, last_name=surname, email=email, password=password)
                login(request, user)  # Kullanıcıyı otomatik olarak giriş yap
                return redirect("index")  # Ana sayfaya yönlendir
            except Exception as e:
                messages.error(request, f"Bir hata oluştu: {str(e)}")

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
