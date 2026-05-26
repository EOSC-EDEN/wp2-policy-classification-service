import os
import connexion

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
yamlfile = os.path.join(BASE_DIR, "yaml", "swagger.yaml")

app = connexion.App(__name__, specification_dir=BASE_DIR)
app.add_api(yamlfile)

if __name__ == "__main__":
    app.run(port=1072)