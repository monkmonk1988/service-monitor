import requests
import time

def check_url(url):
  start_time = time.perf_counter()

  try:
    response = requests.get(url, timeout=5)
    response_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
      "url": url,
      "status_code": response.status_code,
      "response_time_ms": response_time_ms,
      "ok": 200 <= response.status_code <= 399
    }

  except requests.RequestException as error:
    response_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
      "url": url,
      "status_code": None,
      "response_time_ms": response_time_ms,
      "ok": False,
      "error": str(error)
    }

test_urls = [
  "https://www.google.com",
  "https://diese-domain-existiert-definitiv-nicht-123456789.de",
  "https://httpbin.org/status/404"
]

for url in test_urls:
  result = check_url(url)
  print(result)