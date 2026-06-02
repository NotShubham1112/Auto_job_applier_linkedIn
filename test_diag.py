"""Diagnostic: load app, check every screen state, type a message, see what happens."""
import asyncio
import sys
sys.path.insert(0, '.')

from cli.textual_app import build_app


async def test():
    app = build_app(skip_db=True)
    async with app.run_test(headless=True, size=(140, 42)) as pilot:
        # Step 1: wait for boot to finish
        await pilot.pause(3.0)
        print(f"=== After boot, screen stack: {[type(s).__name__ for s in app.screen_stack]}")
        print(f"=== Current screen: {type(app.screen).__name__}")

        # Step 2: find the input
        try:
            inp = app.screen.query_one('#input-box')
            print(f"=== Input found: {type(inp).__name__}, placeholder={inp.placeholder!r}, value={inp.value!r}")
        except Exception as e:
            print(f"=== Input not found: {e}")
            return

        # Step 3: focus and type
        inp.focus()
        await pilot.pause(0.3)
        for ch in 'hello world test':
            await pilot.press(ch)
        await pilot.pause(0.3)
        print(f"=== After typing, value={inp.value!r}, has_focus={inp.has_focus}")

        # Step 4: submit
        await pilot.press('enter')
        await pilot.pause(0.5)
        print(f"=== After enter, value={inp.value!r}")

        # Step 5: find chat output
        co = None
        for w in app.screen.walk_children():
            if type(w).__name__ == 'StreamingOutput':
                co = w
                break
        if co is None:
            print("=== StreamingOutput not found")
        else:
            print(f"=== StreamingOutput found")
            print(f"    _active_role: {co._active_role!r}")
            print(f"    _active_buffer: {co._active_buffer!r}")
            print(f"    lines written: {co.line_count if hasattr(co, 'line_count') else 'n/a'}")
            # Try internal lines
            for attr in ['_lines', 'lines', '_wrapped_lines']:
                if hasattr(co, attr):
                    val = getattr(co, attr)
                    print(f"    {attr}: type={type(val).__name__} len={len(val) if hasattr(val, '__len__') else 'n/a'}")
                    if hasattr(val, '__iter__') and len(val) > 0:
                        print(f"      first: {str(val[0])[:100]!r}")

        # Step 6: pause more and check final state
        await pilot.pause(2.0)
        app.save_screenshot('diag1.svg')
        print("=== Saved diag1.svg")


asyncio.run(test())
