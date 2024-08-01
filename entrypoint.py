from app import create_app
from waitress import serve
from platformdirs import *
from app.common.environments import APP_PORT, IS_DEVELOPMENT

app = create_app()

if IS_DEVELOPMENT:
    app.run(port=APP_PORT,debug=True)
else:
    serve(app, host="0.0.0.0", port=APP_PORT)