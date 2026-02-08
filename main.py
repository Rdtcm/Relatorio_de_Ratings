"""
This code get informations about rating actions with playwright and gives
an PDF with the informations given from web page.
"""

import scrapping_rating_actions
import generate_pdf


def main():
    data = scrapping_rating_actions.run_scraper()
    return generate_pdf.GeneratePDF.generate_pdf(data)


if __name__ == "__main__":
    main()
    
