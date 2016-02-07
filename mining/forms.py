import re

#########
# Util
#########
url_re = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

integer_re = re.compile(r"(?<![-.])\b[0-9]+\b(?!\.[0-9])")


def validate_text(text):
    return True, None # free text is always valid


def validate_url(text):
    if url_re.match(text):
        return True, None
    else:
        if len(text) == 0:
            return False, "Please provide a URL."
        else:
            return False, "Please provide a URL. {} is not a valid.".format(text)


def validate_integer(text):
    if integer_re.match(text):
        return True, None
    else:
        if len(text) == 0:
            return False, "Please provide an integer."
        else:
            return False, "Please provide an integer. {} is not valid.".format(text)


class FormField(object):
    def __init__(self, input_type, name, label, placeholder="", validator=validate_text, required=True):
        self.type = input_type
        self.name = name
        self.label = label
        self.placeholder = placeholder
        self.validator = validator
        self.required = required
        self.value = ""
        self.has_error = False
        self.error_msg = None

    def validate(self):
        if not self.value:
            if self.required:
                return False, '{} is required.'.format(self.name)
            else:
                return True, None
        else:
            return self.validator(self.value)


class TextField(FormField):
    def __init__(self, name, label, placeholder="", required=True):
        super(TextField, self).__init__('text', name, label, placeholder, validate_text, required)

    def parsed_value(self):
        return self.value


class URLField(FormField):
    def __init__(self, name, label, placeholder="", required=True):
        super(URLField, self).__init__('text', name, label, placeholder, validate_url, required)

    def parsed_value(self):
        return self.value


class IntegerField(FormField):
    def __init__(self, name, label, placeholder="", required=True):
        super(IntegerField, self).__init__('text', name, label, placeholder, validate_integer, required)

    def parsed_value(self):
        return int(self.value)


class Form(object):
    def __init__(self, values, fields):
        self.fields = []
        self.values = values
        self.__dict__.update(fields)
        for key, field in fields.iteritems():
            self.add_field(field)
        self.fields.sort(key=lambda x: x.name, reverse=True)

    def add_field(self, field):
        field.value = self.values[field.name]
        self.fields.append(field)

    def named_values(self):
        return {field.name: field.parsed_value() for field in self.fields}

    def validate(self):
        has_passed = True
        for field in self.fields:
            ok, msg = field.validate()
            field.has_error = not ok
            field.error_msg = msg
            if field.has_error:
                has_passed = False
        return has_passed
