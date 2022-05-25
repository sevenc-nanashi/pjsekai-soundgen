import audioop
import gzip
import io
import json
import sys
import time
from urllib.parse import quote

import pydub
import requests
from tqdm import tqdm

from type import LevelData, LevelList

SOUND_MAP = {
    3: "perfect",
    4: "flick",
    5: "sperfect",
    6: "tick",
    7: "sperfect",
    8: "flick",
    10: "critical_tap",
    11: "critical_flick",
    12: "sperfect",
    13: "critical_tick",
    14: "sperfect",
    15: "critical_flick",
}


def overlay_without_sync(seg1, seg2, position):
    output = io.BytesIO()
    sample_width = seg1.sample_width
    spawn = seg1._spawn

    output.write(seg1[:position]._data)

    # drop down to the raw data
    bseg1 = seg1[position:]._data
    bseg2 = seg2._data
    pos = 0
    seg_max = max(len(bseg1), len(bseg2))
    bseg1 = bseg1.ljust(seg_max, b"\x00")
    bseg2 = bseg2.ljust(seg_max, b"\x00")
    output.write(audioop.add(bseg1[pos : pos + seg_max], bseg2, sample_width))
    pos += seg_max
    output.write(bseg1[pos:])

    return spawn(data=output)


def overlay_without_sync_loop(seg1, seg2, start, end):
    output = io.BytesIO()
    sample_width = seg1.sample_width
    spawn = seg1._spawn

    output.write(seg1[:start]._data)
    seg2_len = len(seg2)

    # drop down to the raw data
    # bseg1 = seg1[start:]._data
    # bseg2 = seg2._data
    pos = start
    while end > pos:
        current_len = min(seg2_len, end - pos)
        bseg1 = seg1[pos : pos + current_len]._data
        bseg2 = seg2[:current_len]._data
        seg_len = min(len(bseg1), len(bseg2))
        bseg1 = bseg1[:seg_len]
        bseg2 = bseg2[:seg_len]
        output.write(audioop.add(bseg1, bseg2, sample_width))
        pos += seg2_len
    output.write(seg1[end:]._data)

    return spawn(data=output)


def sync_segment(seg1, seg2):
    return seg2.set_channels(seg1.channels).set_frame_rate(seg1.frame_rate).set_sample_width(seg1.sample_width)


def color_escape(color: int):
    r, g, b = color // 65536, (color // 256) % 256, color % 256
    return f"\033[38;2;{r};{g};{b}m"


print(
    f"""
{color_escape(0x00bbd0)}== pjsekai-soundgen -----------------------------------------------------------\033[m
    {color_escape(0x00afc7)}pjsekai-soundgen / プロセカ風譜面音声生成ツール\033[m
    Version: {color_escape(0x0f6ea3)}0.1.0\033[m
    Developed by {color_escape(0x48b0d5)}名無し｡(@sevenc-nanashi)\033[m
    https://github.com/sevenc-nanashi/pjsekai-soundgen
{color_escape(0xff5a91)}-------------------------------------------------------------------------------\033[m
""".strip()
)


volume = 0.5
session = requests.Session()
if len(sys.argv) < 2:
    name = input("曲名を入力してください: ")
    keywords = quote(name.encode("utf-8"))
    levels: LevelList = session.get(f"https://servers-legacy.purplepalette.net/levels/list?keywords={keywords}").json()

    if not levels["items"]:
        exit("曲が見つかりませんでした。")

    print("曲を選択して下さい: \n")
    for i, level in enumerate(levels["items"]):
        print(f"{i + 1}) {level['title']} / {level['author']} #{level['name']}")
    print("")
    while True:
        index = input("> ")
        try:
            index = int(index)
            level = levels["items"][index - 1]
            break
        except (ValueError, IndexError):
            pass
else:
    level_id = sys.argv[1]
    level_resp = session.get(f"https://servers-legacy.purplepalette.net/levels/{level_id}")
    if level_resp.status_code != 200:
        exit(f"{level_id} は存在しません。")
    level = level_resp.json()["item"]
print(f"{level['title']} / {level['author']} #{level['name']} を選択しました。")

total_time = time.time()
bgm_data = session.get("https://servers.purplepalette.net" + level["bgm"]["url"]).content
bgm = pydub.AudioSegment.from_file(io.BytesIO(bgm_data)).apply_gain(0.5)
SEG_MAP = {
    name: sync_segment(bgm, pydub.AudioSegment.from_mp3(f"./sounds/{name}.mp3")).apply_gain(volume)
    for name in SOUND_MAP.values()
}

CONNECT_SEG = {
    9: sync_segment(bgm, pydub.AudioSegment.from_mp3("./sounds/connect.mp3")).apply_gain(volume),
    16: sync_segment(bgm, pydub.AudioSegment.from_mp3("./sounds/connect_critical.mp3")).apply_gain(volume),
}

chart_data_gzip = session.get("https://servers.purplepalette.net" + level["data"]["url"]).content
chart_data: LevelData = json.loads(gzip.decompress(chart_data_gzip).decode("utf-8"))
print("音声を合成中...")
single_sounds = set()
hold_sounds = {9: [], 16: []}
for i, entity in enumerate(chart_data["entities"], 1):
    if entity["archetype"] < 3:
        continue
    if entity["archetype"] in [9, 16]:
        hold_sounds[entity["archetype"]].append((1, round(entity["data"]["values"][0] * 1000)))
        hold_sounds[entity["archetype"]].append((-1, round(entity["data"]["values"][3] * 1000)))
    if SOUND_MAP.get(entity["archetype"]) is None:
        continue
    single_sounds.add((SOUND_MAP[entity["archetype"]], round(entity["data"]["values"][0] * 1000)))

start_time = time.time()
eta = "??:??"
print("単ノーツの音声を生成中:")
for sound, position in tqdm(single_sounds, unit="notes", colour="#8693f6"):
    bgm = overlay_without_sync(bgm, SEG_MAP[sound], position)

print("\n長押しノーツの音声を生成中:")
for ari, (archetype, slide_notes) in enumerate(hold_sounds.items(), 1):
    print(f"  {ari}/2")
    count = 0
    ranges = []
    slide_notes.sort(key=lambda x: (x[1], -x[0]))
    for diff, ntime in slide_notes:
        count += diff
        assert count >= 0
        if count == 1 and diff == 1:
            ranges.append([ntime, None])
        elif count == 0 and diff == -1:
            ranges[-1][1] = ntime
    assert count == 0

    eta = "??:??"
    start_time = time.time()
    for start, end in tqdm(ranges, unit="notes", colour=("#5be29c" if archetype == 9 else "#feb848")):
        bgm = overlay_without_sync_loop(bgm, CONNECT_SEG[archetype], start, end)
    print("")

print("音声を出力中...")
bgm.export(f"./dist/{level['name']}.mp3", format="mp3")
print(f"完了しました。音声は dist/{level['name']}.mp3 に出力されました。")
total_time = time.time() - total_time
print(f"合計時間: {int(total_time / 60)}:{int(total_time % 60):02d}")
