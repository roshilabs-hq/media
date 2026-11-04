# מנוע קליי מקובץ תוכנית (משימה 142, 4.11): spec.json -> קומפוזיציית HyperFrames + שער לגריד.
#   python clay.py <spec.json> <workdir> [--no-render]
# workdir: voice/01.wav..NN.wav (שורה לכל סצנה, כולל שער הסיום), icons/*.png. פלט: build/, video.mp4, cover.jpg.
# spec: title, series, num, name, next, scenes=[[html, "light"|"dark"], ...]. שער הסיום והחתימה נבנים מהשדות (החלטות #212, #215).
import json, os, shutil, subprocess, sys

ENGINE = 'C:/projects/reel-agent/engine'
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
GAP, T0 = 0.3, 0.4
MARK = ('<svg class="mk" viewBox="100 118 296 278" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><g stroke-linecap="round" fill="none">'
        '<g stroke="#2e2e33" stroke-width="30"><line x1="150" y1="150" x2="150" y2="362"/><line x1="214" y1="150" x2="214" y2="362"/>'
        '<line x1="278" y1="150" x2="278" y2="362"/><line x1="342" y1="150" x2="342" y2="362"/></g>'
        '<line x1="118" y1="378" x2="378" y2="136" stroke="#c2261a" stroke-width="32"/></g></svg>')
BRAND = MARK + '<span>רושינוביץ · אוטומציה לעסקים</span>'

CSS = '''@font-face{font-family:Heebo;src:url(assets/heebo-var-hebrew.woff2);font-weight:100 900}
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;overflow:hidden;background:#efece4}
#root{position:relative;width:100%;height:100%;overflow:hidden;font-family:Heebo,sans-serif;direction:rtl}
.clip{position:absolute;inset:0}
#sun{position:absolute;inset:-40%;background:repeating-conic-gradient(from 0deg at 50% 50%,rgba(194,38,26,.05) 0 5deg,transparent 5deg 10deg)}
#vig{position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,transparent 35%,#efece4 85%)}
.scene{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;padding:300px 86px 300px;gap:64px;color:#1a1a18}
.dark{background:radial-gradient(circle at 50% 52%,#7a2216 0%,#2a1310 40%,#1a1a18 72%);color:#efece4}
.t{font-weight:900;font-size:104px;line-height:1.18;text-align:center}
.w{display:inline-block}
.hl{color:#c2261a}.dark .hl{color:#ff6a4d}
.ic{width:540px;height:auto;filter:drop-shadow(0 43px 43px rgba(0,0,0,.22));margin-top:auto}
.pill{margin-bottom:auto;background:#1a1a18;color:#efece4;font-weight:800;font-size:60px;white-space:nowrap;padding:17px 48px;border-radius:32px;box-shadow:0 22px 43px rgba(0,0,0,.2)}
.dark .pill{background:#c2261a}
.stack{position:relative;width:540px;height:540px;margin-top:auto}
.stack img{position:absolute;inset:0;width:100%;filter:drop-shadow(0 32px 32px rgba(0,0,0,.2))}
.meter{position:absolute;left:-150px;bottom:0;width:34px;height:475px;border-radius:22px;background:#1a1a18}
.meter i{position:absolute;inset:auto 0 0;height:8%;background:linear-gradient(#ff6a4d,#c2261a);border-radius:22px}
.meter b{position:absolute;bottom:-64px;left:50%;transform:translateX(-50%);font-size:37px;font-weight:500;white-space:nowrap;color:#63635b}
.bubble{margin-top:auto;background:#fff;border-radius:54px 54px 11px 54px;padding:43px 54px;font-weight:800;font-size:65px;box-shadow:0 26px 54px rgba(26,26,24,.14);text-align:center}
.bubble small{display:block;font-weight:500;font-size:45px;color:#63635b;margin-top:16px}
.ep{position:absolute;top:150px;left:0;right:0;margin:auto;width:max-content;background:#c2261a;color:#fff;font-weight:800;font-size:44px;padding:10px 32px;border-radius:40px}
.trio{margin-top:auto;display:flex;gap:40px}.trio div{display:flex;flex-direction:column;align-items:center;gap:18px}.trio img{width:270px;filter:drop-shadow(0 30px 30px rgba(0,0,0,.2))}.trio b{font-size:44px;font-weight:800;white-space:nowrap}
.cv{margin-top:auto;display:flex;flex-direction:column;align-items:center;gap:10px}.ep2{background:#c2261a;color:#fff;font-weight:800;font-size:64px;padding:12px 44px;border-radius:44px}.num{font-weight:900;font-size:250px;line-height:1.05;white-space:nowrap;color:#c2261a;letter-spacing:-.02em}.name{font-weight:900;font-size:130px;line-height:1.1}.brand{display:flex;align-items:center;gap:18px}.brand .mk{height:64px;width:auto;flex:none}
.sign{font-weight:800;font-size:50px;color:#63635b;letter-spacing:.04em;margin-bottom:auto}'''


def dur(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).strip())


def build(spec, d):
    SC = scenes(spec)
    out = os.path.join(d, 'build')
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.join(out, 'assets'))
    shutil.copytree(os.path.join(ENGINE, 'hf', 'assets', 'js'), os.path.join(out, 'assets', 'js'))
    shutil.copy('C:/projects/GevaSchool/fonts/Heebo-var-hebrew.woff2', os.path.join(out, 'assets', 'heebo-var-hebrew.woff2'))  # OFL
    for f in os.listdir(os.path.join(d, 'icons')):
        shutil.copy(os.path.join(d, 'icons', f), os.path.join(out, 'assets', f))
    shutil.copy(os.path.join(ENGINE, 'music', 'bed-lightsail2.mp3'), os.path.join(out, 'assets', 'bed.mp3'))
    for f in ('pop.mp3', 'swipe.mp3', 'whoosh.mp3'):
        shutil.copy(os.path.join(ENGINE, 'sfx', 'ov', f), os.path.join(out, 'assets', f))

    t, times = T0, []
    for k in range(len(SC)):
        v = os.path.join(out, 'assets', f'v{k + 1:02d}.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(d, 'voice', f'{k + 1:02d}.wav'), '-af',
                        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse', v], check=True)
        dd = dur(v)
        times.append((t, dd))
        t += dd + GAP
    total = times[-1][0] + times[-1][1] + 1.4

    body, js, aud = [], [], []
    for k, ((html, kind), (st, dd)) in enumerate(zip(SC, times)):
        i = k + 1
        a = 0 if k == 0 else st - 0.35
        e = times[k + 1][0] - 0.2 if k + 1 < len(SC) else total
        body.append(f'<section id="s{i}" class="clip scene {kind}" data-start="{a:.2f}" data-duration="{e - a:.2f}" data-track-index="{1 + k % 2}">{html}</section>')
        if k:  # הכותרת הראשונה גלויה מהפריים הראשון: הוא תמונת התצוגה של הריל
            js.append(f'tl.from("#s{i} .w", {{ y: 120, opacity: 0, duration: 0.45, stagger: 0.1, ease: "back.out(1.8)" }}, {a + 0.05:.2f});')
        js.append(f'tl.from("#s{i} .ic, #s{i} .stack, #s{i} .bubble, #s{i} .cv", {{ scale: 0, rotation: -12, duration: 0.6, ease: "back.out(2.2)" }}, {a + 0.35:.2f});')
        js.append(f'tl.fromTo("#s{i} .ic", {{ y: 0 }}, {{ y: -27, duration: 1.4, yoyo: true, repeat: {max(int((e - a) / 1.4), 1)}, ease: "sine.inOut" }}, {a + 0.95:.2f});')
        js.append(f'tl.from("#s{i} .pill, #s{i} .sign", {{ scale: 0.4, opacity: 0, duration: 0.4, ease: "back.out(3)" }}, {min(a + 1.2, st + dd * 0.6):.2f});')
        if k + 1 < len(SC):
            js.append(f'tl.to("#s{i} > *", {{ y: -30, opacity: 0, duration: 0.3, ease: "power2.in" }}, {e - 0.3:.2f});')
        aud.append(f'<audio id="v{i:02d}" src="assets/v{i:02d}.wav" data-start="{st:.2f}" data-duration="{dd:.2f}" data-track-index="{10 + k}" data-volume="1"></audio>')
        aud.append(f'<audio id="fx{i}" src="assets/{"whoosh" if kind == "dark" else "pop"}.mp3" data-start="{a + 0.35:.2f}" data-duration="1" data-track-index="{30 + k}" data-volume="0.35"></audio>')
        if 'trio' in html:
            js.append(f'tl.from("#s{i} .trio > div", {{ scale: 0, opacity: 0, duration: 0.4, stagger: {dd / 3.2:.2f}, ease: "back.out(2.4)" }}, {a + 0.5:.2f});')
        if kind == 'dark':
            js.append(f'tl.fromTo("#s{i}", {{ clipPath: "circle(0% at 50% 55%)" }}, {{ clipPath: "circle(120% at 50% 55%)", duration: 0.6, ease: "power3.inOut" }}, {a:.2f});')
            js.append(f'tl.to("#s{i} .pill", {{ scale: 1.1, yoyo: true, repeat: 1, duration: 0.18 }}, {st + dd * 0.7:.2f});')
    aud.append(f'<audio id="bed" src="assets/bed.mp3" data-start="0" data-duration="{total:.2f}" data-track-index="9" data-volume="0.12"></audio>')
    js.append(f'tl.fromTo("#sun", {{ rotation: 0 }}, {{ rotation: {total * 9:.0f}, duration: {total:.2f}, ease: "none" }}, 0);')

    page = f'''<!doctype html>
<html lang="he" data-resolution="portrait"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920"><title>{spec['title']}</title>
<script src="assets/js/gsap-3.14.2.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{total:.2f}">
<section class="clip" data-start="0" data-duration="{total:.2f}" data-track-index="0"><div id="sun"></div><div id="vig"></div></section>
{chr(10).join(aud + body)}
</div>
<script>const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["main"] = tl;</script></body></html>'''
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(page)
    shutil.copy(os.path.join(ENGINE, 'news', 'hyperframes.json'), out)
    print(f'{len(SC)} סצנות, {total:.1f} שניות')
    return out



def cover_html(spec):
    return (f'<div class="cv"><div class="ep2">{spec["series"]}</div><div class="num">{spec["num"]}</div>'
            f'<div class="name">{spec["name"]}</div></div>')


def scenes(spec):
    return [tuple(x) for x in spec['scenes']] + [(cover_html(spec) + f'<div class="pill">{spec["next"]}</div><div class="sign brand">{BRAND}</div>', 'light')]


def cover(spec, d):
    """השער לגריד: אותו עיצוב כמו שער הסיום, בלי תווית הפרק הבא, 1080x1920 -> cover.jpg"""
    from PIL import Image
    out = os.path.join(d, 'build')
    html = os.path.join(out, 'cover.html')
    open(html, 'w', encoding='utf-8').write(
        f'<!doctype html><html lang="he"><head><meta charset="UTF-8"><style>{CSS}.cv{{margin:auto}}</style></head><body><div id="root">'
        f'<div id="sun" style="transform:rotate(8deg)"></div><div id="vig"></div><section class="scene">{cover_html(spec)}'
        f'<div class="sign brand" style="margin-bottom:auto;margin-top:60px">{BRAND}</div></section></div></body></html>')
    png = os.path.join(out, 'cover.png')
    if os.path.exists(png):
        os.remove(png)
    subprocess.run([EDGE, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                    '--window-size=1080,1920', f'--screenshot={png}', 'file:///' + html.replace(os.sep, '/')], check=True, timeout=60)
    import time
    for _ in range(60):  # Edge חוזר לפני שסיים לכתוב את הקובץ
        if os.path.exists(png) and os.path.getsize(png) > 1000:
            break
        time.sleep(0.5)
    im = Image.open(png).convert('RGB')
    assert im.size == (1080, 1920), im.size
    im.save(os.path.join(d, 'cover.jpg'), quality=92)


if __name__ == '__main__':
    spec = json.load(open(sys.argv[1], encoding='utf-8'))
    d = sys.argv[2]
    assert len(os.listdir(os.path.join(d, 'voice'))) >= len(spec['scenes']) + 1, 'חסרה קריינות: שורה לכל סצנה ועוד אחת לשער הסיום'
    out = build(spec, d)
    cover(spec, d)
    subprocess.run(['npx', '-y', 'hyperframes@0.8.46', 'check'], cwd=out, shell=os.name == 'nt', check=True)
    if '--no-render' not in sys.argv:
        subprocess.run(['npx', '-y', 'hyperframes@0.8.46', 'render', '--fps', '30', '--workers', '3', '-o', os.path.abspath(os.path.join(d, 'video.mp4'))], cwd=out, check=True, shell=os.name == 'nt')
