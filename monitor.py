import requests
import time
import socket
import json

def get_response_time(start_time):
  return round((time.perf_counter() - start_time) * 1000, 2)

def check_url(url):
  start_time = time.perf_counter()

  try:
    response = requests.get(url, timeout=5)

    return {
      "url": url,
      "status_code": response.status_code,
      "response_time_ms": get_response_time(start_time),
      "ok": 200 <= response.status_code <= 399
    }

  except requests.RequestException as error:

    return {
      "url": url,
      "status_code": None,
      "response_time_ms": get_response_time(start_time),
      "ok": False,
      "error": type(error).__name__
    }

def check_port(host, port):
  """ hatte erst create_connection die geht aber durch alle IPv4 und IPv6 Adressen und das dauert zu lange. 
      Daher habe ich die getaddrinfo Variante genommen, die nur die erste Adresse nimmt.
      nachteil wen die 2te Adresse die richtige ist oder IPv6 bei mir dann wird es fehlschlagen.
  """
  start_time = time.perf_counter()
  
  try:
    address_info = socket.getaddrinfo(
      host, port, type=socket.SOCK_STREAM
    )
    
    family, socktype, proto, _, address = address_info[0]
    
    with socket.socket(family, socktype, proto) as connection:
      connection.settimeout(3)
      connection.connect(address)
      return {
        "host": host,
        "port": port,
        "response_time_ms": get_response_time(start_time),
        "ok": True
      }
    
  except OSError as error:
    return {
      "host": host,
      "port": port,
      "response_time_ms": get_response_time(start_time),
      "ok": False,
      "error": type(error).__name__
    }

def run_checks(path):
  results = []

  try:
    with open(path, "r", encoding="utf-8") as file:
      targets = json.load(file)

  except FileNotFoundError:
    return [{
      "index": None,
      "type": "file",
      "ok": False,
      "error": f"Error reading {path}"
    }]

  except json.JSONDecodeError as error:
    return [{
      "index": None,
      "type": "file",
      "ok": False,
      "error": (
        f"Error parsing {path}",
        f" at line {error.lineno}, column {error.colno}",
        f"{error.msg}")
    }]

  except OSError as error:
    return [{
      "index": None,
      "type": "file",
      "ok": False,
      "error": f"Error reading {path}: {type(error).__name__}"
    }]

  if not isinstance(targets, list):
    return [{
      "index": None,
      "type": "file",
      "ok": False,
      "error": f"Invalid format in {path}: Expected a list of targets."
    }]


  for index, item in enumerate(targets):
    target_type = item.get("type") if isinstance(item, dict) else None

    try:
      if not isinstance(item, dict):
        raise ValueError("Each target must be a dictionary.")

      if target_type == "url":
        url = item.get("target")

        if not isinstance(url, str) or not url.strip():
          raise ValueError(
            "'target' must be a non-empty URL string."
          )

        result = check_url(url)

      elif target_type == "port":
        host = item.get("host")
        port = item.get("port")

        if not isinstance(host, str) or not host.strip():
          raise ValueError(
            "'host' must be a non-empty string."
          )

        if isinstance(port, bool):
          raise ValueError("'port' must be an integer.")

        try:
          port = int(port)
        except (TypeError, ValueError):
          raise ValueError("'port' must be a valid integer.")

        if not 1 <= port <= 65535:
          raise ValueError(
            "'port' must be between 1 and 65535."
          )

        result = check_port(host, port)

      else:
        result = {
          "ok": False,
          "error": f"Unknown target type: {target_type!r}"
        }

    except (KeyError, TypeError, ValueError) as error:
      result = {
        "ok": False,
        "error": str(error)
      }

    result["index"] = index
    result["type"] = target_type
    results.append(result)

  return results


if __name__ == "__main__":
 
  results = run_checks("targets_tests.json")

  for result in results:
    print(result)
