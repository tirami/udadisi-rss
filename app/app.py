from mining.forms import TextField, URLField, IntegerField
import mining.views as views
from miner import RssMiner

form_fields = {
    'name': TextField('name', 'Name', 'Name of the miner.'),
    'parent_id': URLField('parent_id', 'Engine URL', 'URL of the engine.'),
    'interval': IntegerField('interval', 'Interval', 'Mining interval in seconds.'),
    'urls': TextField('urls', 'URLs', 'URLs fo websites to mine (one on each new line)')
}


def run():
    # configure the service
    views.miner_cls = RssMiner
    views.form_fields = form_fields
    # views.app.run(host='0.0.0.0')
    views.app.run()


if __name__ == "__main__":
    run()

