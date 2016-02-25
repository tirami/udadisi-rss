import flask
from flask import redirect, url_for
from flask import render_template
from flask import request

from forms import Form
from category import Category

app = flask.Flask(__name__)
app.config['DEBUG'] = True

miners = {}
form_fields = {}
miner_cls = None  # the miner class must implement a constructor that takes a category, start and stop methods.


@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'GET':
        # return an html list of all the categories
        return render_template('category/index.html', categories=Category.all(), success=True)
    elif request.method == 'POST':
        # create new category based on the posted id
        params = request.get_json()
        new_category_id = int(params['id'])
        fields = {key: "" for key, value in form_fields.iteritems()}
        new_category = Category(new_category_id, fields)
        new_category.save()
        return 'OK', 200
    else:
        return 'error', 400


@app.route('/categories/<category_id>', methods=['GET', 'POST', 'DELETE'])
def categories_edit(category_id):
    try:
        category = Category.find_by_id(category_id)
        if category:
            if request.method == 'GET':
                category_dict = category.__dict__
                form = Form(category_dict, form_fields)
                return render_template('category/edit.html', form=form, category_id=category_id, success=True)
            elif request.method == 'POST':
                form = Form(request.form, form_fields)
                if form.validate():
                    values = form.named_values()
                    category.from_dict(values)
                    category.save()
                    miner = miner_cls(category)
                    miners[category_id] = miner
                    miner.start()
                    return redirect(url_for('categories'))
                else:
                    return render_template('category/edit.html', form=form, category_id=category_id, success=True)
            elif request.method == 'DELETE':
                if category_id in miners:
                    miner = miners[category_id]
                    miner.stop()
                    del miners[category_id]
                    Category.delete(category_id)
                    return 'Category {} deleted.'.format(category_id), 200
                else:
                    return 'Category {} not present on miner.'.format(category_id), 400
            else:
                return 'Unsupported request method.', 400
        else:
            return 'Category {} not found.'.format(category_id), 400
    except ValueError, e:
        print e
        return '{} is not a valid category id.'.format(category_id), 400