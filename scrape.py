import requests
from bs4 import BeautifulSoup
from random import randint
from time import sleep

# Base URL
base_url = "https://www.fenabrave.org.br/portalv2/Conteudo/emplacamentos"
session = requests.Session()
resp = session.get(base_url)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")
token_input = soup.find("input", {"name": "__RequestVerificationToken"})

if not token_input:
    raise ValueError("Could not find __RequestVerificationToken!")
token_value = token_input.get("value")

get_data = {
    "__RequestVerificationToken": token_value # Anti-forgery cookie
}
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": base_url,
}

for year in range(2015, 2026):
    for month in range(1, 13):
        month_str = f"{month:02d}"
        download_url = f"https://www.fenabrave.org.br/portal/files/{year}_{month_str}_02.pdf"

        print(f"Downloading: {download_url}")

        download_response = session.get(download_url, data=get_data, headers=headers)

        if download_response.status_code == 200:
            with open(f"{year}_{month_str}.pdf.pdf", "wb") as f:
                f.write(download_response.content)
            print("File saved!")
        else:
            for i in range(1, 10):
                alt_download_url = f'https://www.fenabrave.org.br/portal/files/{i}_{year}_{month_str}_2.pdf'
                print(f"Trying alternative URL: {alt_download_url}")
                sleep(randint(1, 3))
                download_response = session.get(alt_download_url, data=get_data, headers=headers)
                if download_response.status_code == 200:
                    with open(f"{year}_{month_str}.pdf", "wb") as f:
                        f.write(download_response.content)
                    print("File saved from alternative URL!")
                    break
        sleep(randint(1, 3))
                
    
