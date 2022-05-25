# pjsekai-soundgen / プロセカ風譜面音声生成ツール

pjsekai-soundgen は、[SweetPotato](https://potato.purplepalette.net)の譜面から音声を生成するツールです。

## 必須事項

- [Python 3.9 以上](https://www.python.org/downloads/)
- [PATH 上の ffmpeg](https://ffmpeg.org/)

## 利用方法

0. Python をインストールする。
1. `pip install poetry`で Poetry をインストールする。
2. `poetry install`で依存パッケージをインストールする。
3. `poetry run python main.py`で実行する。

## 注意

動画の概要欄などに、自分（=名無し｡）の

- 名前（`名無し｡`）
- Twitter のプロフィール
- このリポジトリへのリンク
- YouTube のチャンネル

が分かる文章を載せて下さい。

#### 例

```
プロセカ風譜面音声生成ツール：
  https://github.com/sevenc-nanashi/pjsekai-soundgen
  作成：名無し｡
  Twitter: https://twitter.com/sevenc_nanashi
  YouTube: https://youtube.com/channel/UCv9Wgrqn0ovYhUggSSm5Qtg
```

## 謝辞

sounds フォルダ内は[mkpoli/paletteworks](https://github.com/mkpoli/paletteworks)からのものです。

```
MIT License

Copyright (c) 2021 mkpoli

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

`overlay_without_sync`、`overlay_without_sync_loop`は[jiaaro/pydub](https://github.com/jiaaro/pydub)からのものです。

```
Copyright (c) 2011 James Robert, http://jiaaro.com

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
