import os
import sys
import ctypes
import gzip
from typing import TypeVar, Tuple, Optional

from PIL import Image
from .rlottiecommon import LOTLayerNode, LOTMarkerList

# References: rlottie/inc/rlottie.h

TLottieAnimation = TypeVar("TLottieAnimation", bound="LottieAnimation")

def frange(start, stop: Optional[float] = None, step: Optional[float] = None):
    # if set start=0.0 and step = 1.0 if not specified
    start = float(start)
    if stop == None:
        stop = start + 0.0
        start = 0.0
    if step == None:
        step = 1.0

    count = 0
    while True:
        temp = float(start + count * step)
        if step > 0 and temp >= stop:
            break
        elif step < 0 and temp <= stop:
            break
        yield temp
        count += 1

class LottieAnimationPointer(ctypes.c_void_p):
    pass

class LottieAnimation:
    def __init__(self, path: str = '', data: str = '', key_size: Optional[int] = None, resource_path: str = ''):
        self.rlottie_lib = None
        self.animation_p = None
        self.data_c = None
        self.key_c = None
        self.resource_path_abs_c = None

        self._load_lib()
        self.lottie_init()
        self.lottie_configure_model_cache_size(0)

        if path != '':
            self.lottie_animation_from_file(path=path)
        else:
            self.lottie_animation_from_data(data=data, key_size=key_size, resource_path=resource_path)
        
    def _load_lib(self):
        if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
            rlottie_lib_name = 'rlottie.dll'
        elif sys.platform.startswith('darwin'):
            rlottie_lib_name = 'librlottie.dylib'
        else:
            rlottie_lib_name = 'librlottie.so'

        rlottie_lib_path_local = os.path.join(os.path.dirname(__file__), rlottie_lib_name)

        if os.path.isfile(rlottie_lib_path_local):
            self.rlottie_lib_path = rlottie_lib_path_local
        elif os.path.isfile(rlottie_lib_name):
            self.rlottie_lib_path = os.path.abspath(rlottie_lib_name)
        else:
            self.rlottie_lib_path = rlottie_lib_name
        
        if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
            self.rlottie_lib = ctypes.WinDLL(self.rlottie_lib_path)
        else:
            self.rlottie_lib = ctypes.CDLL(self.rlottie_lib_path)
    
    def __del__(self):
        self.lottie_animation_destroy()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lottie_animation_destroy()
    
    @classmethod
    def from_file(cls, path: str) -> TLottieAnimation:
        '''
        Constructs LottieAnimation object from lottie file path.

        :param str path: lottie resource file path
        
        :return: LottieAnimation object
        :rtype: LottieAnimation
        '''
        return cls(path=path)
    
    @classmethod
    def from_data(cls, data: str, key_size: Optional[int] = None, resource_path: str = '') -> TLottieAnimation:
        '''
        Constructs LottieAnimation object from JSON string data.

        :param str data: the JSON string data.
        :param int key_size: (optional) the string that will be used to cache the JSON string data.
        :param str resource_path: (optional) the path that will be used to load external resource needed by the JSON data.

        :return: LottieAnimation object
        :rtype: LottieAnimation
        '''
        return cls(data=data, key_size=key_size, resource_path=resource_path)
    
    @classmethod
    def from_tgs(cls, path: str) -> TLottieAnimation:
        '''
        Constructs LottieAnimation object from tgs file path.

        :param str path: tgs resource file path

        :return: LottieAnimation object
        :rtype: LottieAnimation
        '''
        with gzip.open(path) as f:
            data = f.read().decode(encoding='utf-8')
        return cls(data=data)
    
    def lottie_init(self):
        '''
        Runs lottie initialization code when rlottie library is loaded
        dynamically.

        This api should be called before any other api when rlottie library
        is loaded using dlopen() or equivalent.
        '''
        self.rlottie_lib.lottie_init.argtypes = []
        self.rlottie_lib.lottie_init.restype = ctypes.c_void_p
        self.rlottie_lib.lottie_init()
    
    def lottie_shutdown(self):
        '''
        Runs lottie teardown code when rlottie library is loaded
        dynamically.
        
        This api should be called before unloading the rlottie library for
        proper cleanup of the resource without doing so will result in undefined
        behaviour.
        '''
        self.rlottie_lib.lottie_shutdown.argtypes = []
        self.rlottie_lib.lottie_shutdown.restype = ctypes.c_void_p
        self.rlottie_lib.lottie_shutdown()

    def lottie_animation_from_file(self, path: str):
        '''
        Constructs an animation object from JSON file path.

        NOTE: You should use from_file(path=path) instead

        :param str path: lottie resource file path
        '''
        self.rlottie_lib.lottie_animation_from_file.argtypes = [ctypes.c_char_p]
        self.rlottie_lib.lottie_animation_from_file.restype = LottieAnimationPointer

        if not os.path.isabs(path):
            path = os.path.abspath(path)
        if not os.path.isfile(path):
            raise OSError(f'Cannot find file {path}')

        path_p = ctypes.c_char_p(path.encode())

        self.animation_p = self.rlottie_lib.lottie_animation_from_file(path_p)

        del path_p
    
    def lottie_animation_from_data(self, data: str, key_size: Optional[int] = None, resource_path: str = ''):
        '''
        Constructs an animation object from JSON string data.

        NOTE: You should use from_data(data=data) instead

        :param str data: the JSON string data.
        :param int key_size: (optional) the size of string that will be used to cache the JSON string data.
        :param str resource_path: (optional) the path that will be used to load external resource needed by the JSON data.
        '''
        self.data_c = ctypes.create_string_buffer(data.encode())
        data_size = ctypes.sizeof(self.data_c)

        if key_size == None:
            key_size = data_size
        self.key_c = ctypes.create_string_buffer(key_size)
        
        resource_path_abs = ''
        if resource_path != '':
            resource_path_abs = os.path.abspath(resource_path)
        self.resource_path_abs_c = ctypes.create_string_buffer(resource_path_abs.encode())
        resource_path_abs_size = ctypes.sizeof(self.resource_path_abs_c)

        self.rlottie_lib.lottie_animation_from_data.argtypes = [ctypes.POINTER(ctypes.c_char * data_size), ctypes.POINTER(ctypes.c_char * key_size), ctypes.POINTER(ctypes.c_char * resource_path_abs_size)]
        self.rlottie_lib.lottie_animation_from_data.restype = LottieAnimationPointer

        self.animation_p = self.rlottie_lib.lottie_animation_from_data(ctypes.byref(self.data_c), ctypes.byref(self.key_c), ctypes.byref(self.resource_path_abs_c))

    def lottie_animation_destroy(self):
        '''
        Free given Animation object resource.
        Call this before loading new lottie animation.
        '''
        if not self.animation_p:
            return

        self.rlottie_lib.lottie_animation_destroy.argtypes = [LottieAnimationPointer]
        self.rlottie_lib.lottie_animation_destroy.restype = ctypes.c_void_p
        self.rlottie_lib.lottie_animation_destroy(self.animation_p)

        del self.animation_p
        self.animation_p = None

        if self.data_c:
            del self.data_c
            self.data_c = None
        if self.key_c:
            del self.key_c
            self.key_c = None
        if self.resource_path_abs_c:
            del self.resource_path_abs_c
            self.resource_path_abs_c = None
    
    def lottie_animation_get_size(self) -> Tuple[int, int]:
        '''
        Returns default viewport size of the Lottie resource.

        :return: width, height
        :rtype: int, int
        '''
        self.rlottie_lib.lottie_animation_get_size.argtypes = [LottieAnimationPointer, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
        self.rlottie_lib.lottie_animation_get_size.restype = ctypes.c_void_p

        width_c = ctypes.c_size_t()
        height_c = ctypes.c_size_t()
        self.rlottie_lib.lottie_animation_get_size(self.animation_p, ctypes.byref(width_c), ctypes.byref(height_c))

        width = width_c.value
        height = height_c.value

        del width_c, height_c

        return width, height
    
    def lottie_animation_get_duration(self) -> int:
        '''
        Returns total animation duration of Lottie resource in second.

        :return: duration
        :rtype: int
        '''
        self.rlottie_lib.lottie_animation_get_duration.argtypes = [LottieAnimationPointer]
        self.rlottie_lib.lottie_animation_get_duration.restype = ctypes.c_double

        duration = self.rlottie_lib.lottie_animation_get_duration(self.animation_p)
        return duration
    
    def lottie_animation_get_totalframe(self) -> int:
        '''
        Returns total number of frames present in the Lottie resource.

        :return: totalframe
        :rtype: int
        '''
        totalframe = self.rlottie_lib.lottie_animation_get_totalframe(self.animation_p)

        return totalframe
    
    def lottie_animation_get_framerate(self) -> int:
        '''
        Returns default framerate of the Lottie resource.

        :return: framerate
        :rtype: int
        '''
        self.rlottie_lib.lottie_animation_get_framerate.argtypes = [LottieAnimationPointer]
        self.rlottie_lib.lottie_animation_get_framerate.restype = ctypes.c_double

        framerate = self.rlottie_lib.lottie_animation_get_framerate(self.animation_p)

        return framerate
    
    def lottie_animation_render_tree(self, frame_num: int = 0, width: Optional[int] = None, height: Optional[int] = None) -> LOTLayerNode:
        '''
        Get the render tree which contains the snapshot of the animation object
        at frame = @c frame_num, the content of the animation in that frame number.

        Example for getting content of render_tree: render_tree.mMaskList.size

        :param int frame_num: (optional) Content corresponds to the frame_num needs to be drawn. Defaults to 0.
        :param int width: (optional) Requested snapshot viewport width.
        :param int height: (optional) Requested snapshot viewport height.

        :return: animation snapshot tree.
        :rtype: rlottie_python.rlottiecommon.LOTLayerNode
        '''
        self.rlottie_lib.lottie_animation_render_tree.argtypes = [LottieAnimationPointer, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t]
        self.rlottie_lib.lottie_animation_render_tree.restype = ctypes.POINTER(LOTLayerNode)

        if width == None or height == None:
            width, height = self.lottie_animation_get_size()

        render_tree_p = self.rlottie_lib.lottie_animation_render_tree(self.animation_p, ctypes.c_size_t(frame_num), ctypes.c_size_t(width), ctypes.c_size_t(height))

        render_tree = render_tree_p.contents

        del render_tree_p

        return render_tree
    
    def lottie_animation_get_frame_at_pos(self, pos: float) -> int:
        '''
        Maps position to frame number and returns it.

        :param float pos: position in the range [ 0.0 .. 1.0 ].

        :return: Mapped frame number in the range [ start_frame .. end_frame ]. 0 if the Lottie resource has no animation.
        :rtype: int
        '''
        self.rlottie_lib.lottie_animation_get_frame_at_pos.argtypes = [LottieAnimationPointer, ctypes.c_float]
        self.rlottie_lib.lottie_animation_get_frame_at_pos.restype = ctypes.c_size_t

        mapped_frame = self.rlottie_lib.lottie_animation_get_frame_at_pos(self.animation_p, ctypes.c_float(pos))
        
        return mapped_frame
    
    def lottie_animation_render(self, frame_num: int = 0, buffer_size: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, bytes_per_line: Optional[int] = None) -> bytes:
        '''
        Request to render the content of the frame frame_num to buffer.

        :param int frame_num: (optional) the frame number needs to be rendered. Defaults to 0.
        :param int buffer_size: (optional) size of surface buffer use for rendering
        :param int width: (optional) width of the surface
        :param int height: (optional) height of the surface
        :param int bytes_per_line: (optional) stride of the surface in bytes.

        :return: rendered surface buffer
        :rtype: bytes
        '''
        if width == None or height == None:
            width, height = self.lottie_animation_get_size()

        if bytes_per_line == None:
            bytes_per_line = width * 4
        
        if buffer_size == None:
            buffer_size = width * height * 4

        buffer_c = ctypes.create_string_buffer(buffer_size)

        self.rlottie_lib.lottie_animation_render.argtypes = [LottieAnimationPointer, ctypes.c_size_t, ctypes.POINTER(ctypes.c_char * buffer_size), ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t]
        self.rlottie_lib.lottie_animation_render.restype = ctypes.c_void_p
        
        self.rlottie_lib.lottie_animation_render(self.animation_p, ctypes.c_size_t(frame_num), ctypes.byref(buffer_c), ctypes.c_size_t(width), ctypes.c_size_t(height), ctypes.c_size_t(bytes_per_line))

        buffer = buffer_c.raw

        del buffer_c

        return buffer
    
    def lottie_animation_render_async(self, frame_num: int = 0, buffer_size: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, bytes_per_line: Optional[int] = None) -> bytes:
        '''
        Request to render the content of the frame frame_num to buffer asynchronously.
        user must call lottie_animation_render_flush() to make sure render is finished.

        :param int frame_num: (optional) the frame number needs to be rendered. Defaults to 0.
        :param int buffer_size: (optional) size of surface buffer use for rendering
        :param int width: (optional) width of the surface
        :param int height: (optional) height of the surface
        :param int bytes_per_line: (optional) stride of the surface in bytes.

        :return: rendered surface buffer
        :rtype: bytes
        '''
        self.rlottie_lib.lottie_animation_render_async.argtypes = [LottieAnimationPointer, ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t]
        self.rlottie_lib.lottie_animation_render_async.restype = ctypes.c_void_p

        if width == None or height == None:
            width, height = self.lottie_animation_get_size()

        if bytes_per_line == None:
            bytes_per_line = width * 4
        
        if buffer_size == None:
            buffer_c = ctypes.create_string_buffer(width * height * 4)
        
        self.rlottie_lib.lottie_animation_render_async(self.animation_p, ctypes.c_size_t(frame_num), ctypes.byref(buffer_c), ctypes.c_size_t(width), ctypes.c_size_t(height), ctypes.c_size_t(bytes_per_line))

        return buffer_c.raw

    def lottie_animation_render_flush(self) -> bytes:
        '''
        Request to finish the current async renderer job for this animation object.
        If render is finished then this call returns immidiately.
        If not, it waits till render job finish and then return.

        User must call lottie_animation_render_async() and lottie_animation_render_flush()
        in pair to get the benefit of async rendering.
        
        :return: the pixel buffer it finised rendering
        :rtype: bytes
        '''
        self.rlottie_lib.lottie_animation_get_duration.argtypes = [LottieAnimationPointer]
        self.rlottie_lib.lottie_animation_get_duration.restype = ctypes.c_uint32

        buffer_c = self.rlottie_lib.lottie_animation_render_flush(self.animation_p)

        buffer = buffer_c.raw

        del buffer_c

        return buffer
    
    def lottie_animation_property_override(self, _type: str, keypath: str, *args):
        '''
        Request to change the properties of this animation object.
        Keypath should conatin object names separated by (.) and can handle globe(**) or wildchar(*)

        Example: lottie_animation_property_override("LOTTIE_ANIMATION_PROPERTY_FILLCOLOR", "layer1.group1.fill1", ctypes.float(1.0), ctypes.float(0.0), ctypes.float(0.0))

        :param str _type: Property type.
        :param str keypath: Specific content of target.
        :param *args: Property values.
        '''
        _type_enum = [
            'LOTTIE_ANIMATION_PROPERTY_FILLCOLOR',      # Color property of Fill object , value type is float [0 ... 1]
            'LOTTIE_ANIMATION_PROPERTY_FILLOPACITY',    # Opacity property of Fill object , value type is float [ 0 .. 100]
            'LOTTIE_ANIMATION_PROPERTY_STROKECOLOR',    # Color property of Stroke object , value type is float [0 ... 1]
            'LOTTIE_ANIMATION_PROPERTY_STROKEOPACITY',  # Opacity property of Stroke object , value type is float [ 0 .. 100]
            'LOTTIE_ANIMATION_PROPERTY_STROKEWIDTH',    # stroke with property of Stroke object , value type is float
            'LOTTIE_ANIMATION_PROPERTY_TR_ANCHOR',      # Transform Anchor property of Layer and Group object , value type is int
            'LOTTIE_ANIMATION_PROPERTY_TR_POSITION',    # Transform Position property of Layer and Group object , value type is int
            'LOTTIE_ANIMATION_PROPERTY_TR_SCALE',       # Transform Scale property of Layer and Group object , value type is float range[0 ..100]
            'LOTTIE_ANIMATION_PROPERTY_TR_ROTATION',    # Transform Scale property of Layer and Group object , value type is float. range[0 .. 360] in degrees
            'LOTTIE_ANIMATION_PROPERTY_TR_OPACITY'      # Transform Opacity property of Layer and Group object , value type is float [ 0 .. 100]
        ]

        try:
            _type_index = _type_enum.index(_type)
        except IndexError:
            raise IndexError('Invalid _type')

        self.rlottie_lib.lottie_animation_property_override(self.animation_p, ctypes.c_int(_type_index), ctypes.c_char_p(keypath), *args)
    
    def lottie_animation_get_markerlist(self) -> Optional[list]:
        '''
        Returns list of markers in the Lottie resource
        LOTMarkerList has a LOTMarker list and size of list
        LOTMarker has the marker's name, start frame, and end frame.

        Example for getting content of markerlist: markerlist.ptr.name

        :return: The list of marker. If there is no marker, return None
        :rtype: list or None
        '''
        self.rlottie_lib.lottie_animation_get_markerlist.argtypes = [LottieAnimationPointer]
        self.rlottie_lib.lottie_animation_get_markerlist.restype = ctypes.POINTER(LOTMarkerList)

        markerlist = self.rlottie_lib.lottie_animation_get_markerlist(self.animation_p)

        return markerlist.contents

    def lottie_configure_model_cache_size(self, cache_size: int):
        '''
        Configures rlottie model cache policy.
        Provides Library level control to configure model cache
        policy. Setting it to 0 will disable
        the cache as well as flush all the previously cached content.

        to disable Caching configure with 0 size.
        to flush the current Cache content configure it with 0 and
        then reconfigure with the new size.

        :param int cache_size: Maximum Model Cache size.
        '''
        self.rlottie_lib.lottie_configure_model_cache_size.argtypes = [ctypes.c_size_t]
        self.rlottie_lib.lottie_configure_model_cache_size.restype = ctypes.c_void_p
        self.rlottie_lib.lottie_configure_model_cache_size(ctypes.c_size_t(cache_size))
    
    def render_pillow_frame(self, frame_num: int = 0, buffer_size: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, bytes_per_line: Optional[int] = None) -> Image:
        '''
        Create Pillow Image at frame_num

        :param int frame_num: (optional) the frame number needs to be rendered. Defaults to 0.
        :param int buffer_size: (optional) size of surface buffer use for rendering
        :param int width: (optional) width of the surface
        :param int height: (optional) height of the surface
        :param int bytes_per_line: (optional) stride of the surface in bytes.

        :return: rendered Pillow Image
        :rtype: PIL.Image.Image
        '''
        if width == None or height == None:
            width, height = self.lottie_animation_get_size()
                
        buffer = self.lottie_animation_render(frame_num=frame_num, buffer_size=buffer_size, width=width, height=height, bytes_per_line=bytes_per_line)

        im = Image.frombuffer('RGBA', (width, height), buffer, 'raw', 'BGRA')

        return im
    
    def save_frame(self, save_path: str, frame_num: int = 0, buffer_size: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, bytes_per_line: Optional[int] = None, *args, **kwargs) -> Image:
        '''
        Save Image at frame_num to save_path

        :param str save_path: path to save the Pillow Image
        :param int frame_num: (optional) the frame number needs to be rendered. Defaults to 0.
        :param int buffer_size: (optional) size of surface buffer use for rendering
        :param int width: (optional) width of the surface
        :param int height: (optional) height of the surface
        :param int bytes_per_line: (optional): stride of the surface in bytes.
        :param *args: (optional) additional arguments passing to im.save()
        :param **kwargs: (optional) additional arguments passing to im.save()

        :return: rendered Pillow Image
        :rtype: PIL.Image.Image
        '''
        im = self.render_pillow_frame(frame_num=frame_num, buffer_size=buffer_size, width=width, height=height, bytes_per_line=bytes_per_line)
        im.save(save_path, *args, **kwargs)
    
    def save_animation(self, save_path:str, fps: int = 0, frame_num_start: Optional[int] = None, frame_num_end: Optional[int] = None, buffer_size: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, bytes_per_line: Optional[int] = None, *args, **kwargs) -> Image:
        '''
        Save Image from frame_num_start to frame_num_end and save it to save_path
        It is possible to save animation as apng, gif or webp

        For .gif, maximum framerate is capped at 50
        Users may override this by specifying fps, at risk of breaking their gif

        :param str save_path: Path to save the Pillow Image
        :param int fps: (optional) Set fps of output image. Will skip frames if lower than original
        :param int frame_num_start: (optional) the starting frame number needs to be rendered.
        :param int frame_num_end: (optional) the ending frame number needs to be rendered.
        :param int buffer_size: (optional) size of surface buffer use for rendering
        :param int width: (optional) width of the surface
        :param int height: (optional) height of the surface
        :param int bytes_per_line: (optional) stride of the surface in bytes.
        :param *args: (optional) additional arguments passing to im.save()
        :param **kwargs: (optional) additional arguments passing to im.save()

        :return: rendered Pillow Image
        :rtype: PIL.Image.Image
        '''
        fps_orig = self.lottie_animation_get_framerate()
        duration = self.lottie_animation_get_duration()

        export_ext = os.path.splitext(save_path)[-1].lower()

        if not fps:
            fps = fps_orig
    
            # For .gif, maximum framerate is capped at 50
            # Users may override this by specifying fps, at risk of breaking their gif
            # Reference: https://wunkolo.github.io/post/2020/02/buttery-smooth-10fps/
            if export_ext == '.gif' and fps_orig > 50:
                fps = 50
        
        if export_ext == '.gif' and kwargs.get('disposal') == None:
            kwargs['disposal'] = 2
        
        if kwargs.get('loop') == None:
            kwargs['loop'] = 0
        
        frames = int(duration * fps)
        frame_duration = 1000 / fps

        if frame_num_start == None:
            frame_num_start = 0
        if frame_num_end == None:
            frame_num_end = frames

        im_list = []
        for frame in range(frame_num_start, frame_num_end):
            pos = frame / frame_num_end
            frame_num = self.lottie_animation_get_frame_at_pos(pos)
            im_list.append(self.render_pillow_frame(frame_num=frame_num, buffer_size=buffer_size, width=width, height=height, bytes_per_line=bytes_per_line).copy())

        im_list[0].save(save_path, save_all=True, append_images=im_list[1:], duration=int(frame_duration), *args, **kwargs)
