import requests
from requests_html import HTML

class TestClass(object):
  def test_connectable(self):
    r = requests.get('http://localhost/', timeout=3)
    assert r.status_code == 200
