import re
import requests
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal
import sys

def banner():
    print(colored(r"""
▄▄▄ .• ▌ ▄ ·.  ▄▄▄· ▪  ▄▄▌      ▄▄▄ .▐▄• ▄ ▪  .▄▄ · ▄▄▄▄▄▄▄▄ . ▐ ▄  ▄▄· ▄▄▄ .     ▄▄·  ▄ .▄▄▄▄ . ▄▄· ▄ •▄ ▄▄▄ .▄▄▄  
▀▄.▀··██ ▐███▪▐█ ▀█ ██ ██•      ▀▄.▀· █▌█▌▪██ ▐█ ▀. •██  ▀▄.▀·•█▌▐█▐█ ▌▪▀▄.▀·    ▐█ ▌▪██▪▐█▀▄.▀·▐█ ▌▪█▌▄▌▪▀▄.▀·▀▄ █·
▐▀▀▪▄▐█ ▌▐▌▐█·▄█▀▀█ ▐█·██▪      ▐▀▀▪▄ ·██· ▐█·▄▀▀▀█▄ ▐█.▪▐▀▀▪▄▐█▐▐▌██ ▄▄▐▀▀▪▄    ██ ▄▄██▀▐█▐▀▀▪▄██ ▄▄▐▀▀▄·▐▀▀▪▄▐▀▀▄ 
▐█▄▄▌██ ██▌▐█▌▐█ ▪▐▌▐█▌▐█▌▐▌    ▐█▄▄▌▪▐█·█▌▐█▌▐█▄▪▐█ ▐█▌·▐█▄▄▌██▐█▌▐███▌▐█▄▄▌    ▐███▌██▌▐▀▐█▄▄▌▐███▌▐█.█▌▐█▄▄▌▐█•█▌
 ▀▀▀ ▀▀  █▪▀▀▀ ▀  ▀ ▀▀▀.▀▀▀      ▀▀▀ •▀▀ ▀▀▀▀▀ ▀▀▀▀  ▀▀▀  ▀▀▀ ▀▀ █▪·▀▀▀  ▀▀▀     ·▀▀▀ ▀▀▀ · ▀▀▀ ·▀▀▀ ·▀  ▀ ▀▀▀ .▀  ▀
                                     by TheOffSecGirl
    """, "cyan"))

# Captura de señal para manejar Ctrl+C
def signal_handler(sig, frame):
    print(colored("\n[!] Interrupción detectada. Saliendo del programa.", "red"))
    sys.exit(0)

# Configurar señal
signal.signal(signal.SIGINT, signal_handler)

def send_login_request(url, email, field_email, field_password, proxy=None):
    try:
        payload = {field_email: email, field_password: 'fakepassword123'}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        proxies = {"http": proxy, "https": proxy} if proxy else None
        response = requests.post(url, data=payload, headers=headers, timeout=10, proxies=proxies)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"[ERROR] {e}"

def test_email_existence(url, email, field_email, field_password, invalid_strings, valid_strings, proxy):
    response_text = send_login_request(url, email, field_email, field_password, proxy)

    if not response_text:
        return f"[!] No se pudo obtener respuesta para {email}."

    if any(err.lower() in response_text.lower() for err in invalid_strings):
        return f"[-] El email {email} no está registrado."
    elif any(success.lower() in response_text.lower() for success in valid_strings):
        return f"[+] El email {email} está registrado."
    else:
        return f"[?] Resultado indeterminado para {email}. Revisar manualmente."

def main():
    banner()
    url = input(colored("\nIngresa la URL del formulario de login: ", "cyan")).strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    field_email = input(colored("\nIngresa el nombre del campo para el email (por defecto: email): ", "cyan")).strip() or "email"
    field_password = input(colored("\nIngresa el nombre del campo para la contraseña (por defecto: password): ", "cyan")).strip() or "password"

    invalid_strings = input(colored("\nIngresa cadenas que indican email inválido, separadas por comas (por defecto: 'no existe,usuario no encontrado'): ", "cyan"))
    invalid_strings = [s.strip() for s in invalid_strings.split(',')] if invalid_strings else ["no existe", "usuario no encontrado"]

    valid_strings = input(colored("\nIngresa cadenas que indican email válido, separadas por comas (por defecto: 'contraseña incorrecta,password incorrecto'): ", "cyan"))
    valid_strings = [s.strip() for s in valid_strings.split(',')] if valid_strings else ["contraseña incorrecta", "password incorrecto"]

    proxy = input(colored("\nIngresa un proxy (opcional, formato http://ip:puerto): ", "cyan")).strip() or None

    email_source = input(colored("\nIngresa '1' para introducir emails manualmente o '2' para cargar desde un archivo: ", "cyan")).strip()

    if email_source == '1':
        email_list = input(colored("\nIngresa los emails a probar (separados por comas): ", "cyan")).split(',')
        email_list = [email.strip() for email in email_list]
    elif email_source == '2':
        file_path = input(colored("\nIngresa la ruta del archivo con la lista de emails: ", "cyan")).strip()
        try:
            with open(file_path, 'r') as file:
                email_list = [line.strip() for line in file.readlines()]
        except Exception as e:
            print(colored(f"[!] Error al leer el archivo: {e}", "red"))
            return
    else:
        print(colored("[!] Opción no válida. Saliendo.", "red"))
        return

    if not email_list:
        print(colored("[!] No se encontraron emails para probar. Saliendo.", "red"))
        return

    print(colored("\n[+] Probando emails en la URL: ", "green"), url)
    results = []

    try:
        with ThreadPoolExecutor(max_workers=10) as executor:  # Limita el número de hilos a 10
            future_to_email = {executor.submit(test_email_existence, url, email, field_email, field_password, invalid_strings, valid_strings, proxy): email for email in email_list}
            for future in as_completed(future_to_email):
                result = future.result()
                results.append(result)
                print(colored(result, "cyan"))

        # Guardar resultados
        with open("resultado_enum.txt", "w") as output_file:
            output_file.write("\n".join(results))
        print(colored("\n[+] Resultados guardados en 'resultado_enum.txt'.", "green"))
    except KeyboardInterrupt:
        print(colored("\n[!] Proceso interrumpido por el usuario. Cerrando hilos...", "red"))

if __name__ == "__main__":
    main()
