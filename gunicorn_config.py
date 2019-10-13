from zipfile import ZipFile


def on_starting(server):
    with ZipFile("/export", "r") as zip_object:
        zip_object.extractall("/export_unzip")
    app.config["EXPORT"] = "/export_unzip"
