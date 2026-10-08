"""Render the shared first-view band for service and corporate pages."""
from html import escape
from pathlib import Path
from string import Template
import re
from bs4 import BeautifulSoup

TEMPLATE = Path(__file__).resolve().parents[1] / 'source/shared-ui/service-banner.html'


def render_service_banner(title, lines, image_src=None, image_alt='', image_position=None,
                          mobile_src=None, image_width=1536, image_height=1024):
    picture = ''
    if image_src:
        position = f' style="--banner-image-position: {escape(image_position, quote=True)};"' if image_position else ''
        picture_class = 'c-house-cleaning-mv__artwork' if mobile_src else 'c-flex-picture'
        source = f'<source media="(max-width: 767.98px)" srcset="{escape(mobile_src, quote=True)}">' if mobile_src else ''
        picture = (f'<picture class="{picture_class}">{source}<img class="c-flex-image c-house-cleaning-mv__image"'
                   f' src="{escape(image_src, quote=True)}" alt="{escape(image_alt, quote=True)}"'
                   f' width="{int(image_width)}" height="{int(image_height)}" loading="eager" decoding="async"{position}></picture>')
    return Template(TEMPLATE.read_text(encoding='utf-8').strip()).substitute(
        title=escape(title), message='<br/>'.join(escape(line) for line in lines), picture=picture,
        banner_class=' c-house-cleaning-mv--artwork' if mobile_src else '',
        message_class=' c-house-cleaning-mv__sr-copy' if mobile_src else '')


def transform_service_banners(html):
    def replace(match):
        banner = BeautifulSoup(match[0], 'html.parser')
        title = banner.select_one('.c-house-cleaning-mv__sr-heading')
        message = banner.select_one('.c-house-cleaning-mv__text')
        if not title or not message:
            return match[0]
        photo = banner.select_one('.c-house-cleaning-mv__image')
        mobile = banner.select_one('source[media]')
        position = re.search(r'--banner-image-position:\s*([^;]+)', photo.get('style', '')) if photo else None
        return render_service_banner(
            title.get_text(strip=True), message.get_text('\n', strip=True).split('\n'),
            photo.get('src') if photo else None, photo.get('alt', '') if photo else '',
            position[1].strip() if position else None,
            mobile.get('srcset') if mobile else None,
            photo.get('width', 1536) if photo else 1536,
            photo.get('height', 1024) if photo else 1024)
    return re.sub(r'<div\b(?=[^>]*\bclass="[^"]*\bc-house-cleaning-mv--check\b)[^>]*>.*?</div>',
                  replace, html, flags=re.S)
