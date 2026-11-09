# Variant G (Roi 9.11): F's picture (Sofi opening + series tag), WITHOUT the "write 'חוזר'" call,
# all narration after Sofi in the male voice of episode 1: scene 6 = tts 166 (was 167, Sofi's voice), ending = tts 168
# (already in B). Audio rebuilt from B's own parts on B's own timeline (index.html). End hold trimmed. 0 credits, no new TTS.
import os, subprocess, sys
OLD = 'C:/Users/alonr/AppData/Local/Temp/claude/dd2de14e0183b079/ac61ff91-5c52-4b7a-85f6-4f30a059c4d3/scratchpad/ep2'
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OLD)
from assemble import *  # P, ts, head, bubble, words, rrect, sections, run, dur, HDR, BED

sec = sections('B')
a2 = sec[2][0]
CUT7 = 31.08
END_VOICE = 31.43 + 6.55          # 168 ends here
TOTAL = round(END_VOICE + 1.0, 2)  # 1 s on the end card, like episode 1's tail

# --- subtitles: F's events minus the three "חוזר" lines
ev = []
ev.append(rf"Dialogue: 6,{ts(0)},{ts(CUT7)},Bub,,0,0,0,,{{\an5\pos(360,92)\p1\1c&H2D2DE8&\bord0\shad0}}{rrect(330, 50, 25)}{{\p0}}")
ev.append(rf"Dialogue: 7,{ts(0)},{ts(CUT7)},Tag,,0,0,0,,{{\an5\pos(360,93)\fs30\bord0}}חוזרים לבסיס · פרק 2")
head(ev, 0, a2, 'אותן שאלות.', 'כל יום.', y=200)
ws = words('157', 0.14)
for (x, y), wi, q, wd in [((600, 305), 0, 'מה המחיר?', 190), ((120, 305), 2, 'איפה אתם?', 190), ((600, 375), 4, 'יש תור מחר?', 210)]:
    bubble(ev, ws[wi][1], a2, x, y, q, wd)
ev.append(rf"Dialogue: 5,{ts(0.15)},{ts(2.6)},Tag,,0,0,0,,{{\pos(360,372)\fad(0,250)\fscx60\fscy60\t(0,160,\fscx100\fscy100)}}סוֹפִי")
open(P('G.ass'), 'w', encoding='utf-8').write(HDR + '\n'.join(ev) + '\n')

# --- 166 trimmed like the engine trims its voices (silence off both ends)
v6 = os.path.join(OUT, 'v06-166.wav')
run(['-i', P('tts', '166.wav'), '-af', 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
     'silenceremove=start_periods=1:start_threshold=-45dB,areverse', '-ar', '48000', v6])
assert dur(v6) <= 3.9, dur(v6)    # scene 6 has room until 31.43

A = P('B', 'build', 'assets')
parts = [  # (file, start, volume) = B's index.html, with v06 swapped
    (f'{A}/v01.wav', 0.40, 1), (f'{A}/pop.mp3', 0.35, .35), (f'{A}/v02.wav', 6.92, 1), (f'{A}/pop.mp3', 6.92, .35),
    (f'{A}/v03.wav', 9.57, 1), (f'{A}/pop.mp3', 9.57, .35), (f'{A}/v04.wav', 14.11, 1), (f'{A}/pop.mp3', 14.11, .35),
    (f'{A}/v05.wav', 21.77, 1), (f'{A}/whoosh.mp3', 21.77, .35), (v6, 27.48, 1), (f'{A}/pop.mp3', 27.48, .35),
    (f'{A}/v07.wav', 31.43, 1), (f'{A}/pop.mp3', 31.43, .35)]
inputs = ['-i', P('B', 'video.mp4'), '-i', P('clips', 's1.mp4')]
fc = (f"[0:v]trim=0:{TOTAL},setpts=PTS-STARTPTS[b];"
      f"[1:v]scale=1080:1920:flags=lanczos,setsar=1,fps=30,tpad=start_mode=clone:start_duration=0.14,trim=0:{a2:.3f}[h];"
      f"[b][h]overlay=enable='lt(t,{a2:.3f})':eof_action=pass[v];[v]subtitles=G.ass:fontsdir=../logo/fonts[vo];")
labels = []
for i, (f, t, vol) in enumerate(parts):
    inputs += ['-i', f]
    ms = int(t * 1000)
    fc += f"[{i + 2}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[a{i}];"
    labels.append(f'[a{i}]')
inputs += ['-i', f'{A}/bed.mp3']
fc += (f"[{len(parts) + 2}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{TOTAL},volume=0.12,"
       f"afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2[bed];")
fc += f"{''.join(labels)}[bed]amix=inputs={len(parts) + 1}:normalize=0,atrim=0:{TOTAL},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[ao]"
os.chdir(OLD)
out = os.path.join(OUT, 'ep2-G.mp4')
run([*inputs, '-filter_complex', fc, '-map', '[vo]', '-map', '[ao]', '-t', str(TOTAL), '-c:v', 'libx264', '-crf', '18',
     '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out])
print('G', dur(out), 'v06', round(dur(v6), 2), 'total', TOTAL)
