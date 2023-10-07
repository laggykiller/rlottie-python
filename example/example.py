#!/usr/bin/env python3
from rlottie_python import LottieAnimation
from PIL import Image

json_file = "sample.json"
tgs_file = "sample.tgs"

# Loading from json file
anim = LottieAnimation.from_file(json_file)

# Getting attributes about the json file
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

# Saving frame manually
buffer = anim.lottie_animation_render(frame_num=30)
im = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA")
im.save("test1.png")

# Loading from tgs file
anim = LottieAnimation.from_tgs(path=tgs_file)

# Directly get pillow Image
im = anim.render_pillow_frame(frame_num=40)
im.save("test2.png")

# Directly get buffer
buffer = anim.lottie_animation_render(frame_num=50)
width, height = anim.lottie_animation_get_size()
im = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA")
im.save("test3.png")

# Directly get buffer, async
anim.lottie_animation_render_async(frame_num=50)
# You may do other other tasks in between
buffer = anim.lottie_animation_render_flush()
width, height = anim.lottie_animation_get_size()
im = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA")
im.save("test4.png")

# Loading JSON string with from_data()
with open(json_file) as f:
    data = f.read()

# Alternative way of creating instance of LottieAnimation
with LottieAnimation.from_data(data=data) as anim:
    # Saving frame with save_frame
    anim.save_frame("test5.png", frame_num=30)

# Saving animation with save_animation
with LottieAnimation.from_tgs(path=tgs_file) as anim:
    anim.save_animation("test6.apng")
    anim.save_animation("test7.gif")
    anim.save_animation("test8.webp")
