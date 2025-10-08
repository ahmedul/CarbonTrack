from mangum import Mangum
from combined_api_server import app

handler = Mangum(app)
