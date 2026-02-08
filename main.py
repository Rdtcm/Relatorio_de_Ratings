"""
This code get informations about rating actions with playwright and gives
an PDF with the informations given from web page.
"""
import scrapping_rating_actions
import generate_pdf
import subprocess
import sys


def ensure_playwright_browser():
    # Install Chromium if necessary
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        print("Falha ao instalar Chromium do Playwright.")



def main():
    ensure_playwright_browser() 
    data = scrapping_rating_actions.run_scraper()
    return generate_pdf.GeneratePDF.generate_pdf(data)


if __name__ == "__main__":
    main()
