\
import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
import pdfplumber
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_DIR = DATA_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

PROGRAM_URLS = {
    "master_ai": "https://abit.itmo.ru/program/master/ai",
    "master_ai_product": "https://abit.itmo.ru/program/master/ai_product",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ITMO-bot/1.0)"}

def fetch_url(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def save_text(name: str, content: str):
    (RAW_DIR / f"{name}.html").write_text(content, encoding="utf-8")

def visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())
    return text

def find_pdf_links(html: str, base_url: str):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            if href.startswith("http"):
                links.append(href)
            else:
                # на случай относительных ссылок
                if href.startswith("/"):
                    from urllib.parse import urljoin
                    links.append(urljoin(base_url, href))
                else:
                    links.append(base_url.rstrip("/") + "/" + href)
    return list(dict.fromkeys(links))  # unique

def download_file(url: str, out_path: Path):
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    out_path.write_bytes(r.content)

def parse_pdf_courses(pdf_path: Path):
    """Best-effort парсер: вытягивает таблицы и ищет похожие на названия дисциплин строки"""
    courses = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # таблицы
                try:
                    tables = page.extract_tables()
                except Exception:
                    tables = []
                for tbl in tables or []:
                    for row in tbl:
                        row_text = " | ".join([c.strip() if isinstance(c, str) else "" for c in row])
                        if len(row_text) < 5:
                            continue
                        # эвристика: строки с предметами часто содержат буквы и нет длинных чисел
                        if re.search(r"[А-Яа-яA-Za-z]", row_text) and not re.search(r"^\d{3,}$", row_text):
                            courses.append({"name": row_text[:120]})
                # текст
                text = page.extract_text() or ""
                for line in text.splitlines():
                    line = line.strip()
                    if 4 < len(line) < 120 and re.search(r"[А-Яа-яA-Za-z]", line):
                        # отсекать шапки / служебные
                        if not re.search(r"(Семестр|Кредиты|ЗЕТ|Часы|Итого|Трудоемкость)", line, flags=re.I):
                            courses.append({"name": line})
    except Exception as e:
        print(f"[WARN] PDF parse failed for {pdf_path.name}: {e}")
    # дедуп
    uniq = []
    seen = set()
    for c in courses:
        key = c["name"]
        if key not in seen:
            seen.add(key)
            uniq.append(c)
    return uniq[:300]  # ограничим

def main():
    programs = []
    for pid, url in PROGRAM_URLS.items():
        print(f"[*] Fetch {pid}: {url}")
        html = fetch_url(url)
        save_text(pid, html)
        text = visible_text(html)

        # найти PDF планы
        pdfs = find_pdf_links(html, url)
        print(f"    found {len(pdfs)} pdfs")
        all_courses = []
        for i, pdf_url in enumerate(pdfs):
            out = RAW_DIR / f"{pid}_plan_{i+1}.pdf"
            try:
                print(f"    download {pdf_url}")
                download_file(pdf_url, out)
                parsed = parse_pdf_courses(out)
                if parsed:
                    all_courses.extend(parsed)
            except Exception as e:
                print(f"[WARN] can't download/parse {pdf_url}: {e}")

        # сформируем summary (коротко)
        summary = " ".join(text.split()[:200])

        programs.append({
            "id": pid,
            "title": f"Программа {pid.replace('_', ' ').title()}",
            "url": url,
            "summary": summary,
            "courses": all_courses[:200],
            "electives": all_courses[:80]  # временно: без точного деления, электivy = подмножество
        })
        time.sleep(1)

    out_json = DATA_DIR / "programs.json"
    out_json.write_text(json.dumps({"programs": programs}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Saved {out_json}")

if __name__ == "__main__":
    main()
