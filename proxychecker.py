import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import os
import time
import ctypes
import threading

RED = "\033[91m"
GREEN = "\033[92m"
GRAY = "\033[90m"
BLUE = "\033[94m"
RESET = "\033[0m"

valid_count = 0
invalid_count = 0
total_count = 0
start_time = time.time()

def current_time():
    return datetime.now().strftime(f"{GRAY}%I:%M:%S %p | {RESET}")

def update_console():
    while update:
        elapsed_time = time.time() - start_time
        time.sleep(0.1)
        if os.name == 'nt':
            ctypes.windll.kernel32.SetConsoleTitleW(f"Proxy Checker | {total_count} Total | {valid_count} Valid | {invalid_count} Invalid | {elapsed_time:.2f}s")
        else:
            sys.stdout.write(f"\033]0;Proxy Checker | {total_count} Total | {valid_count} Valid | {invalid_count} Invalid | {elapsed_time:.2f}s\007")
            sys.stdout.flush()

def check_proxy(proxy):
    try:
        response = requests.get('https://httpbin.org/ip', proxies={'http': proxy}, timeout=5)
        if response.status_code == 200:
            return (proxy, True)
    except Exception:
        pass
    return (proxy, False)

def print_result(proxy, success):
    if success:
        print(f"{current_time()}{GREEN}SUCCESS {RESET} {proxy}")
    else:
        print(f"{current_time()}{RED}FAIL {RESET} {proxy}")

def filter_proxies(proxy_file_path, max_threads=10):
    global valid_count, invalid_count, total_count, update

    valid_proxies = []

    with open(proxy_file_path, 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]
        total_count = len(proxies)

    update_thread = threading.Thread(target=update_console)
    update_thread.start()

    with ThreadPoolExecutor(max_threads) as executor:
        future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}

        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                result, success = future.result()
                print_result(result, success)
                if success:
                    valid_proxies.append(result)
                    valid_count += 1
                else:
                    invalid_count += 1
            except Exception as e:
                print(f"{current_time()}{RED}ERROR {RESET}{proxy}: {e}")

    update = False
    update_thread.join()

    with open(proxy_file_path, 'w') as file:
        for proxy in valid_proxies:
            file.write(proxy + '\n')

    print(f"\n{current_time()}{BLUE}Proxy check completed. Valid proxies saved to {proxy_file_path}.{RESET}")
    print(f"{current_time()}{GREEN}Valid proxies: {valid_count}{RESET} / {total_count}")
    print(f"{current_time()}{RED}Invalid proxies: {invalid_count}{RESET} / {total_count}")
    os.system("pause")

if __name__ == "__main__":
    os.system("cls")
    update = True 
    proxy_file_path = input(f"{current_time()}{BLUE}Enter the path to the proxy file: {RESET}")
    max_threads = int(input(f"{current_time()}{BLUE}Enter the number of threads to use: {RESET}"))
    filter_proxies(proxy_file_path, max_threads)
