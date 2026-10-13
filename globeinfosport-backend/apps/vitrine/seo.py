"""Public crawler endpoints; unpublished articles are never indexed."""
from xml.etree.ElementTree import Element, SubElement, tostring

from django.conf import settings
from django.core.paginator import EmptyPage, Paginator
from django.http import Http404, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_safe

from apps.actualites.models import Article


@require_safe
def sitemap(request):
    base = settings.PUBLIC_SITE_URL.rstrip("/")
    articles = Article.objects.filter(
        statut=Article.Statut.PUBLIE, date_publication__lte=timezone.now()
    ).order_by("pk").only("slug", "updated_at")
    paginator = Paginator(articles, 1000)
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    if "page" not in request.GET:
        root = Element("sitemapindex", xmlns=namespace)
        for number in paginator.page_range:
            entry = SubElement(root, "sitemap")
            SubElement(entry, "loc").text = f"{base}/sitemap.xml?page={number}"
    else:
        try:
            page = paginator.page(int(request.GET["page"]))
        except (ValueError, EmptyPage):
            raise Http404("Page de sitemap introuvable")
        root = Element("urlset", xmlns=namespace)
        if page.number == 1:
            for path in ["/", "/actualites", "/haiti", "/international", "/tv", "/galerie", "/contact"]:
                SubElement(SubElement(root, "url"), "loc").text = base + path
        for article in page:
            entry = SubElement(root, "url")
            SubElement(entry, "loc").text = f"{base}/actualites/{article.slug}"
            SubElement(entry, "lastmod").text = article.updated_at.isoformat()
    return HttpResponse(tostring(root, encoding="utf-8", xml_declaration=True), content_type="application/xml")


@require_safe
def robots(request):
    return HttpResponse(
        "User-agent: *\nAllow: /\nDisallow: /redaction/\nDisallow: /admin/\n"
        f"Sitemap: {settings.PUBLIC_SITE_URL.rstrip('/')}/sitemap.xml\n",
        content_type="text/plain",
    )
