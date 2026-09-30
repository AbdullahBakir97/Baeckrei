"""Search engine support: robots.txt, sitemap and server-rendered meta tags."""
from decimal import Decimal

import pytest
from django.test import RequestFactory
from django.utils import timezone

from apps.content.models import Post
from apps.core import seo
from apps.products.models import Category, Product


@pytest.fixture
def catalog(db):
    breads = Category.objects.get(slug='breads')
    visible = Product.objects.create(
        name='Roggenbrot', name_en='Rye bread', description='Kräftiges Roggenbrot', description_en='Hearty rye bread',
        category=breads, price=Decimal('4.20'), stock=5, status='active', available=True, image='products/rye.png',
    )
    draft = Product.objects.create(
        name='Geheim', description='x', category=breads, price=Decimal('1.00'), stock=5,
        status='draft', available=True, image='products/x.png',
    )
    post = Post.objects.create(title='Neue Brezeln', slug='neue-brezeln', body='Frisch aus dem Ofen.',
                               published_at=timezone.now())
    return visible, draft, post


def test_robots_points_to_sitemap_and_hides_private_pages(client, settings):
    settings.FRONTEND_URL = 'https://backlover.example'
    body = client.get('/robots.txt').content.decode()
    assert 'Sitemap: https://backlover.example/sitemap.xml' in body
    assert 'Disallow: /checkout' in body and 'Disallow: /api/' in body


def test_sitemap_lists_public_pages_only(client, settings, catalog):
    settings.FRONTEND_URL = 'https://backlover.example'
    visible, draft, post = catalog
    body = client.get('/sitemap.xml').content.decode()
    assert f'https://backlover.example/products/{visible.pk}' in body
    assert str(draft.pk) not in body
    assert 'https://backlover.example/blog/neue-brezeln' in body
    assert 'https://backlover.example/categories/breads' in body
    assert 'hreflang="en"' in body


def test_product_page_meta_in_both_languages(catalog, settings):
    settings.FRONTEND_URL = 'https://backlover.example'
    visible = catalog[0]
    factory = RequestFactory()
    german = seo.page_meta(factory.get('/', HTTP_ACCEPT_LANGUAGE='de'), f'products/{visible.pk}')
    assert german['title'].startswith('Roggenbrot')
    assert german['type'] == 'product'
    product_ld = german['json_ld'][-1]
    assert product_ld['offers']['price'] == '4.20' and product_ld['offers']['priceCurrency'] == 'EUR'
    english = seo.page_meta(factory.get('/?lang=en'), f'products/{visible.pk}')
    assert english['title'].startswith('Rye bread')
    assert english['description'] == 'Hearty rye bread'


def test_private_pages_are_not_indexed(db):
    meta = seo.page_meta(RequestFactory().get('/'), 'checkout')
    assert meta['noindex'] is True


def test_storefront_page_gets_its_meta_tags(tmp_path, settings, catalog):
    index = tmp_path / 'index.html'
    index.write_text('<!doctype html><html lang="en"><head><title>Backlover</title></head><body><div id="app"></div></body></html>')
    settings.FRONTEND_INDEX_FILE = str(index)
    seo._index_template.cache_clear()
    visible = catalog[0]
    response = seo.spa_index(RequestFactory().get('/', HTTP_ACCEPT_LANGUAGE='de'), f'products/{visible.pk}')
    html = response.content.decode()
    assert '<title>Roggenbrot · Backlover</title>' in html
    assert 'property="og:type" content="product"' in html
    assert '"@type": "Product"' in html
    assert '<html lang="de">' in html
    assert '<div id="app"></div>' in html
