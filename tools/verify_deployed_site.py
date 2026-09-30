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
         "/house-cleaning/aircon/wall/", "/sitemap.xml",
         "/assets/css/cart/complete.css", "/assets/js/common.js",
         "/favicon/apple-touch-icon-114x114.png",
         "/assets/images/top/kv/slider-pc_business.jpg",
         "/assets/images/header/estimate.svg",
         "/assets/font/campaign/font-awesome/fontawesome-webfont.woff2"]
EXCLUDED = ["/shop/", "/area/chiba-kashiwa/", "/guide/", "/promotion/",
            "/kajitatsu/", "/gift/", "/campaign/senzai02/"]


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
