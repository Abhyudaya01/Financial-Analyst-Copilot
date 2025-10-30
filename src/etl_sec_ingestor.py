import os
import requests
import time
from bs4 import BeautifulSoup

# === Folder setup ===
RAW_DIR = "../data/raw"
PROCESSED_DIR = "../data/processed"
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# === SEC configuration ===
SEC_BASE_URL = "https://data.sec.gov/submissions/"
HEADERS = {
    "User-Agent": "AbhyudayaLohani-FinancialAnalystCopilot (abhyudaya.lohani@example.com)"
}

def get_company_filings(ticker: str, count: int = 2):
    """
    Fetch recent 10-K and 10-Q filings for a given company ticker.
    Default example: Apple (AAPL)
    """
    cik_map = {"aapl": "0000320193"}  # Add more tickers as needed later
    cik = cik_map.get(ticker.lower())
    if not cik:
        raise ValueError(f"Ticker {ticker} not found in CIK map.")

    print(f"📡 Fetching recent filings metadata for {ticker.upper()}...")
    cik_url = f"{SEC_BASE_URL}CIK{cik}.json"
    resp = requests.get(cik_url, headers=HEADERS)
    data = resp.json()

    accession_numbers = data["filings"]["recent"]["accessionNumber"][:count]
    docs = []

    for acc in accession_numbers:
        acc_clean = acc.replace("-", "")
        filing_folder = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_clean}/"

        print(f"\n🔍 Looking for filing documents in: {filing_folder}")
        index_res = requests.get(filing_folder, headers=HEADERS)
        if index_res.status_code != 200:
            print(f"⚠️ Could not access index for {acc}")
            continue

        soup = BeautifulSoup(index_res.text, "html.parser")
        hrefs = [
            a.get("href")
            for a in soup.find_all("a")
            if a.get("href") and a.get("href").endswith(".htm")
        ]
        if not hrefs:
            print(f"⚠️ No .htm files found for {acc}")
            continue

        # 🔎 Smart logic to find the real 10-K or 10-Q filing
        filing_url = None
        for href in hrefs:
            href_lower = href.lower()
            if "10-k" in href_lower or "10q" in href_lower or "10-q" in href_lower:
                filing_url = f"https://www.sec.gov{href}" if href.startswith("/") else f"https://www.sec.gov/Archives/{href}"
                break

        # If still not found, choose the largest .htm file (likely the main filing)
        if not filing_url:
            # Fetch file sizes by head requests (lightweight)
            file_sizes = {}
            for href in hrefs:
                try:
                    url = f"https://www.sec.gov{href}" if href.startswith("/") else f"https://www.sec.gov/Archives/{href}"
                    head = requests.head(url, headers=HEADERS)
                    size = int(head.headers.get("Content-Length", 0))
                    file_sizes[url] = size
                except Exception:
                    continue
            if file_sizes:
                filing_url = max(file_sizes, key=file_sizes.get)

        if not filing_url:
            print(f"⚠️ Could not find valid filing file for {acc}")
            continue

        print(f"📄 Found main filing: {filing_url}")

        # === Retry Logic for Download ===
        for attempt in range(3):
            try:
                res = requests.get(filing_url, headers=HEADERS, timeout=15)
                if res.status_code == 200:
                    raw_path = os.path.join(RAW_DIR, f"{ticker.upper()}_{acc_clean}.html")
                    with open(raw_path, "w", encoding="utf-8") as f:
                        f.write(res.text)
                    docs.append(raw_path)
                    print(f"✅ Downloaded filing: {filing_url}")
                    break
                else:
                    print(f"⚠️ Attempt {attempt+1}: HTTP {res.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Attempt {attempt+1}: Error - {e}")
            time.sleep(2)
        else:
            print(f"❌ Skipped after 3 failed attempts.")

    return docs


def clean_filing(file_path: str):
    """
    Convert raw HTML filing to clean plain text.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    clean_text = " ".join(text.split())

    filename = os.path.basename(file_path).replace(".html", ".txt")
    save_path = os.path.join(PROCESSED_DIR, filename)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(clean_text)

    print(f"🧹 Cleaned and saved: {save_path}")
    return save_path


def run_pipeline(ticker="AAPL", count=2):
    """
    Run the full ETL pipeline: fetch → clean → save
    """
    print(f"🚀 Starting ETL pipeline for {ticker.upper()}")
    files = get_company_filings(ticker, count)
    if not files:
        print("⚠️ No valid filings found or downloaded.")
        return
    processed_files = [clean_filing(f) for f in files]
    print(f"\n✅ ETL completed. Processed filings:\n{processed_files}")


if __name__ == "__main__":
    run_pipeline("AAPL", count=2)
