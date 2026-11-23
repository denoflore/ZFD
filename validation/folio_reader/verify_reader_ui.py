#!/usr/bin/env python3
"""Optional browser acceptance for the committed f88r example (Playwright)."""

import argparse
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.html.resolve()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    receipt = {
        'html_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'page_errors': [],
        'desktop_viewport': {'width': 1440, 'height': 1050},
        'mobile_viewport': {'width': 390, 'height': 844},
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        receipt['browser_version'] = browser.version
        page = browser.new_page(viewport=receipt['desktop_viewport'], device_scale_factor=1)
        page.on('pageerror', lambda error: receipt['page_errors'].append(str(error)))
        page.goto(source.as_uri(), wait_until='domcontentloaded')
        page.wait_for_function("document.getElementById('manuscript-image').complete", timeout=20000)
        receipt['title'] = page.title()
        receipt['image'] = page.locator('img').evaluate_all(
            '(imgs)=>imgs.map(x=>({src:x.src,loaded:x.complete&&x.naturalWidth>0,width:x.naturalWidth}))')
        assert receipt['image'] and all(item['loaded'] for item in receipt['image'])
        assert page.locator('.token-record').count() == 150
        page.locator('#token-search').fill('f88r.6.1')
        assert page.locator('.token-record:not([hidden])').count() == 1
        receipt['search_by_token_id'] = True
        page.locator('#reset-filter').click()
        page.locator('#match-filter').select_option('partial')
        assert page.locator('.token-record:not([hidden])').count() == 81
        receipt['partial_filter_count'] = 81
        page.locator('#match-filter').select_option('unresolved')
        assert page.locator('#no-results').is_visible()
        receipt['empty_filter_state'] = True
        page.locator('#reset-filter').click()
        page.locator('#expand-evidence').click()
        assert page.locator('details.token-record[open]').count() == 150
        receipt['expand_evidence'] = True
        page.locator('#expand-evidence').click()
        page.set_viewport_size(receipt['mobile_viewport'])
        receipt['mobile_overflow'] = page.evaluate('document.documentElement.scrollWidth>innerWidth')
        assert not receipt['mobile_overflow']
        offline = browser.new_page(viewport=receipt['desktop_viewport'])
        offline.on('pageerror', lambda error: receipt['page_errors'].append(str(error)))
        offline.route('https://collections.library.yale.edu/iiif/**', lambda route: route.abort())
        offline.goto(source.as_uri(), wait_until='networkidle')
        receipt['image_failure_fallback'] = offline.locator('#image-fallback').is_visible()
        assert receipt['image_failure_fallback']
        assert not receipt['page_errors'], receipt['page_errors']
        browser.close()
    args.output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
