# rlottie-python

A ctypes API for rlottie, with additional functions for getting Pillow Image.

See example/example.py for example usage.

The functions mostly follow [rlottie/inc/rlottie.h](https://github.com/Samsung/rlottie/blob/master/inc/rlottie.h)

## Examples
Getting information about an lottie animation
```
from rlottie_python import LottieAnimation

anim = LottieAnimation.from_file('example/sample.json')
frames = anim.lottie_animation_get_totalframe()
print(f'{frames = }')

width, height = anim.lottie_animation_get_size()
print(f'{width, height = }')

duration = anim.lottie_animation_get_duration()
print(f'{duration = }')

totalframe = anim.lottie_animation_get_totalframe()
print(f'{totalframe = }')

framerate = anim.lottie_animation_get_framerate()
print(f'{framerate = }')

render_tree = anim.lottie_animation_render_tree(0)
print(f'{render_tree.mMaskList.size = }')

mapped_frame = anim.lottie_animation_get_frame_at_pos(0)
print(f'{mapped_frame = }')
```

Rendering and saving frame
```
from rlottie_python import LottieAnimation
from PIL import Image

anim = LottieAnimation.from_file('example/sample.json')

# Method 1: Saving the frame to file directly
anim.save_frame('frame30.png', frame_num=30)

# Method 2: Getting Pillow Image
im = anim.render_pillow_frame(frame_num=40)
im.save('frame40.png')

# Method 3: Getting buffer
buffer = anim.lottie_animation_render(frame_num=50)
width, height = anim.lottie_animation_get_size()
im = Image.frombuffer('RGBA', (width, height), buffer, 'raw', 'BGRA')
im.save('frame50.png')
```

Loading from JSON file, string of JSON, tgs; and rendering animation
```
from rlottie_python import LottieAnimation

# Loading from file
anim = LottieAnimation.from_file('example/sample.json')
anim.save_animation('animation1.apng')

anim = LottieAnimation.from_tgs('example/sample.tgs')
anim.save_animation('animation2.gif')

with open('example/sample.json') as f:
    data = f.read()

anim = LottieAnimation.from_data(data=data)
anim.save_animation('animation3.webp')
```

You may also load animation using with statement
```
from rlottie_python import LottieAnimation

with LottieAnimation.from_file('example/sample.json') as anim:
    anim.save_animation('animation4.apng')
```

## Credits
- rlottie library: https://github.com/Samsung/rlottie
- Packaging: https://github.com/tttapa/py-build-cmake