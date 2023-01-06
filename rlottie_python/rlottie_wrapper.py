import ctypes
from ctypes import wintypes
import os
from .rlottiecommon import LOTLayerNode, LOTMarkerList
from sys import platform
from PIL import Image
import numpy as np
import gzip

# References: rlottie/inc/rlottie.h

class LottieAnimationStruct(ctypes.c_void_p):
    pass

class LottieAnimation:
    animation_p = None
    rlottie_lib = None

    def __init__(self, path: str='', data: str='', key: str='', resource_path: str=''):
        # self.tempdlldir = TemporaryDirectory()
        self.load_lib()
        self.lottie_init()

        if path != '':
            self.lottie_animation_from_file(path=path)
        else:
            self.lottie_animation_from_data(data=data, key=key, resource_path=resource_path)
    
    def load_lib(self):
        if platform.startswith('win32') or platform.startswith('cygwin'):
            rlottie_lib_name = 'rlottie.dll'
        elif platform.startswith('darwin'):
            rlottie_lib_name = 'librlottie.dylib'
        else:
            rlottie_lib_name = 'librlottie.so'

        if os.path.isfile(rlottie_lib_name):
            rlottie_lib_path = os.path.abspath(rlottie_lib_name)
        else:
            rlottie_lib_path = rlottie_lib_name
        
        if platform.startswith('win32') or platform.startswith('cygwin'):
            self.rlottie_lib = ctypes.WinDLL(rlottie_lib_path)
        else:
            self.rlottie_lib = ctypes.cdll.LoadLibrary(rlottie_lib_path)

    def unload_lib(self):
        '''
        Unload rlottie library
        If the library is not reloaded, previously loaded animation would still remain
        '''
        if self.rlottie_lib:
            if self.animation_p:
                self.lottie_animation_destroy()
            self.lottie_shutdown()

            handle = self.rlottie_lib._handle
            del self.rlottie_lib

            if platform.startswith('win32'):
                ctypes.windll.kernel32.FreeLibrary.argtypes = [wintypes.HMODULE]
                ctypes.windll.kernel32.FreeLibrary(handle)
            else:
                libdl = ctypes.cdll.LoadLibrary("libdl.so")
                libdl.dlclose(handle)
            
            self.rlottie_lib = None
        
    def reload_lib(self):
        self.unload_lib()
        self.load_lib()
    
    def __del__(self):
        self.unload_lib()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unload_lib()
    
    @classmethod
    def from_file(cls, path: str):
        '''
        Constructs LottieAnimation object from lottie file path.

        INPUT:
        path: Lottie resource file path
        '''
        return cls(path=path)
    
    @classmethod
    def from_data(cls, data, key: str='', resource_path: str=''):
        '''
        Constructs LottieAnimation object from JSON string data.

        INPUT:
        data: The JSON string data.
        key (optional): the string that will be used to cache the JSON string data.
        resource_path (optional): the path that will be used to load external resource needed by the JSON data.
        '''
        return cls(data=data, key=key, resource_path=resource_path)
    
    @classmethod
    def from_tgs(cls, path: str):
        '''
        Constructs LottieAnimation object from tgs file path.

        INPUT:
        path: tgs resource file path
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
        self.rlottie_lib.lottie_init()
    
    def lottie_shutdown(self):
        '''
        Runs lottie teardown code when rlottie library is loaded
        dynamically.
        
        This api should be called before unloading the rlottie library for
        proper cleanup of the resource without doing so will result in undefined
        behaviour.
        '''
        self.rlottie_lib.lottie_shutdown()

    def lottie_animation_from_file(self, path: str):
        '''
        Constructs an animation object from JSON file path.

        NOTE: You should use from_file(path=path) instead

        INPUT:
        path: Lottie resource file path
        '''
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        if not os.path.isfile(path):
            raise OSError(f'Cannot find file {path}')

        path_p = ctypes.c_char_p(path.encode())

        lottie_animation_from_file = self.rlottie_lib.lottie_animation_from_file
        lottie_animation_from_file.argtypes = [ctypes.c_char_p]
        lottie_animation_from_file.restype = LottieAnimationStruct

        self.animation_p = lottie_animation_from_file(path_p)
    
    def lottie_animation_from_data(self, data: str, key: str='', resource_path: str=''):
        '''
        Constructs an animation object from JSON string data.

        NOTE: You should use from_data(data=data) instead

        INPUT:
        data: The JSON string data.
        key (optional): the string that will be used to cache the JSON string data.
        resource_path (optional): the path that will be used to load external resource needed by the JSON data.
        '''
        data_p = ctypes.c_char_p(data.encode())
        key_p = ctypes.c_char_p(key.encode())
        
        resource_path_abs = os.path.abspath(resource_path)
        resource_path_abs_p = ctypes.c_char_p(resource_path_abs.encode())

        lottie_animation_from_data = self.rlottie_lib.lottie_animation_from_data
        lottie_animation_from_data.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        lottie_animation_from_data.restype = LottieAnimationStruct

        self.animation_p = lottie_animation_from_data(data_p, key_p, resource_path_abs_p)

    def lottie_animation_destroy(self):
        '''
        Free given Animation object resource.
        Call this before loading new lottie animation.
        '''
        self.rlottie_lib.lottie_animation_destroy(self.animation_p)
    
    def lottie_animation_get_size(self):
        '''
        Returns total animation duration of Lottie resource in second.
        '''
        width = ctypes.c_size_t()
        height = ctypes.c_size_t()
        self.rlottie_lib.lottie_animation_get_size(self.animation_p, ctypes.byref(width), ctypes.byref(height))

        return width.value, height.value
    
    def lottie_animation_get_duration(self):
        '''
        Returns total number of frames present in the Lottie resource.
        '''
        lottie_animation_get_duration = self.rlottie_lib.lottie_animation_get_duration
        lottie_animation_get_duration.argtypes = [LottieAnimationStruct]
        lottie_animation_get_duration.restype = ctypes.c_double

        duration = lottie_animation_get_duration(self.animation_p)
        return duration
    
    def lottie_animation_get_totalframe(self):
        '''
        Returns total number of frames present in the Lottie resource.
        '''
        totalframe = self.rlottie_lib.lottie_animation_get_totalframe(self.animation_p)

        return totalframe
    
    def lottie_animation_get_framerate(self):
        '''
        Returns default framerate of the Lottie resource.
        '''
        lottie_animation_get_framerate = self.rlottie_lib.lottie_animation_get_framerate
        lottie_animation_get_framerate.argtypes = [LottieAnimationStruct]
        lottie_animation_get_framerate.restype = ctypes.c_double

        framerate = lottie_animation_get_framerate(self.animation_p)

        return framerate
    
    def lottie_animation_render_tree(self, frame_num: int=0, width: int=None, height: int=None):
        '''
        Get the render tree which contains the snapshot of the animation object
        at frame = @c frame_num, the content of the animation in that frame number.

        INPUT:
        frame_num (optional): Content corresponds to the @p frame_num needs to be drawn. Defaults to 0.
        width (optional): requested snapshot viewport width.
        height (optional): requested snapshot viewport height.

        OUTPUT:
        Animation snapshot tree.

        Example for getting content of render_tree: render_tree.mMaskList.size
        '''
        lottie_animation_render_tree = self.rlottie_lib.lottie_animation_render_tree
        lottie_animation_render_tree.argtypes = [LottieAnimationStruct, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t]
        lottie_animation_render_tree.restype = ctypes.POINTER(LOTLayerNode)

        if width == None or height == None:
            width, height = self.lottie_animation_get_size()

        render_tree = lottie_animation_render_tree(self.animation_p, ctypes.c_size_t(frame_num), ctypes.c_size_t(width), ctypes.c_size_t(height))

        return render_tree.contents
    
    def lottie_animation_get_frame_at_pos(self, pos: int):
        '''
        Maps position to frame number and returns it.

        INPUT:
        pos: position in the range [ 0.0 .. 1.0 ].

        OUTPUT:
        mapped frame numbe in the range [ start_frame .. end_frame ].
        0 if the Lottie resource has no animation.
        '''
        lottie_animation_get_frame_at_pos = self.rlottie_lib.lottie_animation_get_frame_at_pos
        lottie_animation_get_frame_at_pos.argtypes = [LottieAnimationStruct, ctypes.POINTER(ctypes.c_float)]
        lottie_animation_get_frame_at_pos.restype = ctypes.c_size_t

        mapped_frame = lottie_animation_get_frame_at_pos(self.animation_p, ctypes.c_float(pos))
        
        return mapped_frame
    
    def lottie_animation_render(self, frame_num: int=0, buffer_size: int=None, width: int=None, height: int=None, bytes_per_line: int=None):
        '''
        Request to render the content of the frame frame_num to buffer.

        INPUT:
        frame_num (optional): the frame number needs to be rendered. Defaults to 0.
        buffer_size (optional): size of surface buffer use for rendering
        width (optional): width of the surface
        height (optional): height of the surface
        bytes_per_line (optional): stride of the surface in bytes.

        OUTPUT:
        buffer: rendered surface buffer
        '''        
        if width == None or height == None:
            width, height = self.lottie_animation_get_size()

        if bytes_per_line == None:
            bytes_per_line = width * 4
        
        if buffer_size == None:
            buffer = ctypes.create_string_buffer(width * height * 4)
        
        self.rlottie_lib.lottie_animation_render(self.animation_p, ctypes.c_size_t(frame_num), ctypes.byref(buffer), ctypes.c_size_t(width), ctypes.c_size_t(height), ctypes.c_size_t(bytes_per_line))

        return buffer.raw
    
    def lottie_animation_render_async(self, frame_num: int=0, buffer_size: int=None, width: int=None, height: int=None, bytes_per_line: int=None):
        '''
        Request to render the content of the frame @p frame_num to buffer @p buffer asynchronously.
        user must call lottie_animation_render_flush() to make sure render is finished.

        INPUT:
        frame_num (optional): the frame number needs to be rendered. Defaults to 0.
        buffer_size (optional): size of surface buffer use for rendering
        width (optional): width of the surface
        height (optional): height of the surface
        bytes_per_line (optional): stride of the surface in bytes.

        OUTPUT:
        buffer: rendered surface buffer
        '''
        if width == None or height == None:
            width, height = self.lottie_animation_get_size()

        if bytes_per_line == None:
            bytes_per_line = width * 4
        
        if buffer_size == None:
            buffer = ctypes.create_string_buffer(width * height * 4)
        
        self.rlottie_lib.lottie_animation_render_async(self.animation_p, ctypes.c_size_t(frame_num), ctypes.byref(buffer), ctypes.c_size_t(width), ctypes.c_size_t(height), ctypes.c_size_t(bytes_per_line))

        return buffer.raw

    def lottie_animation_render_flush(self):
        '''
        Request to finish the current async renderer job for this animation object.
        If render is finished then this call returns immidiately.
        If not, it waits till render job finish and then return.

        User must call lottie_animation_render_async() and lottie_animation_render_flush()
        in pair to get the benefit of async rendering.

        OUTPUT:
        buffer: the pixel buffer it finised rendering
        '''
        lottie_animation_get_duration = self.rlottie_lib.lottie_animation_get_duration
        lottie_animation_get_duration.argtypes = [LottieAnimationStruct]
        lottie_animation_get_duration.restype = ctypes.c_uint32

        buffer = self.rlottie_lib.lottie_animation_render_flush(self.animation_p)

        return buffer
    
    def lottie_animation_property_override(self, _type: str, keypath: str, *args):
        '''
        Request to change the properties of this animation object.
        Keypath should conatin object names separated by (.) and can handle globe(**) or wildchar(*)

        INPUT:
        animation: Animation object.
        _type: Property type.
        keypath: Specific content of target.
        *args: Property values.

        Example: lottie_animation_property_override("LOTTIE_ANIMATION_PROPERTY_FILLCOLOR", "layer1.group1.fill1", ctypes.float(1.0), ctypes.float(0.0), ctypes.float(0.0))
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

        self.rlottie_lib.lottie_animation_property_override(self.animation_p, ctypes.c_int(_type_index), ctypes.c_char_p(ctypes.byref(keypath)), *args)
    
    def lottie_animation_get_markerlist(self):
        '''
        Returns list of markers in the Lottie resource
        LOTMarkerList has a LOTMarker list and size of list
        LOTMarker has the marker's name, start frame, and end frame.

        OUTPUT:
        The list of marker. If there is no marker, return null.

        Example for getting content of markerlist: markerlist.ptr.name
        '''
        lottie_animation_get_markerlist = self.rlottie_lib.lottie_animation_get_markerlist
        lottie_animation_get_markerlist.argtypes = [LottieAnimationStruct]
        lottie_animation_get_markerlist.restype = ctypes.POINTER(LOTMarkerList)

        markerlist = self.rlottie_lib.lottie_animation_get_markerlist(self.animation_p)

        return markerlist.contents

    def lottie_configure_model_cache_size(self, cacheSize):
        '''
        Configures rlottie model cache policy.
        Provides Library level control to configure model cache
        policy. Setting it to 0 will disable
        the cache as well as flush all the previously cached content.

        to disable Caching configure with 0 size.
        to flush the current Cache content configure it with 0 and
        then reconfigure with the new size.

        INPUT:
        cacheSize: Maximum Model Cache size.
        '''
        self.rlottie_lib.lottie_configure_model_cache_size(ctypes.c_size_t(cacheSize))
    
    def render_pillow_frame(self, frame_num: int=0, buffer_size: int=None, width: int=None, height: int=None, bytes_per_line: int=None):
        '''
        Create Pillow Image at frame_num

        INPUT:
        frame_num (optional): the frame number needs to be rendered. Defaults to 0.
        buffer_size (optional): size of surface buffer use for rendering
        width (optional): width of the surface
        height (optional): height of the surface
        bytes_per_line (optional): stride of the surface in bytes.

        OUTPUT:
        im: rendered Pillow Image
        '''
        if width == None or height == None:
            width, height = self.lottie_animation_get_size()
                
        buffer = self.lottie_animation_render(frame_num=frame_num, buffer_size=buffer_size, width=width, height=height, bytes_per_line=bytes_per_line)

        im = Image.frombuffer('RGBA', (width, height), buffer, 'raw', 'BGRA')

        return im
    
    def save_frame(self, save_path: str, frame_num: int=0, buffer_size: int=None, width: int=None, height: int=None, bytes_per_line: int=None, *args, **kwargs):
        '''
        Save Image at frame_num to save_path

        INPUT:
        save_path: Path to save the Pillow Image
        frame_num (optional): the frame number needs to be rendered. Defaults to 0.
        buffer_size (optional): size of surface buffer use for rendering
        width (optional): width of the surface
        height (optional): height of the surface
        bytes_per_line (optional): stride of the surface in bytes.
        *args, **kwargs (optional): additional arguments passing to im.save()

        OUTPUT:
        im: rendered Pillow Image
        '''
        im = self.render_pillow_frame(frame_num=frame_num, buffer_size=buffer_size, width=width, height=height, bytes_per_line=bytes_per_line)
        im.save(save_path, *args, **kwargs)
    
    def save_animation(self, save_path:str, fps: int=0, frame_num_start: int=None, frame_num_end: int=None, buffer_size: int=None, width: int=None, height: int=None, bytes_per_line: int=None, *args, **kwargs):
        '''
        Save Image from frame_num_start to frame_num_end and save it to save_path
        It is possible to save animation as apng, gif or webp

        For .gif, maximum framerate is capped at 50
        Users may override this by specifying fps, at risk of breaking their gif

        INPUT:
        save_path: Path to save the Pillow Image
        fps (optional): Set fps of output image. Will skip frames if lower than original
        frame_num_start (optional): the starting frame number needs to be rendered.
        frame_num_end (optional): the ending frame number needs to be rendered.
        buffer_size (optional): size of surface buffer use for rendering
        width (optional): width of the surface
        height (optional): height of the surface
        bytes_per_line (optional): stride of the surface in bytes.
        *args, **kwargs (optional): additional arguments passing to im.save()

        OUTPUT:
        im: rendered Pillow Image
        '''
        if frame_num_start == None or frame_num_end == None:
            frame_num_start = 0
            frame_num_end = self.lottie_animation_get_totalframe()

        fps_orig = self.lottie_animation_get_framerate()
        duration_orig = 1000 / fps_orig

        if fps:
            duration = 1000 / fps
        else:
            duration = 1000 / fps_orig
    
            # For .gif, maximum framerate is capped at 50
            # Users may override this by specifying fps, at risk of breaking their gif
            # Reference: https://wunkolo.github.io/post/2020/02/buttery-smooth-10fps/
            if os.path.splitext(save_path)[-1].lower() == '.gif' and fps_orig > 50:
                duration = 1000 / 50
            
        if os.path.splitext(save_path)[-1].lower() == '.gif' and kwargs.get('disposal') == None:
            kwargs['disposal'] = 2
        
        if kwargs.get('loop') == None:
            kwargs['loop'] = 0
        
        im_list = []
        for frame_num in range(frame_num_start, frame_num_end):
            im_list.append(self.render_pillow_frame(frame_num=frame_num, buffer_size=buffer_size, width=width, height=height, bytes_per_line=bytes_per_line))

        im_list_mapped = []
        time_start = frame_num_start * duration_orig # Starting time in ms
        time_end = frame_num_end * duration_orig # Ending time in ms
        for i in np.arange(time_start, time_end, duration):
            j = min(round((i - time_start) / duration_orig), frame_num_end)
            im_list_mapped.append(im_list[j])

        im_list_mapped[0].save(save_path, save_all=True, append_images=im_list_mapped[1:], duration=int(duration), *args, **kwargs)