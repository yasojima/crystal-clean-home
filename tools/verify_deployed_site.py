"""Check representative Pages responses against the retained source bytes."""
import hashlib
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://yasojima.github.io"
CATEGORIES = ["aircon", "pack", "water", "washer", "kitchen", "room", "coating", "others"]
PATHS = ["/", *[f"/house-cleaning/{name}/" for name in CATEGORIES],
         "/house-cleaning/aircon/wall/", "/contact/", "/policy/", "/sitemap.xml",
         "/assets/css/cart/complete.css", "/assets/js/common.js", "/assets/js/viewport-hud.js",
         "/assets/js/demo-contact.js", "/favicon/crystal-clean-home.svg",
         "/assets/images/crystal-clean-home.png",
         "/assets/images/footer/footer-phone-demo-pc.svg",
         "/assets/images/footer/footer-phone-demo-sp.svg",
         "/assets/images/top/kv/slider-pc_business.jpg",
         "/assets/images/header/estimate.svg",
         "/assets/font/campaign/font-awesome/fontawesome-webfont.woff2"]
EXCLUDED = ["/shop/", "/area/chiba-kashiwa/", "/guide/", "/promotion/",
            "/kajitatsu/", "/gift/", "/campaign/senzai02/",
            "/eco/", "/house-cleaning/", "/house-cleaning/faq/", "/house-cleaning/faq/1/",
            "/office/", "/business/", "/assets/images/about/eco-banner.webp",
            "/assets/images/logo.webp", "/favicon.ico",
            "/assets/images/top/pickup/img-app750.webp",
            "/assets/images/campaign/aircon-all-year/line_bnr.webp",
            "/assets/images/campaign/aircon-multiple-units/line_bnr.webp",
            "/info/news/", "/info/media/", "/info/media/9_12_nikkei_1/",
            "/business/partnership01/", "/campaign/super-sale/",
            "/campaign/cm2026/", "/campaign/dishwasher-air-cleaner/",
            "/campaign/policy-1/"]


def check(path):
    request = Request(ORIGIN + path, headers={"User-Agent": "CrystalCleanHome-DeploymentCheck/1.0"})
    try:
        with urlopen(request, timeout=45) as response:
            data = response.read()
            record = {"path": path, "status": response.status, "url": response.url}
        if path in EXCLUDED:
            return {**record, "expected_status": 404, "passed": False}
        local_path = path.lstrip("/") + ("index.html" if path.endswith("/") else "")
        local_hash = hashlib.sha256((ROOT / "source/site" / local_path).read_bytes()).hexdigest()
        response_hash = hashlib.sha256(data).hexdigest()
        return {**record, "sha256": response_hash,
                "passed": response.status == 200 and response_hash == local_hash and response.url == ORIGIN + path}
    except HTTPError as error:
        return {"path": path, "status": error.code, "passed": path in EXCLUDED and error.code == 404}
    except Exception as error:
        return {"path": path, "error": str(error), "passed": False}


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=4) as pool:
        checks = list(pool.map(check, PATHS + EXCLUDED))
    build = json.loads(subprocess.check_output(
        ["gh", "api", "repos/yasojima/yasojima.github.io/pages/builds/latest"], text=True))
    report = {
        "origin": ORIGIN + "/", "verified_at": datetime.now(timezone.utc).isoformat(),
        "pages_build_status": build["status"], "pages_commit": build["commit"],
        "source_tree": subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD:source/site"], text=True).strip(),
        "checks": checks,
        "passed": all(check["passed"] for check in checks) and build["status"] == "built",
        "scope": "Representative HTTP responses and excluded paths; backend and all-page visual acceptance are not included."
    }
    (ROOT / "source/deployment-verification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    raise SystemExit(0 if report["passed"] else 1)
