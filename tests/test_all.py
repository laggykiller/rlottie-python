#!/usr/bin/env python3
import ctypes
import os
import platform

import pytest
try:
    from PIL import Image

    PILLOW_LOADED = True
except ModuleNotFoundError:
    PILLOW_LOADED = False

from rlottie_python import LottieAnimation
from rlottie_python.rlottiecommon import LOTLayerNode

file_dir = os.path.split(__file__)[0]
json_file = os.path.join(file_dir, "../samples/sample.json")
tgs_file = os.path.join(file_dir, "../samples/sample.tgs")

def test_from_file():
    anim = LottieAnimation.from_file(json_file)
    assert isinstance(anim, LottieAnimation)

def test_from_file_with():
    with LottieAnimation.from_file(json_file) as anim:
        assert isinstance(anim, LottieAnimation)

def test_from_data():
    with open(json_file, encoding="utf-8") as f:
        data = f.read()

    anim = LottieAnimation.from_data(data)
    assert isinstance(anim, LottieAnimation)

def test_from_data_with():
    with open(json_file, encoding="utf-8") as f:
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

@pytest.mark.skipif(PILLOW_LOADED is False, reason="Pillow not installed")
def test_render_pillow_frame():
    with LottieAnimation.from_file(json_file) as anim:
        im = anim.render_pillow_frame()

        assert isinstance(im, Image.Image)

@pytest.mark.skipif(PILLOW_LOADED is False, reason="Pillow not installed")
def test_save_frame(tmpdir):
    tmppath = os.path.join(tmpdir, "0.png")
    with LottieAnimation.from_file(json_file) as anim:
        anim.save_frame(tmppath)

    assert os.path.isfile(tmppath)
    Image.open(tmppath)

def _test_save_animation(out):
    with LottieAnimation.from_file(json_file) as anim:
        anim.save_frame(out)

    assert os.path.isfile(out)

@pytest.mark.skipif(PILLOW_LOADED is False, reason="Pillow not installed")
def test_save_animation_apng(tmpdir):
    tmppath = os.path.join(tmpdir, "0.apng")
    _test_save_animation(tmppath)

@pytest.mark.skipif(PILLOW_LOADED is False, reason="Pillow not installed")
def test_save_animation_gif(tmpdir):
    tmppath = os.path.join(tmpdir, "0.gif")
    _test_save_animation(tmppath)

@pytest.mark.skipif(PILLOW_LOADED is False, reason="Pillow not installed")
@pytest.mark.skipif(platform.python_implementation() == "PyPy", reason="Pillow without webp support")
def test_save_animation_webp(tmpdir):
    tmppath = os.path.join(tmpdir, "0.webp")
    _test_save_animation(tmppath)