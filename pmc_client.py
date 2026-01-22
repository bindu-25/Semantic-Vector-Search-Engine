# pmc_client.py
"""
PMC Client

Responsibilities:
- Search Europe PMC for open-access articles
- Fetch full-text XML from NCBI efetch
- Extract meaningful text sections from articles

"""

import os
import requests
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional

# ---------------- ENDPOINTS ----------------
EPMC_SEARCH_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
NCBI_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# ---------------- LOCAL XML CACHE ----------------
PMC_CACHE_DIR = os.path.join("data", "pmc_cache")
os.makedirs(PMC_CACHE_DIR, exist_ok=True)


# ---------------- UTILITIES ----------------
def _normalize_pmcid(val: str) -> str:
    if not val:
        return ""
    v = str(val).strip().upper()
    if v.startswith("PMC"):
        return v
    if v.isdigit():
        return "PMC" + v
    return ""


def _xml_cache_path(pmcid: str) -> str:
    return os.path.join(PMC_CACHE_DIR, f"{pmcid}.xml")


def _text(elem: Optional[ET.Element]) -> str:
    if elem is None:
        return ""
    return " ".join(elem.itertext()).strip()


# ---------------- SEARCH ----------------
def search_pmc(query: str, max_papers: int = 10, timeout: int = 15) -> List[str]:
    """
    Search Europe PMC for open-access articles.
    Returns a list of normalized PMCIDs.
    """
    params = {
        "query": f"({query}) AND OPEN_ACCESS:Y",
        "format": "json",
        "pageSize": max_papers,
        "resultType": "core",
    }

    resp = requests.get(EPMC_SEARCH_URL, params=params, timeout=timeout)
    resp.raise_for_status()

    results = resp.json().get("resultList", {}).get("result", [])

    pmcids = []
    seen = set()

    for item in results:
        raw = item.get("pmcid") or item.get("id")
        pmcid = _normalize_pmcid(raw)
        if pmcid and pmcid not in seen:
            seen.add(pmcid)
            pmcids.append(pmcid)

    return pmcids[:max_papers]


# ---------------- FETCH ----------------
def fetch_pmc_xml(
    pmcid: str,
    timeout: int = 20,
    use_cache: bool = True
) -> Optional[ET.Element]:
    """
    Fetch PMC article XML using NCBI efetch.
    Cached locally to avoid repeated network calls.
    """
    pmc = _normalize_pmcid(pmcid)
    if not pmc:
        return None

    cache_path = _xml_cache_path(pmc)

    if use_cache and os.path.exists(cache_path):
        try:
            return ET.fromstring(open(cache_path, "rb").read())
        except Exception:
            pass  # fall through to re-fetch

    params = {
        "db": "pmc",
        "id": pmc.replace("PMC", ""),
        "retmode": "xml"
    }

    try:
        resp = requests.get(NCBI_EFETCH_URL, params=params, timeout=timeout)
        resp.raise_for_status()
        xml_bytes = resp.content

        try:
            with open(cache_path, "wb") as f:
                f.write(xml_bytes)
        except Exception:
            pass

        return ET.fromstring(xml_bytes)
    except Exception:
        return None


# ---------------- EXTRACT ----------------
def extract_sections(root: Optional[ET.Element]) -> List[Tuple[str, str]]:
    """
    Extract readable sections from a PMC article.
    Returns a list of (section_title, section_text).
    """
    if root is None:
        return []

    body = root.find(".//body")
    if body is None:
        return []

    sections = []

    for sec in body.findall(".//sec"):
        title = _text(sec.find("title")) or "Section"
        text = _text(sec)
        if text:
            sections.append((title, text))

    if sections:
        return sections

    # Fallback: paragraph-level extraction
    for p in body.findall(".//p"):
        text = _text(p)
        if text:
            sections.append(("Paragraph", text))

    return sections
