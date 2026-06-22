import os
import connexion
from server.classes.detector import PolicyDetector
from flask import current_app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
yamlfile = os.path.join(BASE_DIR, "yaml", "swagger.yaml")


def create_app():
    app = connexion.App(__name__, specification_dir=BASE_DIR)
    app.add_api(yamlfile, arguments={'title': 'DeviceTagger'}, pythonic_params=True)
    foo = 'bar' # needs to be declared and initialized here
    with app.app.app_context():
        current_app.detector = PolicyDetector()
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=1072)