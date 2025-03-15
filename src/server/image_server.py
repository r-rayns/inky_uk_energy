import http.server
import socketserver

from src.logger import logger


class ImageRequestHandler(http.server.SimpleHTTPRequestHandler):
  def do_GET(self):
    if self.path == '/energy_data.png':
      with open("energy_data.png", "rb") as f:
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        self.wfile.write(f.read())
    else:
      self.send_error(403, 'Forbidden')


def serve_image(port = 9000):
  if port is None:
    port = 9000

  logger.info(f"Running server on port {port}")
  with socketserver.TCPServer(("", port), ImageRequestHandler) as httpd:
    httpd.serve_forever()
