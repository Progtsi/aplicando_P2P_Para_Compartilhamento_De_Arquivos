import socket
import threading
import os

SHARED_FOLDER = "compartilhado"
BUFFER_SIZE = 1024

if not os.path.exists(SHARED_FOLDER):
    os.makedirs(SHARED_FOLDER)

def start_server(host="192.168.1.3", port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[SERVIDOR] Aguardando conexoes em {host}:{port}...")

    while True:
        conn, addr = server.accept()
        print(f"[CONECTADO] Peer conectado: {addr}")
        threading.Thread(target=handle_client, args=(conn,)).start()

def handle_client(conn):
    try:
        request = conn.recv(BUFFER_SIZE).decode()
        if request == "LIST":
            files = os.listdir(SHARED_FOLDER)
            response = "\n".join(files) if files else "Nenhum arquivo disponivel"
            conn.send(response.encode())
        elif request.startswith("GET "):
            file_name = request.split(" ", 1)[1]
            file_path = os.path.join(SHARED_FOLDER, file_name)
            if os.path.exists(file_path):
                conn.send(b"OK")
                with open(file_path, "rb") as f:
                    while True:
                        data = f.read(BUFFER_SIZE)
                        if not data:
                            break
                        conn.send(data)
                print(f"[ENVIO] Arquivo '{file_name}' enviado.")
            else:
                conn.send(b"ERRO: Arquivo nao encontrado.")
    finally:
        conn.close()

def list_files(server_ip, port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, port))
    sock.send(b"LIST")
    data = sock.recv(4096).decode()
    print("\n--- Arquivos disponiveis ---\n" + data + "\n")
    sock.close()

def download_file(server_ip, file_name, port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, port))
    sock.send(f"GET {file_name}".encode())
    response = sock.recv(BUFFER_SIZE)
    if response == b"OK":
        with open(f"baixado_{file_name}", "wb") as f:
            while True:
                data = sock.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
        print(f"[DOWNLOAD] Arquivo '{file_name}' baixado como 'baixado_{file_name}'")
    else:
        print(response.decode())
    sock.close()

def main():
    print("==== P2P Compartilhamento de Arquivos ====")
    print("1 - Iniciar como servidor (compartilhar arquivos)")
    print("2 - Conectar como cliente (baixar arquivos)")
    choice = input("Escolha uma opcao: ")

    if choice == "1":
        port = int(input("Porta do servidor (padrao 5000): ") or 5000)
        print(f"[INFO] Coloque os arquivos na pasta '{SHARED_FOLDER}' para compartilhar.")
        start_server(port=port)
    elif choice == "2":
        server_ip = input("IP do peer servidor: ")
        port = int(input("Porta do servidor (padrao 5000): ") or 5000)
        while True:
            print("\n--- Menu Cliente ---")
            print("1 - Listar arquivos")
            print("2 - Baixar arquivo")
            print("3 - Sair")
            opt = input("Escolha: ")
            if opt == "1":
                list_files(server_ip, port)
            elif opt == "2":
                file_name = input("Digite o nome do arquivo para baixar: ")
                download_file(server_ip, file_name, port)
            elif opt == "3":
                break
            else:
                print("Opcao invalida.")
    else:
        print("Opcao invalida.")

if __name__ == "__main__":
    main()
