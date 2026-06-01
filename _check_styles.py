import re
files = [
    'ui/components.py', 'ui/styles.py',
    'plugins/help_plugin.py', 'plugins/jobhunt_plugin.py',
    'plugins/search_plugin.py', 'plugins/status_plugin.py',
    'plugins/jobs_plugin.py', 'plugins/interviews_plugin.py',
    'plugins/history_plugin.py', 'plugins/resume_plugin.py',
    'plugins/coverletter_plugin.py', 'plugins/settings_plugin.py',
    'plugins/chat_plugin.py', 'plugins/agent_plugin.py', 'plugins/apply_plugin.py',
    'chat/engine.py', 'chat/router.py', 'cli/app.py',
]
old_tokens = {'score_high', 'score_mid', 'score_low'}
found = False
for f in files:
    with open(f, encoding='utf-8') as fp:
        content = fp.read()
    for m in re.finditer(r'style="([^"]+)"', content):
        style = m.group(1)
        for token in style.split():
            if token in old_tokens:
                ln = content[:m.start()].count('\n') + 1
                print(f'{f}:{ln}: style="{style}" has OLD token "{token}"')
                found = True
if not found:
    print('No old style tokens found.')
