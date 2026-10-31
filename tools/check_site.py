"""Optional browser regression checks. No API calls; use an isolated browser context.

Start a static server first, then run with a Python environment containing Playwright:
  python tools/check_site.py --url http://127.0.0.1:8894 --chrome /path/to/chrome
Screenshots and the report go to ignored output/site-checks/.
"""
import argparse
import asyncio
import json
import re
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
COUNTS = {'review-four': 4, 'review-mini-four': 4, 'compare-ten': 10,
          'cycle-fifteen': 15, 'v5-parameterized': 10, 'v5-seventy': 70,
          'sympy-55': 55, 'rag-fifteen': 15, 'rag-hundred': 100, 'wildflower': 100}


async def check(url, chrome):
    output = ROOT / 'output/site-checks'
    output.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, **({'executable_path': chrome} if chrome else {}))
        context = await browser.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
        page = await context.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        await page.goto(url + '/')
        await page.wait_for_selector('.experiment-card')
        assert await page.locator('.experiment-card').count() == 10
        assert await page.locator('.history-tile').count() == 4
        assert await page.locator('.task-evidence').count() == 0
        scripts = await page.locator('script[src]').evaluate_all('(els)=>els.map(e=>e.getAttribute("src"))')
        assert not any('-data.js' in x for x in scripts), scripts
        assert await page.evaluate('db.cards.length') == 505
        assert not re.search('[А-Яа-яІіЇїЄє]', await page.locator('body').inner_text())
        await page.locator('#method-filter').select_option('rag')
        assert await page.locator('.experiment-card').count() == 2
        await page.locator('#method-filter').select_option('all')
        await page.screenshot(path=str(output / 'overview-desktop.png'))
        for width in [320, 390, 1440]:
            await page.set_viewport_size({'width': width, 'height': 900})
            assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth'), ('hub', width)
            if width == 390:
                await page.screenshot(path=str(output / 'overview-mobile.png'))

        for slug, count in COUNTS.items():
            await page.goto(url + '/experiment.html?id=' + slug)
            await page.wait_for_selector('.task-evidence')
            assert await page.locator('.task-evidence').count() == count, slug
            assert await page.locator('.math-fallback').count() == 0, slug
            scripts = await page.locator('script[src]').evaluate_all('(els)=>els.map(e=>e.getAttribute("src"))')
            assert sum('-data.js' in x for x in scripts) == 1, scripts
            await page.locator('#expand-tasks').click()
            assert await page.locator('.task-evidence[open]').count() == count
            assert not re.search('[А-Яа-яІіЇїЄє]', await page.locator('body').inner_text()), slug
            for width in [320, 390, 1440]:
                await page.set_viewport_size({'width': width, 'height': 900})
                assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (slug, width)
            if slug == 'rag-hundred':
                assert await page.locator('.math-block').count() == 294
                await page.locator('#expand-tasks').click()
                await page.screenshot(path=str(output / 'study-desktop.png'))

        for version in ['v1', 'v2', 'v3', 'v4']:
            await page.goto(url + '/experiment.html?id=cards-' + version)
            await page.wait_for_selector('.experiment-chart')
            assert not re.search('[А-Яа-яІіЇїЄє]', await page.locator('body').inner_text())
        await page.locator('a', has_text='Browse original cards').click()
        await page.wait_for_selector('#card-version')
        assert await page.locator('#card-version').input_value() == 'v4'
        assert await page.locator('tbody tr').count() == 25
        await page.locator('#search').fill('nonexistent-qa-question')
        assert await page.locator('tbody tr').count() == 0
        await page.locator('#search').fill('')
        await page.locator('[data-card]').first.click()
        assert await page.locator('#card-dialog').is_visible()
        await page.locator('#card-dialog [data-close]').click()

        # English edit fields must preserve untranslated evidence when unchanged.
        await page.goto(url + '/#versions')
        canonical = await page.evaluate('structuredClone(db.versions[0])')
        await page.locator('[data-edit="v1"]').click()
        assert await page.locator('#version-form [name=title]').input_value() == 'Initial baseline'
        await page.locator('#version-form [name=status]').select_option('accepted')
        await page.locator('#version-form [type=submit]').click()
        assert await page.evaluate('db.versions[0].title') == canonical['title']
        assert await page.evaluate('db.versions[0].notes') == canonical['notes']
        assert await page.evaluate('db.versions[0].status') == 'accepted'
        await page.goto(url + '/#issues')
        await page.wait_for_selector('[data-issue]')
        await page.locator('[data-issue]').first.select_option('retest')
        assert await page.evaluate('db.issues.some(i=>i.status==="retest")')

        # Seed the existing schema, including user edits, then cross the new pages.
        await page.evaluate('''() => {
          const seed=structuredClone(db);
          seed.versions[0].title='My existing custom title';
          seed.versions[0].prompt='<private-note> literal $x </private-note>';
          seed.issues[0].status='retest';
          localStorage.setItem(KEY,JSON.stringify(seed));
        }''')
        original = await page.evaluate('JSON.parse(localStorage.getItem(KEY))')
        await page.goto(url + '/experiment.html?id=rag-fifteen')
        await page.wait_for_selector('.task-evidence')
        assert await page.evaluate('db') == original
        await page.goto(url + '/#versions')
        await page.wait_for_selector('[data-edit]')
        assert 'My existing custom title' in await page.locator('main').inner_text()
        assert await page.evaluate('db') == original

        await page.locator('[data-edit="v1"]').click()
        assert await page.locator('#version-form [name=prompt]').input_value() == original['versions'][0]['prompt']
        await page.locator('#version-dialog [data-close]').first.click()
        await page.locator('#new-run').click()
        for key, value in {'id': 'qa-only', 'date': '2026-10-31', 'title': 'QA version', 'notes': 'Preserved after reload'}.items():
            await page.locator(f'#version-form [name={key}]').fill(value)
        await page.locator('#version-form [type=submit]').click()
        await page.reload()
        assert await page.evaluate('db.versions.at(-1).id') == 'qa-only'
        saved = await page.evaluate('db')

        async with page.expect_download() as dl:
            await page.locator('#backup').click()
        download = await dl.value
        export_path = await download.path()
        assert json.loads(Path(export_path).read_text(encoding='utf-8')) == saved
        await page.locator('#backup-file').set_input_files({'name': 'bad.json', 'mimeType': 'application/json', 'buffer': b'{"schema_version":999}'})
        await page.wait_for_timeout(100)
        assert await page.evaluate('db') == saved
        imported = json.loads(json.dumps(saved))
        imported['versions'][-1]['title'] = 'Imported update'
        await page.locator('#backup-file').set_input_files({'name': 'good.json', 'mimeType': 'application/json', 'buffer': json.dumps(imported).encode()})
        await page.wait_for_function('db.versions.at(-1).title === "Imported update"')
        assert await page.evaluate('db.cards.length') == 505
        assert len(await page.evaluate('db.versions')) == len(saved['versions'])

        # Existing CSV import and source scope editing must still work.
        await page.locator('#new-run').click()
        for key, value in {'id': 'qa-csv', 'date': '2026-10-31', 'title': 'CSV import'}.items():
            await page.locator(f'#version-form [name={key}]').fill(value)
        csv = b'set_topic,set_level,card_number,front_preview,self_contained_passes,faithfulness_ratio\nSets,L1,1,An imported question,1,1\n'
        await page.locator('#version-form [name=csv]').set_input_files({'name': 'cards_qa.csv', 'mimeType': 'text/csv', 'buffer': csv})
        await page.wait_for_selector('[data-scope]')
        await page.locator('[data-scope] [name=document]').fill('qa.pdf')
        await page.locator('[data-scope] [name=pages]').fill('1–2')
        await page.locator('#version-form [type=submit]').click()
        await page.wait_for_function('db.versions.at(-1).id === "qa-csv"')
        assert await page.evaluate('db.records.at(-1).document') == 'qa.pdf'
        assert await page.evaluate('db.records.at(-1).coverage') is None
        assert await page.evaluate('db.cards.length') == 506

        await page.goto(url + '/experiment.html?id=not-a-real-study')
        assert await page.locator('h1').inner_text() == 'Study not found.'
        await page.locator('main a').click()
        await page.wait_for_selector('.experiment-card')
        await page.go_back()
        assert await page.locator('h1').inner_text() == 'Study not found.'

        # file:// remains usable because lazy evidence is loaded through script tags.
        await page.goto((ROOT / 'experiment.html').as_uri() + '?id=v5-parameterized')
        await page.wait_for_selector('.task-evidence')
        assert await page.locator('.task-evidence').count() == 10
        assert not errors, errors
        await browser.close()
    report={'status':'passed','task_experiments':10,'historical_versions':4,'page_errors':errors,
            'widths':[320,390,1440],'persistence_import_export_csv':'passed','direct_file_open':'passed'}
    (output/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8894')
    parser.add_argument('--chrome')
    args=parser.parse_args()
    asyncio.run(check(args.url.rstrip('/'),args.chrome))
