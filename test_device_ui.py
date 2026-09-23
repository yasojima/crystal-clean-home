from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import re
import subprocess

root = Path(__file__).parent
paths = json.loads((root/'source/device/manifest.json').read_text())
for name in paths:
    entry = (root/'docs'/name).read_text(encoding='utf-8')
    assert '(min-width:993px)' in entry and '(max-width:992px)' in entry, name
    for device, other in [('desktop','mobile'),('mobile','desktop')]:
        source = root/'source/device'/device/'css'/name
        output = root/'docs/device'/device/'css'/name
        assert source.is_file() and output.is_file(), name
        text = output.read_text(encoding='utf-8')
        assert '/device/'+other+'/' not in text, name
        for css in re.findall(r'/crystal-clean-home/device/[^"\s)]+\.css', text):
            assert (root/'docs'/css.removeprefix('/crystal-clean-home/')).is_file(), css
for device in ['desktop','mobile']:
    assert json.loads((root/'source/device'/device/'images.json').read_text(encoding='utf-8'))
footer = (root/'brand/shared-ui/footer.html').read_text(encoding='utf-8')
files = subprocess.check_output(['git','ls-files','docs/*.html','docs/**/*.html'],cwd=root,text=True).splitlines()
def check(name):
    text = (root/name).read_text(encoding='utf-8')
    if 'cch-header' not in text:
        return 0
    assert footer in text, name
    assert text.count('data-device-images') == 1, name
    assert text.count('data-shared-ui="style"') == 1, name
    assert 'data-cch-page="'+('home' if name=='docs/index.html' else 'inner')+'"' in text, name
    assert not re.search(r'id=["\']fixed_side|class=["\'](?:simulation_btn|fix_bottom)["\']',text),name
    return 1
with ThreadPoolExecutor(max_workers=16) as pool:
    count = sum(pool.map(check,files))
home = (root/'docs/index.html').read_text(encoding='utf-8')
assert not re.search(r'iekire|osoujihonpo|おそうじ本舗|お掃除本舗|イエキレ|家キレイ',home,re.I)
assert '<!-- cch-hero:start -->' in home
print(f'PASS: {len(paths)} CSS entries, isolated PC/SP imports, {count} shared UI pages, clean home metadata')
