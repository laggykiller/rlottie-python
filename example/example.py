from rlottie_python import LottieAnimation
from PIL import Image

json_file = 'sample.json'
tgs_file = 'sample.tgs'

# Loading from json file
anim = LottieAnimation.from_file(json_file)

# Getting attributes about the json file
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

# Saving frame manually
buffer = anim.lottie_animation_render(frame_num=30)
im = Image.frombuffer('RGBA', (width, height), buffer, 'raw', 'BGRA')
im.save('test1.png')

# Before loading other file, you have to delete previously created LottieAnimation first
# Or else, the previous animation would persist
# Alternatively, you may use multiprocessing
del anim

# Now you may load new animation safely
with open(json_file) as f:
    with LottieAnimation.from_data(data=f.read()) as anim:
        # Saving frame with save_frame
        anim.save_frame('test2.png', frame_num=30)

# Directly get pillow Image
im = anim.render_pillow_frame(frame_num=40)
im.save('test3.png')

# After finishing, it is a good practice to delete instance of LottieAnimation
del anim

# To avoid deleting manually, you may do this instead
# Loading from tgs file
with LottieAnimation.from_tgs(path=tgs_file) as anim:
    # Saving animation with save_animation
    anim.save_animation('test4.apng')
    anim.save_animation('test5.gif')
    anim.save_animation('test6.webp')