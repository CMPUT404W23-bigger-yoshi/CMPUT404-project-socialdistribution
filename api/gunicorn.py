from api.app import create_app

# try to prevent others from importing from here
__all__ = []

# entrypoint for gunicorn.
# we need to be able to pass params to create_app
# for example to configure DB URIs for testing,
# but gunicorn needs a globally scoped app object to start the app as well. hence this entrypoint
app = create_app()
