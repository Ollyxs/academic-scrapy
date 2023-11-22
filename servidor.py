import sys
import json
import signal
import socketserver
import threading as th
from datetime import datetime
from requests_html import HTMLSession


session = HTMLSession()
sem = th.BoundedSemaphore(1)


def exit(s, f):
    print("\nSaliendo...")
    sys.exit()


def get_refseek(query):
    refseek = f"https://www.refseek.com/documents?q={query[0]}"
    r = session.get(refseek)
    r.html.render()
    count = 0
    results = []
    print("---Refseek------------------")
    for result in r.html.find(".gsc-webResult"):
        title = result.find(".gs-title", first=True).text
        description = result.find(".gs-snippet", first=True).text
        link = result.find(".gs-title", first=True).absolute_links
        print(f"Title: {title}\nDescription: {description}\nLink: {link}\n")
        results.append(f"Title: {title}\nDescription: {description}\nLink: {link}\n")
        count += 1
        if count >= query[1]:
            break
    return results


def get_scielo(query):
    scielo = f"https://search.scielo.org/?lang=es&count=15&from=0&output=site&sort=&format=summary&fb=&page=1&q={query[0]}"
    r = session.get(scielo)
    r.html.render()
    count = 0
    results = []
    print("---Scielo-------------------")
    for result in r.html.find(".results .item"):
        if result.find(".DOIResults a", first=True):
            title = result.find(".line a", first=True).text
            author = result.find(".author", first=True).text
            link = result.find(".line a", first=True).absolute_links
            doi = result.find(".DOIResults a", first=True).text
            print(f"Title: {title}\nAuthor: {author}\nLink: {link}\nDOI: {doi}\n")
            results.append(
                f"Title: {title}\nAuthor: {author}\nLink: {link}\nDOI: {doi}\n"
            )
            count += 1
            if count >= query[1]:
                break
    return results


class CustomRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print(f"Cliente conectado: {self.client_address}")
        while True:
            data = self.request.recv(4096).decode("utf-8")
            msg = json.loads(data)
            if msg[0].lower().strip() == "exit":
                print(f"Cliente {self.client_address} desconectado")
                break
            with sem:
                with open("log.txt", "a") as f:
                    f.write(f"{datetime.now()} - {self.client_address}: {msg}\n")
            refseek = get_refseek(msg)
            scielo = get_scielo(msg)
            response = [refseek, scielo]
            self.request.sendall(json.dumps(response).encode("utf-8"))


def start_server():
    address = ("localhost", 9988)
    server = socketserver.ForkingTCPServer(address, CustomRequestHandler)
    ip, port = server.server_address
    print(f"Servidor iniciado en {ip}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit)
    start_server()
