import sys
import socket
import argparse
import json


def client(ip, port, results):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("No se pudo crear el socket")
        sys.exit()

    try:
        s.connect((ip, port))
    except NameError:
        print("Direccion IP y/o puertos no definidos")
        print("Utilice -a para definir la direccion IP")
        print("Utilice -p para definir el puerto")
        sys.exit()
    except ConnectionRefusedError:
        print("Conexion rechazada")
        sys.exit()
    except OverflowError:
        print("Puerto invalido, debe ser un entero entre 0 y 65535")
        sys.exit()
    except socket.error:
        print("Fallo temporal en la resolucion de nombres")
        sys.exit()

    while True:
        try:
            m = input(" >> ")
            msg = [m, results]
            s.send(json.dumps(msg).encode("utf-8"))
            if m.lower().strip() == "exit":
                s.close()
                break
            data = s.recv(4096).decode("utf-8")
            response = json.loads(data)
            print("Resultados de la busqueda:")
            print("\n---Refseek------------------\n")
            for result in response[0]:
                print(result)
            print("\n---Scielo-------------------\n")
            for result in response[1]:
                print(result)
        except Exception as e:
            s.close()
            print("A ocurrido un error: ", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente TCP")
    parser.add_argument("-a", "--address", type=str, help="Direccion IP del servidor")
    parser.add_argument("-p", "--port", type=int, help="Puerto del servidor")
    parser.add_argument(
        "-r",
        "--results",
        default=3,
        type=int,
        help="Número de resultados, por defecto 3",
    )
    args = parser.parse_args()
    client(args.address, args.port, args.results)
