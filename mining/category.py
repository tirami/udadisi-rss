import glob
import os
import yaml


class Category(object):

    def __init__(self, category_id, fields={}):
        self.id = category_id
        self.from_dict(fields)

    def from_dict(self, fields):
        self.__dict__.update(fields)

    def load(self):
        f = open(self.file_path(), "r")
        settings = yaml.safe_load(f)
        f.close()
        self.from_dict(settings)

    def save(self):
        settings = {key: str(val) for key, val in self.__dict__.iteritems()}
        del settings['id']  # remove the id, we don't want it serialised
        f = open(self.file_path(), "w")
        yaml.dump(settings, f, default_flow_style=False, encoding='utf-8')
        f.close()

    def file_path(self):
        return os.path.join('categories', 'settings{}.yaml'.format(self.id))

    @staticmethod
    def all():
        files_names = glob.glob1('categories', 'settings*.yaml')
        rtn = []
        for file_name in files_names:
            category_id = file_name[len('settings'):-len('.yaml')]
            category = Category(category_id=category_id)
            category.load()
            rtn.append(category)
        return rtn

    @staticmethod
    def find_by_id(category_id):
        file_path = os.path.join('categories', 'settings{}.yaml'.format(category_id))
        if os.path.exists(file_path):
            rtn = Category(category_id)
            rtn.load()
            return rtn
        else:
            return None

    @staticmethod
    def delete(category_id):
        file_path = os.path.join('categories', 'settings{}.yaml'.format(category_id))
        if os.path.exists(file_path):
            os.remove(file_path)