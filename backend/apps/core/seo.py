"""Search engine and share-preview support for the Vue storefront.

The storefront is a single-page app, so crawlers that don't run JavaScript
(WhatsApp, Facebook, most link previews) would see the same empty page for
every URL. These views give them real content:

* ``robots.txt`` and ``sitemap.xml`` list the public pages, products,
  categories and journal posts.
* ``spa_index`` serves the built ``index.html`` with the page's title,
  description, share image and structured data already in ``<head>``. The
  app takes over in the browser as usual. It is only routed when
  ``FRONTEND_INDEX_FILE`` points at the built file (production).
"""
import json
from functools import lru_cache
from html import escape
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils.translation import get_language_from_request
from django.views.decorators.http import require_GET

from apps.content.models import Post
from apps.products.models import Category, Product

STATIC_PAGES = ['/', '/products', '/seasonal', '/blog', '/about', '/contact',
                '/impressum', '/privacy', '/terms', '/cookie-policy']
PRIVATE_PREFIXES = ['/admin', '/cart', '/checkout', '/profile', '/orders', '/settings',
                    '/login', '/register', '/forgot-password', '/reset-password', '/wishlist', '/compare']

PAGE_TEXT = {
    'de': {
        'tagline': 'Bäckerei in der {street}, {city}',
        'description': 'Frisches Brot, Brezeln, Croissants und Kuchen, jeden Morgen gebacken in der {street}, {city}. '
                       'Online bestellen zur Abholung oder Lieferung.',
        '/products': 'Shop', '/seasonal': 'Saisonales', '/blog': 'Journal', '/about': 'Über uns',
        '/contact': 'Kontakt', '/impressum': 'Impressum', '/privacy': 'Datenschutz', '/terms': 'AGB',
        '/cookie-policy': 'Cookie-Richtlinie',
    },
    'en': {
        'tagline': 'Bakery on {street}, {city}',
        'description': 'Fresh bread, Brezeln, croissants and cakes baked every morning on {street}, {city}. '
                       'Order online for pickup or delivery.',
        '/products': 'Shop', '/seasonal': 'Seasonal', '/blog': 'Journal', '/about': 'About us',
        '/contact': 'Contact', '/impressum': 'Impressum', '/privacy': 'Privacy Policy',
        '/terms': 'Terms and Conditions', '/cookie-policy': 'Cookie Policy',
    },
}


def site_url():
    return settings.FRONTEND_URL.rstrip('/')


def _shop():
    from apps.shop import config
    shop = config.get()
    return {
        'name': shop.name,
        'street': ' '.join(filter(None, [shop.street, shop.house_number])),
        'postal_code': shop.postal_code,
        'city': shop.city,
        'phone': shop.phone,
        'hours': shop.opening_hours,
    }


def _language(request):
    requested = request.GET.get('lang')
    if requested in PAGE_TEXT:
        return requested
    language = (get_language_from_request(request) or 'de')[:2]
    return language if language in PAGE_TEXT else 'de'


def _localized(obj, field, language):
    if language == 'en' and getattr(obj, f'{field}_en', ''):
        return getattr(obj, f'{field}_en')
    return getattr(obj, field, '') or ''


def _clip(text, length=160):
    text = ' '.join(str(text or '').split())
    return text if len(text) <= length else text[:length - 1].rstrip() + '…'


def _media_url(request, file_field):
    if not file_field:
        return None
    return request.build_absolute_uri(file_field.url)


def public_products():
    return Product.objects.filter(status='active', available=True).select_related('category')


@require_GET
def robots_txt(request):
    lines = ['User-agent: *', 'Allow: /']
    lines += [f'Disallow: {prefix}' for prefix in PRIVATE_PREFIXES + ['/api/']]
    lines += ['', f'Sitemap: {site_url()}/sitemap.xml', '']
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


@require_GET
def sitemap_xml(request):
    """Every public page, with German and English alternates (?lang=)."""
    entries = [(path, None) for path in STATIC_PAGES]
    entries += [(f'/categories/{c.slug}', c.modified_at) for c in Category.objects.filter(is_active=True)]
    entries += [(f'/products/{p.pk}', p.modified_at) for p in public_products()]
    entries += [(f'/blog/{post.slug}', post.updated_at) for post in Post.objects.published()]

    base = site_url()
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             'xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for path, modified in entries:
        url = xml_escape(f'{base}{path}')
        parts.append('<url>')
        parts.append(f'<loc>{url}</loc>')
        if modified:
            parts.append(f'<lastmod>{modified.date().isoformat()}</lastmod>')
        for language in ('de', 'en'):
            parts.append(f'<xhtml:link rel="alternate" hreflang="{language}" href="{url}?lang={language}"/>')
        parts.append(f'<xhtml:link rel="alternate" hreflang="x-default" href="{url}"/>')
        parts.append('</url>')
    parts.append('</urlset>')
    return HttpResponse('\n'.join(parts), content_type='application/xml; charset=utf-8')


def bakery_json_ld():
    shop = _shop()
    return {
        '@context': 'https://schema.org',
        '@type': 'Bakery',
        '@id': f'{site_url()}/#bakery',
        'name': shop['name'],
        'url': site_url(),
        'image': f'{site_url()}/og-image.jpg',
        'address': {'@type': 'PostalAddress', 'streetAddress': shop['street'], 'postalCode': shop['postal_code'],
                    'addressLocality': shop['city'], 'addressCountry': 'DE'},
        **({'telephone': shop['phone']} if shop['phone'] else {}),
        'openingHoursSpecification': [
            {'@type': 'OpeningHoursSpecification', 'dayOfWeek': DAY_NAMES[day],
             'opens': opens.strftime('%H:%M'), 'closes': closes.strftime('%H:%M')}
            for day, ranges in sorted(shop['hours'].items()) for opens, closes in ranges
        ],
        'servesCuisine': 'Bakery',
        'priceRange': '€',
    }


DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def page_meta(request, path):
    """Title, description, image and structured data for a storefront URL."""
    language = _language(request)
    text = PAGE_TEXT[language]
    shop = _shop()
    path = '/' + path.strip('/') if path.strip('/') else '/'
    meta = {
        'language': language,
        'title': f"{shop['name']} · {text['tagline'].format(**shop)}",
        'description': text['description'].format(**shop),
        'image': f'{site_url()}/og-image.jpg',
        'url': f'{site_url()}{path}',
        'type': 'website',
        'noindex': any(path == p or path.startswith(p + '/') for p in PRIVATE_PREFIXES),
        'json_ld': [bakery_json_ld()],
        'site_name': shop['name'],
    }
    parts = path.strip('/').split('/')

    if path in text:
        meta['title'] = f"{text[path]} · {shop['name']}"
    elif parts[0] == 'products' and len(parts) == 2:
        product = public_products().filter(pk=_uuid_or_none(parts[1])).first() if _uuid_or_none(parts[1]) else None
        if product:
            name = _localized(product, 'name', language)
            description = _localized(product, 'description', language)
            image = _media_url(request, product.image)
            meta.update(title=f"{name} · {shop['name']}", description=_clip(description) or meta['description'],
                        image=image or meta['image'], type='product')
            meta['json_ld'].append({
                '@context': 'https://schema.org', '@type': 'Product', 'name': name,
                'description': _clip(description, 500), 'image': [image] if image else [],
                'offers': {'@type': 'Offer', 'price': f'{product.price:.2f}', 'priceCurrency': 'EUR',
                           'availability': 'https://schema.org/InStock' if product.stock > 0
                           else 'https://schema.org/OutOfStock',
                           'url': meta['url'], 'seller': {'@id': f'{site_url()}/#bakery'}},
            })
    elif parts[0] == 'categories' and len(parts) == 2:
        category = Category.objects.filter(slug=parts[1], is_active=True).first()
        if category:
            name = _localized(category, 'name', language)
            meta.update(title=f"{name} · {shop['name']}",
                        description=_clip(_localized(category, 'description', language)) or meta['description'])
    elif parts[0] == 'blog' and len(parts) == 2:
        post = Post.objects.published().filter(slug=parts[1]).first()
        if post:
            image = _media_url(request, post.cover_image)
            meta.update(title=f"{post.title} · {shop['name']}", description=_clip(post.excerpt or post.body),
                        image=image or meta['image'], type='article')
            meta['json_ld'].append({
                '@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': post.title,
                'datePublished': post.published_at.isoformat(), 'dateModified': post.updated_at.isoformat(),
                'publisher': {'@id': f'{site_url()}/#bakery'}, 'mainEntityOfPage': meta['url'],
            })
    return meta


def _uuid_or_none(value):
    import uuid
    try:
        return uuid.UUID(str(value))
    except ValueError:
        return None


def render_head(meta):
    def tag(attr, key, content):
        return f'<meta {attr}="{escape(key)}" content="{escape(str(content))}">'

    lines = [
        f'<title>{escape(meta["title"])}</title>',
        tag('name', 'description', meta['description']),
        f'<link rel="canonical" href="{escape(meta["url"])}">',
        tag('property', 'og:title', meta['title']),
        tag('property', 'og:description', meta['description']),
        tag('property', 'og:image', meta['image']),
        tag('property', 'og:url', meta['url']),
        tag('property', 'og:type', meta['type']),
        tag('property', 'og:site_name', meta.get('site_name') or settings.SHOP_NAME),
        tag('property', 'og:locale', 'de_DE' if meta['language'] == 'de' else 'en_GB'),
        tag('name', 'twitter:card', 'summary_large_image'),
    ]
    if meta['noindex']:
        lines.append(tag('name', 'robots', 'noindex, nofollow'))
    for item in meta['json_ld']:
        data = json.dumps(item, ensure_ascii=False).replace('</', '<\\/')
        lines.append(f'<script type="application/ld+json">{data}</script>')
    return '\n    '.join(lines)


@lru_cache(maxsize=1)
def _index_template(path):
    return Path(path).read_text(encoding='utf-8')


def spa_index(request, path=''):
    """The built storefront page with this URL's meta tags already filled in."""
    index_file = getattr(settings, 'FRONTEND_INDEX_FILE', '')
    if not index_file or not Path(index_file).exists():
        raise Http404('The storefront build is not configured.')
    html = _index_template(index_file)
    meta = page_meta(request, path)
    # The build carries a generic <title>; replace it with the page's own head.
    head = render_head(meta)
    if '<title>' in html:
        start, end = html.index('<title>'), html.index('</title>') + len('</title>')
        html = html[:start] + head + html[end:]
    else:
        html = html.replace('</head>', f'    {head}\n  </head>', 1)
    html = html.replace('<html lang="en">', f'<html lang="{meta["language"]}">', 1)
    response = HttpResponse(html)
    response['Vary'] = 'Accept-Language'
    return response
