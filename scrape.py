import requests
from bs4 import BeautifulSoup
from random import randint
from time import sleep
import argparse
from datetime import datetime

BASE_URL = "https://www.fenabrave.org.br/portalv2/Conteudo/emplacamentos"
SESSION = requests.Session()

def get_verification_token(session: requests.Session, url: str) -> str:
    """Obtém o token antifalsificação do site."""
    resp = session.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    token_input = soup.find("input", {"name": "__RequestVerificationToken"})
    if not token_input:
        raise ValueError("Could not find __RequestVerificationToken!")
    return token_input.get("value")

def build_headers(referer: str) -> dict:
    """Cria os headers para requisições."""
    return {
        "User-Agent": "Mozilla/5.0",
        "Referer": referer,
    }

def try_download_file(session, url, headers, data, output_name):
    """Tenta baixar um arquivo PDF. Retorna True se bem-sucedido."""
    print(f"Downloading: {url}")
    response = session.get(url, data=data, headers=headers)
    if response.status_code == 200:
        with open(output_name, "wb") as f:
            f.write(response.content)
        print("File saved!")
        return True
    return False

def try_alternative_urls(session, year, month, headers, data):
    """Tenta URLs alternativas para o download."""

    alt_url_1 = f"https://www.fenabrave.org.br/portal/files/{year}_{month:02d}_2.pdf"
    if try_download_file(session, alt_url_1, headers, data, f"{year}_{month:02d}.pdf"):
        print("File saved from alternative URL!")
        return True

    for i in range(1, 10):
        alt_url_2 = f'https://www.fenabrave.org.br/portal/files/{i}_{year}_{month:02d}_2.pdf'
        print(f"Trying alternative URL: {alt_url_2}")
        sleep(randint(1, 3))
        if try_download_file(session, alt_url_2, headers, data, f"{year}_{month:02d}.pdf"):
            print("File saved from alternative URL!")
            return True
    return False

def download_all_pdfs(start_year = 2003, end_year = 2025, start_month = 1, end_month = 12):
    """Faz o download dos PDFs de emplacamentos entre os anos especificados."""
    token = get_verification_token(SESSION, BASE_URL)
    headers = build_headers(BASE_URL)
    data = {"__RequestVerificationToken": token}

    for year in range(start_year, end_year + 1):
        for month in range(start_month, end_month):
            url = f"https://www.fenabrave.org.br/portal/files/{year}_{month:02d}_02.pdf"
            output_name = f"{year}_{month:02d}.pdf"

            if not try_download_file(SESSION, url, headers, data, output_name):
                try_alternative_urls(SESSION, year, month, headers, data)

            sleep(randint(1, 3))

def validate_month(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 12:
        raise argparse.ArgumentTypeError(f"Mês inválido: {value}. Deve ser entre 1 e 12.")
    return ivalue

def validate_year(value):
    current_year = datetime.now().year
    ivalue = int(value)
    if ivalue < 2000 or ivalue > current_year:
        raise argparse.ArgumentTypeError(f"Ano inválido: {value}. Deve estar entre 2000 e {current_year}.")
    return ivalue

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-year", type=validate_year, required=True)
    parser.add_argument("--end-year", type=validate_year, required=True)
    parser.add_argument("--start-month", type=validate_month, default=1)
    parser.add_argument("--end-month", type=validate_month, default=12)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if args.start_year > args.end_year:
        raise ValueError("Ano inicial não pode ser maior que o ano final.")
    if args.start_year == args.end_year and args.start_month > args.end_month:
        raise ValueError("Mês inicial não pode ser maior que o mês final dentro do mesmo ano.")
    download_all_pdfs(
        start_year=args.start_year,
        end_year=args.end_year,
        start_month=args.start_month,
        end_month=args.end_month
    )
