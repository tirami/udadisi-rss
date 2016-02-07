import unittest

from forms import Form, FormField, validate_url


class SimpleForm(Form):
    def __init__(self, values):
        super(SimpleForm, self).__init__(values)
        self.parent_uri = FormField('text', 'parent_uri', 'Url of the engine', validate_url, True)
        self.add_field(self.parent_uri)


class SimpleFormTest(unittest.TestCase):
    def test_valid_url(self):
        values = {'parent_uri': 'http://www.google.com'}
        form = SimpleForm(values)
        is_valid = form.validate()
        self.assertEquals(is_valid, True)

    def text_invalid_url(self):
        values = {'parent_uri': 'not a url qwerty'}
        form = SimpleForm(values)
        is_valid = form.validate()
        self.assertEquals(is_valid, False)
        self.assertEquals(form.parent_uri.has_error, True)
        self.assertEquals(form.parent_uri.error_msg, 'parent_uri is not a valid URL.')

