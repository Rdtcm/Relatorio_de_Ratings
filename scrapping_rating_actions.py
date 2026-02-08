from dataclasses import dataclass, asdict
from typing import List
from playwright.sync_api import sync_playwright, Page, TimeoutError
import re
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


SEARCH_URL = (
    "https://www.fitchratings.com/search?"
    "dateValue=lastWeek&expanded=racs&filter.sector=&"
    "filter.language=Portuguese&filter.region=&"
    "filter.country=&filter.reportType=Rating+Action+Commentary&"
    "filter.topic=&viewType=data"
)


@dataclass
class RatingRecord:
    agency: str
    company: str
    rating_current: str
    rating_previous: str
    outlook_current: str
    outlook_previous: str
    action: str
    date: str
    link: str



def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_result_rows(page: Page):
    logging.info("Abrindo página de busca...")
    page.goto(SEARCH_URL, timeout=60000)

    # espera container principal
    page.wait_for_selector(".frw-column__main")

    rows = page.locator(
        ".frw-column__main > .frw-article-data"
    )

    logging.info(f"{rows.count()} blocos encontrados.")

    return rows


def extract_basic_rows(page: Page):
    rows = load_result_rows(page)

    data = []
    total = rows.count()

    EMISSAO_KEYWORDS = [
        "debenture",
        "debênture",
        "issuance",
        "bond",
        "note",
        "emissão",
        "cri",
        "cra",
        "fidc",
        "cotas"
    ]

    for i in range(1, total):
        try:
            row = rows.nth(i)

            link_locator = row.locator(
                ".frw-article-data--title a"
            )

            if link_locator.count() == 0:
                continue

            title = link_locator.first.inner_text().lower()

            # ignora emissões
            if any(k in title for k in EMISSAO_KEYWORDS):
                logging.info(f"Ignorado (emissão): {title}")
                continue

            link = link_locator.first.get_attribute("href")
            if not link:
                continue

            day = row.locator(".frw-date__1").inner_text()
            month_year = row.locator(".frw-date__2").inner_text()

            date = clean_text(f"{day} {month_year}")

            data.append({
                "date": date,
                "link": f"https://www.fitchratings.com{link}"
            })

        except Exception as e:
            logging.exception(f"Erro linha {i}: {e}")

    logging.info(f"{len(data)} links coletados.")
    return data


def extract_agency(text: str) -> str:
    """
    Identifica a agência a partir do texto.
    Procura por agências conhecidas no conteúdo principal do relatório.
    """

    lower = text.lower()

    # Ordem por cobertura / prioridade
    if re.search(r"\bfitch\b", lower):
        return "Fitch Ratings"
    if re.search(r"moody['’]s", lower):
        return "Moody's"
    if re.search(r"s&p|standard and poor", lower):
        return "S&P Global Ratings"
    if re.search(r"\bdbrs\b", lower):
        return "DBRS Morningstar"
    if re.search(r"\bkbra\b", lower):
        return "KBRA"
    if re.search(r"a\.m\. best", lower):
        return "A.M. Best"
    if re.search(r"\bscope ratings\b", lower):
        return "Scope Ratings"

    return "-"



def parse_action_page(page: Page, url: str, date: str) -> RatingRecord:
    logging.info(f"Abrindo ação: {url}")

    page.goto(url, timeout=60000)

    # espera conteúdo principal
    page.wait_for_selector(".frw-RAC")

    raw_text = page.locator(".frw-RAC").inner_text()
    text = clean_text(raw_text)
    agency = extract_agency(raw_text)


    company, rating_prev, rating_curr = \
        extract_entity_and_ratings_from_table(page)

    # só usa fallback se NÃO houver na tabela
    if not company and not rating_curr:
        company = extract_company_from_title(page)

    if not company and not rating_curr:
        company = extract_company(text)

    if not rating_curr:
        rating_prev, rating_curr = extract_ratings(text)

    # rating_prev, rating_curr = extract_ratings(text)

    outlook_prev, outlook_curr = extract_outlook(text)
    action = extract_action(text)

    return RatingRecord(
        agency=agency,
        company=company,
        rating_current=rating_curr,
        rating_previous=rating_prev,
        outlook_current=outlook_curr,
        outlook_previous=outlook_prev,
        action=action,
        date=date,
        link=url,
    )



def extract_company(text: str) -> str:
    patterns = [
        r"ratings? .*? da (.+?)(?:,|;|\.)",
        r"rating .*? da (.+?)(?:,|;|\.)",
        r"rating .*? de (.+?)(?:,|;|\.)",
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if not m:
            continue

        company = clean_text(m.group(1)).split(",")[0]

        # remove descrições posteriores
        company = re.split(
            r"\s(e de sua|com perspectiva|com outlook|para|em)\s",
            company,
            flags=re.IGNORECASE
        )[0]

        # remove partes de emissão
        company = re.sub(
            r"\s*e de sua .*",
            "",
            company,
            flags=re.IGNORECASE
        )

        # corrige variações de S.A.
        company = re.sub(r"\bS\.?A?\.?$", "S.A.", company)

        # bloqueia se ainda parecer emissão
        if re.search(r"emiss[aã]o|deb[eê]nture", company, re.I):
            return ""

        return company.strip()

    return ""


def extract_company_from_title(page: Page) -> str:
    try:
        title = page.locator("h1").inner_text()
    except:
        return ""

    title = clean_text(title)

    patterns = [
        r"ratings? da ([^;,.]+)",
        r"rating da ([^;,.]+)",
        r"downgrades ([^;,.]+)",
        r"affirms ([^;,.]+)",
        r"upgrades ([^;,.]+)",
        r"assigns ([^;,.]+)",
        r"places ([^;,.]+)",
        r"revises ([^;,.]+)",
        r"publishes ([^;,.]+)",
    ]

    for p in patterns:
        m = re.search(p, title, re.IGNORECASE)
        if not m:
            continue

        company = m.group(1)

        company = re.split(
            r" ratings?| at | to | para | em ",
            company,
            flags=re.IGNORECASE
        )[0]

        company = clean_text(company)

        if re.search(r"emiss[aã]o|deb[eê]nture", company, re.I):
            return ""

        return company

    return ""


def extract_ratings(text: str):
    change = re.search(
        r"de\s+[‘']?([A-Za-z+\-]+\(bra\))[’']?\s+para\s+[‘']?([A-Za-z+\-]+\(bra\))[’']?",
        text,
        re.IGNORECASE
    )

    if change:
        return change.group(1), change.group(2)

    matches = re.findall(r"[‘']([A-Za-z+\-]+\(bra\))[’']", text)

    if len(matches) >= 2:
        return matches[1], matches[0]

    if len(matches) == 1:
        return "", matches[0]

    return "", ""


def extract_entity_and_ratings_from_table(page: Page):
    try:
        page.wait_for_selector(".rt-table", timeout=5000)
    except TimeoutError:
        return "", "", ""

    rows = page.locator(".rt-tbody .rt-tr-group")
    total = rows.count()

    for i in range(total):
        row = rows.nth(i)
        cells = row.locator(".rt-td")

        if cells.count() < 3:
            continue

        entity = clean_text(cells.nth(0).inner_text())
        rating_cell = clean_text(cells.nth(1).inner_text())
        prior_cell = clean_text(cells.nth(2).inner_text())

        entity_lower = entity.lower()

        # ignora dívidas
        if any(k in entity_lower for k in [
            "/", "bond", "note", "debenture",
            "debênture", "senior", "unsecured",
            "secured", "notes", "emissão",
            "emission", "debentures"
        ]):
            continue

        rating_match = re.search(
            r"\b(?:AAA|AA|A|BBB|BB|B|CCC|CC|C)[+\-]?\(bra\)", rating_cell)
        prior_match = re.search(
            r"\b(?:AAA|AA|A|BBB|BB|B|CCC|CC|C)[+\-]?\(bra\)",
            prior_cell
        )

        rating = rating_match.group(0) if rating_match else ""
        prior = prior_match.group(0) if prior_match else ""

        if entity and rating:
            return entity, prior, rating

    return "", "", ""


def extract_outlook(text: str):
    prev_match = re.search(
        r"de (Estável|Positiva|Negativa)",
        text,
        re.IGNORECASE
    )

    curr_match = re.search(
        r"para (Estável|Positiva|Negativa)",
        text,
        re.IGNORECASE
    )

    if not curr_match:
        curr_match = re.search(
            r"(?:Outlook|Perspectiva).*?(Estável|Positiva|Negativa)",
            text,
            re.IGNORECASE
        )

    prev = prev_match.group(1) if prev_match else ""
    curr = curr_match.group(1) if curr_match else ""

    return prev, curr


def extract_action(text: str) -> str:
    lower = text.lower()

    if "afirmou" in lower:
        return "Afirmado"
    if "elevou" in lower:
        return "Upgrade"
    if "rebaixou" in lower:
        return "Downgrade"
    if "atribuiu" in lower:
        return "Novo Rating"

    return "Outro"


# ----------------------------
# EXECUÇÃO
# ----------------------------
def run_scraper() -> List[RatingRecord]:
    records = []
    seen_links = set()
    seen_records = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        rows = extract_basic_rows(page)

        for row in rows:
            link = row["link"]

            # evita processar link duplicado
            if link in seen_links:
                logging.info(f"Link duplicado ignorado: {link}")
                continue

            seen_links.add(link)

            try:
                record = parse_action_page(
                    page,
                    link,
                    row["date"]
                )
                # ignora registros sem empresa válida
                if not record.company:
                    logging.info("Registro sem empresa ignorado.")
                    continue

                record_key = (
                    record.company,
                    record.rating_current,
                    record.action,
                )

                if record_key in seen_records:
                    logging.info("Registro duplicado ignorado.")
                    continue

                seen_records.add(record_key)
                records.append(record)

            except Exception:
                logging.warning("Registro ignorado.")

        browser.close()

    return records


if __name__ == "__main__":
    data = run_scraper()

    for r in data:
        print(asdict(r))
