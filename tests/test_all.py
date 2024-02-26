#!/usr/bin/env python3
import ctypes
from pathlib import Path

from PIL import Image
from rlottie_python import LottieAnimation
from rlottie_python.rlottiecommon import LOTLayerNode

file_dir = Path(__file__).parent
json_file = Path(file_dir, "../samples/sample.json").as_posix()
tgs_file = Path(file_dir, "../samples/sample.tgs").as_posix()

def test_from_file():
    anim = LottieAnimation.from_file(json_file)
    assert isinstance(anim, LottieAnimation)

def test_from_file_with():
    with LottieAnimation.from_file(json_file) as anim:
        assert isinstance(anim, LottieAnimation)

def test_from_data():
    with open(json_file) as f:
        data = f.read()

    anim = LottieAnimation.from_data(data)
    assert isinstance(anim, LottieAnimation)

def test_from_data_with():
    with open(json_file) as f:
        data = f.read()
    
    with LottieAnimation.from_data(data) as anim:
        assert isinstance(anim, LottieAnimation)

def test_from_tgs():
    anim = LottieAnimation.from_tgs(tgs_file)
    assert isinstance(anim, LottieAnimation)

def test_from_tgs_with():
    with LottieAnimation.from_tgs(tgs_file) as anim:
        assert isinstance(anim, LottieAnimation)

def test_lottie_animation_get_size():
    with LottieAnimation.from_file(json_file) as anim:
        size = anim.lottie_animation_get_size()
    
    assert size == (800, 600)

def test_lottie_animation_get_duration():
    with LottieAnimation.from_file(json_file) as anim:
        duration = anim.lottie_animation_get_duration()
    
    assert duration == 2.0

def test_lottie_animation_get_totalframe():
    with LottieAnimation.from_file(json_file) as anim:
        totalframe = anim.lottie_animation_get_totalframe()
    
    assert totalframe == 51

def test_lottie_animation_get_framerate():
    with LottieAnimation.from_file(json_file) as anim:
        framerate = anim.lottie_animation_get_framerate()
    
    assert framerate == 25.0

def test_lottie_animation_render_tree():
    with LottieAnimation.from_file(json_file) as anim:
        render_tree = anim.lottie_animation_render_tree()
    
    assert isinstance(render_tree, LOTLayerNode)

def test_lottie_animation_get_frame_at_pos():
    with LottieAnimation.from_file(json_file) as anim:
        frame = anim.lottie_animation_get_frame_at_pos(0.5)
    
    assert frame == 25

def test_lottie_animation_render():
    with LottieAnimation.from_file(json_file) as anim:
        buffer = anim.lottie_animation_render()
    
    assert isinstance(buffer, bytes)

def test_lottie_animation_render_async():
    with LottieAnimation.from_file(json_file) as anim:
        anim.lottie_animation_render_async()
        buffer = anim.lottie_animation_render_flush()
    
    assert isinstance(buffer, bytes)

def test_lottie_animation_property_override():
    with LottieAnimation.from_file(json_file) as anim:
        anim.lottie_animation_property_override(
            "LOTTIE_ANIMATION_PROPERTY_FILLCOLOR",
            "layer1.group1.fill1",
            ctypes.c_float(1.0),
            ctypes.c_float(0.0),
            ctypes.c_float(0.0)
        )
    
def test_lottie_animation_get_markerlist():
    with LottieAnimation.from_file(json_file) as anim:
        markerlist = anim.lottie_animation_get_markerlist()
    
    assert markerlist is None

def test_lottie_configure_model_cache_size():
    with LottieAnimation.from_file(json_file) as anim:
        anim.lottie_configure_model_cache_size(0)

def test_render_pillow_frame():
    with LottieAnimation.from_file(json_file) as anim:
        im = anim.render_pillow_frame()

        assert isinstance(im, Image.Image)
    
def test_save_frame(tmpdir):
    tmppath = Path(tmpdir, "0.png").as_posix()
    with LottieAnimation.from_file(json_file) as anim:
        anim.save_frame(tmppath)

    assert Path(tmppath).is_file()
    Image.open(tmppath)

def _test_save_animation(out):
    with LottieAnimation.from_file(json_file) as anim:
        anim.save_frame(out)

    assert Path(out).is_file()

def test_save_animation(tmpdir):
    for i in ("0.apng", "0.gif", "0.webp"):
        tmppath = Path(tmpdir, i).as_posix()
        _test_save_animation(tmppath)