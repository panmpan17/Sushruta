# Susrhuta
Sprite sheet 是常在遊戲開發用的的技術，把小圖片和在一起變成大圖，壓縮 CPU 和記憶體使用。<br>
此專案是免費製作 Sprite sheet 的 UI 程式。

Sprite sheet is a technique use in game developer. <br>
Combine small images to big image, reduce the use of CPU and memory. <br>
This project is a free app that can produce spritesheet.

## Requirement
- Python
    - Pillow
    - TkOuter
    - PSD tools

## Execute
There's two way to execute the program, one is UI mode, another is console mode.<br>

UI start:

```
$ python controller ui
```

![UI](docs/demo-1.png)

### Console Mode
```
$ python controller console --help
```

#### Enviroment parameter

```
-i --images     | Add indivisual image
-f --folders    | Scan the folder
-t --trim       | Trim the image when loading in
--trim-result   | Trim the out put atlas
--result-folder | Result output folder path
--prefix        | Atlas filename prefix
```

#### Example
```
$ python controller console -i image-1.png -i image-2.png
```
```
$ python controller console -i image-1.png -f ~/Desktop -f ~/Document
```
```
$ python controller console -i image-1.png -i image-2.png --prefix atlas-12345
```

#### Result
![UI](docs/demo-2.png)<br>
<img src="docs/test-0-0.gif" alt="drawing" width="100"/> <img src="docs/test-1-0.gif" alt="drawing" width="100"/><br>
<img src="docs/test-0-1.gif" alt="drawing" width="100"/> <img src="docs/test-1-1.gif" alt="drawing" width="100"/>

#### More About Sprite Sheet
[SpriteSheets Part.1 Stroage](https://www.youtube.com/watch?v=crrFUYabm6E) <br>
[SpriteSheets Part.2 Performance](https://www.youtube.com/watch?v=_KyUqyS5MLA)