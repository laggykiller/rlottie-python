# rlottie-python

A ctypes API for rlottie, with additional functions for getting Pillow Image and animated sequences, as well as telegram animated stickers (tgs).

See example/example.py for example usage.

The functions mostly follow [rlottie/inc/rlottie_capi.h](https://github.com/Samsung/rlottie/blob/master/inc/rlottie_capi.h)

Documentations: https://rlottie-python.readthedocs.io/en/latest/

## Table of contents
- [Installing](#installing)
- [Building from source](#building-from-source)
- [Examples](#examples)
- [Comparing to other library](#comparing-to-other-library)
- [Credits](#credits)

## Installing

Note that rlottie is included in the wheel package, you need not install librlottie.

To install, run the following:
```bash
pip3 install rlottie-python
```

`Pillow` is optional dependency. It is required for `render_pillow_frame()`,
`save_frame()` and `save_animation()`. To also install Pillow, run:
```bash
pip3 install rlottie-python[full]
```

## Examples
Getting information about an lottie animation
```python
from rlottie_python import LottieAnimation

anim = LottieAnimation.from_file("samples/sample.json")
frames = anim.lottie_animation_get_totalframe()
print(f"{frames = }")

width, height = anim.lottie_animation_get_size()
print(f"{width, height = }")

duration = anim.lottie_animation_get_duration()
print(f"{duration = }")

totalframe = anim.lottie_animation_get_totalframe()
print(f"{totalframe = }")

framerate = anim.lottie_animation_get_framerate()
print(f"{framerate = }")

render_tree = anim.lottie_animation_render_tree(0)
print(f"{render_tree.mMaskList.size = }")

mapped_frame = anim.lottie_animation_get_frame_at_pos(0)
print(f"{mapped_frame = }")
```

Rendering and saving frame
```python
from rlottie_python import LottieAnimation
from PIL import Image

anim = LottieAnimation.from_file("samples/sample.json")

# Method 1: Saving the frame to file directly
anim.save_frame("frame30.png", frame_num=30)

# Method 2: Getting Pillow Image
im = anim.render_pillow_frame(frame_num=40)
im.save("frame40.png")

# Method 3: Getting buffer
buffer = anim.lottie_animation_render(frame_num=50)
width, height = anim.lottie_animation_get_size()
im = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA")
im.save("frame50.png")
```

Loading from JSON file, string of JSON, tgs; and rendering animation
```python
from rlottie_python import LottieAnimation

# Loading from file
anim = LottieAnimation.from_file("samples/sample.json")
anim.save_animation("animation1.apng")

anim = LottieAnimation.from_tgs("samples/sample.tgs")
anim.save_animation("animation2.gif")

with open("samples/sample.json", encoding="utf-8") as f:
    data = f.read()

anim = LottieAnimation.from_data(data=data)
anim.save_animation("animation3.webp")
```

You may also load animation using with statement
```python
from rlottie_python import LottieAnimation

with LottieAnimation.from_file("samples/sample.json") as anim:
    anim.save_animation("animation4.apng")
```

Notice, if you are running on Linux and want to use rlottie_python in main process
and child processes spawned by `multiprocessing.Process`, you may have to change
start method to `spawn`, or else deadlock may occur:
```python
if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
```

## Comparing to other library
The `lottie` (https://pypi.org/project/lottie/) python package is also capable of working with lottie files and telegram animated stickers (tgs). It is also able to support many input/output formats and vector graphics, without any dependency on extenral libraries such as librlottie. However some images it creates is broken ([Example1](https://github.com/laggykiller/sticker-convert/issues/5) [Example2](https://gitlab.com/mattbas/python-lottie/-/issues/95)). It seems librlottie is more stable in terms of rendering frames.

The `pyrlottie` (https://pypi.org/project/pyrlottie/) python package is also able to convert lottie and tgs files to webp/gif. However, it works by calling executables `gif2webp` and `lottie2gif` with subprocess, and it does not support macOS.

## Building from source

To build wheel, run the following:
```bash
git clone --recursive https://github.com/laggykiller/rlottie-python.git
cd rlottie-python

# To build wheel
python3 -m build .

# To install directly
pip3 install .
```

## Development
To run tests:
```bash
pip install pytest
pytest
```

To lint:
```bash
pip install ruff mypy isort
mypy
isort .
ruff check
ruff format
```

## Credits
- rlottie library: https://github.com/Samsung/rlottie
- Packaging: https://github.com/tttapa/py-build-cmake