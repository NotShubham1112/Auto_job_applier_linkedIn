import re
files = [
    'ui/components.py', 'ui/styles.py',
    'plugins/help_plugin.py', 'plugins/jobhunt_plugin.py',
    'plugins/search_plugin.py', 'plugins/status_plugin.py',
    'plugins/jobs_plugin.py', 'plugins/interviews_plugin.py',
    'plugins/history_plugin.py', 'plugins/resume_plugin.py',
    'plugins/coverletter_plugin.py', 'plugins/settings_plugin.py',
    'chat/engine.py', 'chat/router.py', 'cli/app.py',
]
for f in files:
    with open(f, encoding='utf-8') as fp:
        content = fp.read()
    for m in re.finditer(r'style="([^"]+)"', content):
        style = m.group(1)
        if 'bold' in style or 'score_' in style:
            line_no = content[:m.start()].count('\n') + 1
            print(f'{f}:{line_no}: style="{style}"')
