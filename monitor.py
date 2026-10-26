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

  except (json.JSONDecodeError, FileNotFoundError) as error:
    return [{
      "ok": False,
      "error": f"Error reading {path}: {type(error).__name__}"
    }]

  if not isinstance(targets, list):
    return [{
      "ok": False,
      "error": f"Invalid format in {path}: Expected a list of targets."
    }]

  for item in targets:
    
    try:
      
      if not isinstance(item, dict):
        raise ValueError("Each target must be a dictionary.")

      target_type = item.get("type")

      if target_type == "url":
        result = check_url(item["target"])
      
      elif target_type == "port":
        result = check_port(item["host"], item["port"])
      
      else:
        result = {
          "ok": False,
          "error": f"Unknown target type: {target_type}"
        }

    except(KeyError, TypeError, ValueError) as error:
      result = {
        "ok": False,
        "error": f"Invalid target format: {type(error).__name__}"
      }

    results.append(result)

  return results


if __name__ == "__main__":
 
  results = run_checks("gibt-es-nicht.json")

  for result in results:
    print(result)
