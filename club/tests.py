from html.parser import HTMLParser
from urllib.parse import urlsplit

from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import resolve, reverse


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.headings = []
        self.landmarks = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "img":
            self.images.append(attrs)
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(int(tag[1]))
        if tag in {"header", "nav", "main", "section", "article", "footer"}:
            self.landmarks.add(tag)


class NavigationTests(TestCase):
    fixtures = ["club_catalog"]

    def test_named_routes_render(self):
        for name in ("home", "booking_create", "menu_catalog", "dashboard", "login", "register", "booking_list"):
            with self.subTest(route=name):
                url = reverse(f"club:{name}")
                self.assertEqual(resolve(url).view_name, f"club:{name}")
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                page = PageParser()
                page.feed(response.content.decode())
                self.assertEqual(page.headings.count(1), 1)
                for link in page.links:
                    path = urlsplit(link).path
                    if path:
                        self.assertEqual(self.client.get(path).status_code, 200)

    def test_home_structure_and_assets(self):
        response = self.client.get(reverse("club:home"))
        page = PageParser()
        page.feed(response.content.decode())
        self.assertEqual(page.landmarks, {"header", "nav", "main", "section", "article", "footer"})
        for previous, current in zip(page.headings, page.headings[1:]):
            self.assertLessEqual(current, previous + 1)
        self.assertEqual(len(page.images), 4)
        for image in page.images:
            self.assertTrue(image.get("alt"))
            self.assertTrue(finders.find(image["src"].removeprefix("/static/")))
        self.assertNotContains(response, "style=")
        self.assertNotContains(response, "<!--")

    def test_unknown_route_returns_404(self):
        self.assertEqual(self.client.get("/not-a-page/").status_code, 404)
