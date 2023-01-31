from django.test import Client, TestCase


class ErrorCaseTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404_page_uses_correct_template(self):
        """Страница 404 отдаёт кастомный шаблон."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')
