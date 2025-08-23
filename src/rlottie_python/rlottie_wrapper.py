#!/usr/bin/env python3
import ctypes
import gzip
import os
import sys
import sysconfig
from enum import IntEnum
from types import TracebackType
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Type

if TYPE_CHECKING:
    from PIL import Image

from ._rlottiecommon import LOTLayerNode, LOTMarkerList

# References: rlottie/inc/rlottie_capi.h


def _load_lib_with_prefix_suffix(
    lib_prefix: str, lib_suffix: str
) -> Optional[ctypes.CDLL]:
    package_dir = os.path.dirname(__file__)
    rlottie_lib_name = lib_prefix + "rlottie" + lib_suffix
    rlottie_lib_path_local = os.path.join(package_dir, rlottie_lib_name)

    if os.path.isfile(rlottie_lib_path_local):
        rlottie_lib_path = rlottie_lib_path_local
    elif os.path.isfile(rlottie_lib_name):
        rlottie_lib_path = os.path.abspath(rlottie_lib_name)
    else:
        rlottie_lib_path = rlottie_lib_name

    try:
        return ctypes.cdll.LoadLibrary(rlottie_lib_path)
    except OSError:
        return None


def _load_lib(rlottie_lib_path: Optional[str] = None) -> Optional[ctypes.CDLL]:
    if rlottie_lib_path:
        try:
            return ctypes.cdll.LoadLibrary(rlottie_lib_path)
        except OSError:
            return None

    if sys.platform.startswith(("win32", "cygwin", "msys", "os2")):
        lib = _load_lib_with_prefix_suffix("", ".dll")
    elif sys.platform.startswith("darwin"):
        lib = _load_lib_with_prefix_suffix("lib", ".dylib")
    else:
        lib = _load_lib_with_prefix_suffix("lib", ".so")

    if lib:
        return lib

    lib_suffixes: List[str] = []
    shlib_suffix = sysconfig.get_config_var("SHLIB_SUFFIX")
    if isinstance(shlib_suffix, str):
        lib_suffixes.append(shlib_suffix)
    if sys.platform.startswith(("win32", "cygwin", "msys", "os2")):
        lib_prefixes = ("", "lib")
    elif sys.platform.startswith("darwin"):
        lib_prefixes = ("lib", "")
    else:
        lib_prefixes = ("lib", "")
    lib_suffixes.extend([".so", ".dll", ".dylib"])

    for lib_prefix in lib_prefixes:
        for lib_suffix in set(lib_suffixes):
            lib = _load_lib_with_prefix_suffix(lib_prefix, lib_suffix)
            if lib:
                return lib

    return None


RLOTTIE_LIB = _load_lib()


class _LottieAnimationPointer(ctypes.c_void_p):
    pass


class LottieAnimationProperty(IntEnum):
    LOTTIE_ANIMATION_PROPERTY_FILLCOLOR = 0
    LOTTIE_ANIMATION_PROPERTY_FILLOPACITY = 1
    LOTTIE_ANIMATION_PROPERTY_STROKECOLOR = 2
    LOTTIE_ANIMATION_PROPERTY_STROKEOPACITY = 3
    LOTTIE_ANIMATION_PROPERTY_STROKEWIDTH = 4
    LOTTIE_ANIMATION_PROPERTY_TR_ANCHOR = 5
    LOTTIE_ANIMATION_PROPERTY_TR_POSITION = 6
    LOTTIE_ANIMATION_PROPERTY_TR_SCALE = 7
    LOTTIE_ANIMATION_PROPERTY_TR_ROTATION = 8
    LOTTIE_ANIMATION_PROPERTY_TR_OPACITY = 9

    @classmethod
    def from_param(cls, obj: int) -> int:
        return int(obj)


class LottieAnimation:
    def __init__(
        self,
        path: str = "",
        data: str = "",
        key_size: Optional[int] = None,
        resource_path: Optional[str] = None,
        rlottie_lib_path: Optional[str] = None,
    ) -> None:
        self.animation_p = None
        self.data_c: Optional[ctypes.Array[ctypes.c_char]] = None
        self.key_c: Optional[ctypes.Array[ctypes.c_char]] = None
        self.resource_path_abs_c: Optional[ctypes.Array[ctypes.c_char]] = None
        self.async_buffer_c: Optional[ctypes.Array[ctypes.c_char]] = None

        self._load_lib(rlottie_lib_path)
        self.lottie_init()
        self.lottie_configure_model_cache_size(0)

        if path != "":
            self.lottie_animation_from_file(path=path)
        else:
            self.lottie_animation_from_data(
                data=data, key_size=key_size, resource_path=resource_path
            )

    def _load_lib(self, rlottie_lib_path: Optional[str] = None) -> None:
        if rlottie_lib_path is None:
            if RLOTTIE_LIB is None:
                raise OSError("Could not load rlottie library")
            else:
                self.rlottie_lib = RLOTTIE_LIB
                return

        rlottie_lib = _load_lib(rlottie_lib_path)
        if rlottie_lib is None:
            raise OSError(f"Could not load rlottie library from {rlottie_lib_path}")
        else:
            self.rlottie_lib = rlottie_lib

    def __del__(self) -> None:
        if self.rlottie_lib:
            self.lottie_animation_destroy()

    def __enter__(self) -> "LottieAnimation":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if self.rlottie_lib:
            self.lottie_animation_destroy()

    @classmethod
    def from_file(
        cls, path: str, rlottie_lib_path: Optional[str] = None
    ) -> "LottieAnimation":
        """
        Constructs LottieAnimation object from lottie file path.

        :param str path: lottie resource file path
        :param Optional[str] rlottie_lib_path: Optionally specific where the rlottie
            library is located

        :return: LottieAnimation object
        :rtype: LottieAnimation
        """
        return cls(path=path, rlottie_lib_path=rlottie_lib_path)

    @classmethod
    def from_data(
        cls,
        data: str,
        key_size: Optional[int] = None,
        resource_path: Optional[str] = None,
        rlottie_lib_path: Optional[str] = None,
    ) -> "LottieAnimation":
        """
        Constructs LottieAnimation object from JSON string data.

        :param str data: the JSON string data.
        :param Optional[int] key_size: the string that will be used to
            cache the JSON string data.
        :param Optional[str] resource_path: the path that will be used to
            load external resource needed by the JSON data.
        :param Optional[str] rlottie_lib_path: Optionally specific where the rlottie
            library is located

        :return: LottieAnimation object
        :rtype: LottieAnimation
        """
        return cls(
            data=data,
            key_size=key_size,
            resource_path=resource_path,
            rlottie_lib_path=rlottie_lib_path,
        )

    @classmethod
    def from_tgs(
        cls, path: str, rlottie_lib_path: Optional[str] = None
    ) -> "LottieAnimation":
        """
        Constructs LottieAnimation object from tgs file path.

        :param str path: tgs resource file path
        :param Optional[str] rlottie_lib_path: Optionally specific where the rlottie
            library is located

        :return: LottieAnimation object
        :rtype: LottieAnimation
        """
        with gzip.open(path) as f:
            data = f.read().decode(encoding="utf-8")
        return cls(data=data, rlottie_lib_path=rlottie_lib_path)

    def lottie_init(self) -> None:
        """
        Runs lottie initialization code when rlottie library is loaded
        dynamically.

        This api should be called before any other api when rlottie library
        is loaded using dlopen() or equivalent.
        """
        self.rlottie_lib.lottie_init.argtypes = []
        self.rlottie_lib.lottie_init.restype = ctypes.c_void_p
        self.rlottie_lib.lottie_init()

    def lottie_shutdown(self) -> None:
        """
        Runs lottie teardown code when rlottie library is loaded
        dynamically.

        This api should be called before unloading the rlottie library for
        proper cleanup of the resource without doing so will result in undefined
        behaviour.
        """
        self.rlottie_lib.lottie_shutdown.argtypes = []
        self.rlottie_lib.lottie_shutdown.restype = ctypes.c_void_p
        self.rlottie_lib.lottie_shutdown()

    def lottie_animation_from_file(self, path: str) -> None:
        """
        Constructs an animation object from JSON file path.

        .. note::
            You should use from_file(path=path) instead

        :param str path: lottie resource file path
        """
        self.rlottie_lib.lottie_animation_from_file.argtypes = [ctypes.c_char_p]
        self.rlottie_lib.lottie_animation_from_file.restype = _LottieAnimationPointer

        if not os.path.isabs(path):
            path = os.path.abspath(path)
        if not os.path.isfile(path):
            raise OSError(f"Cannot find file {path}")

        path_p = ctypes.c_char_p(path.encode())

        self.animation_p = self.rlottie_lib.lottie_animation_from_file(path_p)

        del path_p

    def lottie_animation_from_data(
        self,
        data: str,
        key_size: Optional[int] = None,
        resource_path: Optional[str] = None,
    ) -> None:
        """
        Constructs an animation object from JSON string data.

        .. note::
            You should use from_data(data=data) instead

        :param str data: the JSON string data.
        :param Optional[int] key_size: the size of string that will be used to
            cache the JSON string data.
        :param Optional[str] resource_path: the path that will be used to
            load external resource needed by the JSON data.
        """
        self.data_c = ctypes.create_string_buffer(data.encode())
        data_size = ctypes.sizeof(self.data_c)

        if key_size is None:
            key_size = data_size
        self.key_c = ctypes.create_string_buffer(key_size)

        resource_path_abs = ""
        if resource_path is not None:
            resource_path_abs = os.path.abspath(resource_path)
        self.resource_path_abs_c = ctypes.create_string_buffer(
            resource_path_abs.encode()
        )
        resource_path_abs_size = ctypes.sizeof(self.resource_path_abs_c)

        self.rlottie_lib.lottie_animation_from_data.argtypes = [
            ctypes.POINTER(ctypes.c_char * data_size),
            ctypes.POINTER(ctypes.c_char * key_size),
            ctypes.POINTER(ctypes.c_char * resource_path_abs_size),
        ]
        self.rlottie_lib.lottie_animation_from_data.restype = _LottieAnimationPointer

        self.animation_p = self.rlottie_lib.lottie_animation_from_data(
            ctypes.byref(self.data_c),
            ctypes.byref(self.key_c),
            ctypes.byref(self.resource_path_abs_c),
        )

    def lottie_animation_destroy(self) -> None:
        """
        Free given Animation object resource.

        Call this before loading new lottie animation.
        """
        if not self.animation_p:
            return

        self.rlottie_lib.lottie_animation_destroy.argtypes = [_LottieAnimationPointer]
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
        """
        Returns default viewport size of the Lottie resource.

        :return: width, height
        :rtype: Tuple[int, int]
        """
        self.rlottie_lib.lottie_animation_get_size.argtypes = [
            _LottieAnimationPointer,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_size_t),
        ]
        self.rlottie_lib.lottie_animation_get_size.restype = ctypes.c_void_p

        width_c = ctypes.c_size_t()
        height_c = ctypes.c_size_t()
        self.rlottie_lib.lottie_animation_get_size(
            self.animation_p, ctypes.byref(width_c), ctypes.byref(height_c)
        )

        width = width_c.value
        height = height_c.value

        del width_c, height_c

        return width, height

    def lottie_animation_get_duration(self) -> int:
        """
        Returns total animation duration of Lottie resource in second.

        :return: duration
        :rtype: int
        """
        self.rlottie_lib.lottie_animation_get_duration.argtypes = [
            _LottieAnimationPointer
        ]
        self.rlottie_lib.lottie_animation_get_duration.restype = ctypes.c_double

        duration = self.rlottie_lib.lottie_animation_get_duration(self.animation_p)
        return duration

    def lottie_animation_get_totalframe(self) -> int:
        """
        Returns total number of frames present in the Lottie resource.

        :return: totalframe
        :rtype: int
        """
        totalframe = self.rlottie_lib.lottie_animation_get_totalframe(self.animation_p)

        return totalframe

    def lottie_animation_get_framerate(self) -> int:
        """
        Returns default framerate of the Lottie resource.

        :return: framerate
        :rtype: int
        """
        self.rlottie_lib.lottie_animation_get_framerate.argtypes = [
            _LottieAnimationPointer
        ]
        self.rlottie_lib.lottie_animation_get_framerate.restype = ctypes.c_double

        framerate = self.rlottie_lib.lottie_animation_get_framerate(self.animation_p)

        return framerate

    def lottie_animation_render_tree(
        self,
        frame_num: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> LOTLayerNode:
        """
        Get the render tree which contains the snapshot of the animation object
        at frame = @c frame_num, the content of the animation in that frame number.

        Example for getting content of render_tree: render_tree.mMaskList.size

        :param int frame_num: Content corresponds to the frame_num needs
            to be drawn. Defaults to 0.
        :param Optional[int] width: Requested snapshot viewport width.
        :param Optional[int] height: Requested snapshot viewport height.

        :return: animation snapshot tree.
        :rtype: rlottie_python.rlottiecommon.LOTLayerNode
        """
        self.rlottie_lib.lottie_animation_render_tree.argtypes = [
            _LottieAnimationPointer,
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_size_t,
        ]
        self.rlottie_lib.lottie_animation_render_tree.restype = ctypes.POINTER(
            LOTLayerNode
        )

        if width is None or height is None:
            width, height = self.lottie_animation_get_size()

        render_tree_p = self.rlottie_lib.lottie_animation_render_tree(
            self.animation_p,
            ctypes.c_size_t(frame_num),
            ctypes.c_size_t(width),
            ctypes.c_size_t(height),
        )

        render_tree = render_tree_p.contents

        del render_tree_p

        return render_tree

    def lottie_animation_get_frame_at_pos(self, pos: float) -> int:
        """
        Maps position to frame number and returns it.

        :param float pos: position in the range [ 0.0 .. 1.0 ].

        :return: Mapped frame number in the range [ start_frame .. end_frame ].
            0 if the Lottie resource has no animation.
        :rtype: int
        """
        self.rlottie_lib.lottie_animation_get_frame_at_pos.argtypes = [
            _LottieAnimationPointer,
            ctypes.c_float,
        ]
        self.rlottie_lib.lottie_animation_get_frame_at_pos.restype = ctypes.c_size_t

        mapped_frame = self.rlottie_lib.lottie_animation_get_frame_at_pos(
            self.animation_p, ctypes.c_float(pos)
        )

        return mapped_frame

    def lottie_animation_render(
        self,
        frame_num: int = 0,
        buffer_size: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        bytes_per_line: Optional[int] = None,
    ) -> bytes:
        """
        Request to render the content of the frame frame_num to buffer.

        :param int frame_num: the frame number needs to be rendered.
            Defaults to 0.
        :param Optional[int] buffer_size: size of surface buffer use for rendering
        :param Optional[int] width: width of the surface
        :param Optional[int] height: height of the surface
        :param Optional[int] bytes_per_line: stride of the surface in bytes.

        :return: rendered surface buffer
        :rtype: bytes
        """
        if width is None or height is None:
            width, height = self.lottie_animation_get_size()

        if bytes_per_line is None:
            bytes_per_line = width * 4

        if buffer_size is None:
            buffer_size = width * height * 4

        buffer_c = ctypes.create_string_buffer(buffer_size)

        self.rlottie_lib.lottie_animation_render.argtypes = [
            _LottieAnimationPointer,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_char * buffer_size),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_size_t,
        ]
        self.rlottie_lib.lottie_animation_render.restype = ctypes.c_void_p

        self.rlottie_lib.lottie_animation_render(
            self.animation_p,
            ctypes.c_size_t(frame_num),
            ctypes.byref(buffer_c),
            ctypes.c_size_t(width),
            ctypes.c_size_t(height),
            ctypes.c_size_t(bytes_per_line),
        )

        buffer = buffer_c.raw

        del buffer_c

        return buffer

    def lottie_animation_render_async(
        self,
        frame_num: int = 0,
        buffer_size: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        bytes_per_line: Optional[int] = None,
    ) -> None:
        """
        Request to render the content of the frame frame_num to buffer asynchronously.

        User must call lottie_animation_render_flush() to make sure render is finished.

        :param int frame_num: the frame number needs to be rendered.
            Defaults to 0.
        :param Optional[int] buffer_size: size of surface buffer use for rendering
        :param Optional[int] width: width of the surface
        :param Optional[int] height: height of the surface
        :param Optional[int] bytes_per_line: stride of the surface in bytes.
        """
        if width is None or height is None:
            width, height = self.lottie_animation_get_size()

        if bytes_per_line is None:
            bytes_per_line = width * 4

        if buffer_size is None:
            buffer_size = width * height * 4

        self.async_buffer_c = ctypes.create_string_buffer(buffer_size)

        self.rlottie_lib.lottie_animation_render_async.argtypes = [
            _LottieAnimationPointer,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_char * buffer_size),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_size_t,
        ]
        self.rlottie_lib.lottie_animation_render_async.restype = ctypes.c_void_p

        self.rlottie_lib.lottie_animation_render_async(
            self.animation_p,
            ctypes.c_size_t(frame_num),
            ctypes.byref(self.async_buffer_c),
            ctypes.c_size_t(width),
            ctypes.c_size_t(height),
            ctypes.c_size_t(bytes_per_line),
        )

    def lottie_animation_render_flush(self) -> bytes:
        """
        Request to finish the current async renderer job for this animation object.

        If render is finished then this call returns immidiately.

        If not, it waits till render job finish and then return.

        User must call lottie_animation_render_async()
        and lottie_animation_render_flush()
        in pair to get the benefit of async rendering.

        :return: the pixel buffer it finised rendering
        :rtype: bytes
        """
        if not self.async_buffer_c:
            raise AttributeError(
                "Nothing was rendered using lottie_animation_render_async()"
            )

        self.rlottie_lib.lottie_animation_get_duration.argtypes = [
            _LottieAnimationPointer
        ]
        self.rlottie_lib.lottie_animation_get_duration.restype = ctypes.c_uint32

        self.rlottie_lib.lottie_animation_render_flush(self.animation_p)

        return bytes(self.async_buffer_c)

    def lottie_animation_property_override(
        self, _type: LottieAnimationProperty, keypath: str, *args: ctypes.c_double
    ) -> None:
        """
        Request to change the properties of this animation object.

        Keypath should conatin object names separated by (.)
        and can handle globe(**) or wildchar(*)

        .. list-table:: Possible values of _types and args
            :header-rows: 1

            * - _type LottieAnimationProperty
              - No. of args
              - args value
              - Description
            * - LOTTIE_ANIMATION_PROPERTY_FILLCOLOR
              - 3 args
              - [0 ... 1]
              - Color property of Fill object:
            * - LOTTIE_ANIMATION_PROPERTY_FILLOPACITY
              - 1 args
              - [0 ... 100]
              - Opacity property of Fill object
            * - LOTTIE_ANIMATION_PROPERTY_STROKECOLOR
              - 3 args
              - [0 ... 1]
              - Color property of Stroke object
            * - LOTTIE_ANIMATION_PROPERTY_STROKEOPACITY
              - 1 args
              - [0 ... 100]
              - Opacity property of Stroke object
            * - LOTTIE_ANIMATION_PROPERTY_STROKEWIDTH
              - 1 args
              - [0 ... +inf]
              - Stroke width property of Stroke object
            * - LOTTIE_ANIMATION_PROPERTY_TR_ANCHOR
              - 0 args
              - Any
              - Transform Anchor property of Layer and Group object
            * - LOTTIE_ANIMATION_PROPERTY_TR_POSITION
              - 2 args
              - Any
              - Transform Position property of Layer and Group object
            * - LOTTIE_ANIMATION_PROPERTY_TR_SCALE
              - 2 args
              - Any
              - Transform Scale property of Layer and Group object
            * - LOTTIE_ANIMATION_PROPERTY_TR_ROTATION
              - 1 args
              - [0 ... 360]
              - Transform Scale property of Layer and Group object
            * - LOTTIE_ANIMATION_PROPERTY_TR_OPACITY
              - 0 args
              - Any
              - Transform Opacity property of Layer and Group object

        Example:
        To change fillcolor property of fill1 object in the
        layer1->group1->fill1 hirarchy to RED color:

        .. code-block:: python

            lottie_animation_property_override(
                LottieAnimationProperty.LOTTIE_ANIMATION_PROPERTY_FILLCOLOR,
                "layer1.group1.fill1",
                ctypes.c_double(1.0),
                ctypes.c_double(0.0),
                ctypes.c_double(0.0)
            )

        If all the color property inside group1 needs to be changed to GREEN color:

        .. code-block:: python

            lottie_animation_property_override(
                LottieAnimationProperty.LOTTIE_ANIMATION_PROPERTY_FILLCOLOR,
                "**.group1.**",
                ctypes.c_double(0.0),
                ctypes.c_double(1.0),
                ctypes.c_double(0.0)
            )

        :param LottieAnimationProperty _type: Property type.
        :param str keypath: Specific content of target.
        :param ctypes.c_double *args: Property values.
        """
        argtypes: List[Any] = [
            _LottieAnimationPointer,
            LottieAnimationProperty,
            ctypes.c_char_p,
        ]
        for _ in args:
            argtypes.append(ctypes.c_double)

        self.rlottie_lib.lottie_animation_property_override.argtypes = argtypes
        self.rlottie_lib.lottie_animation_property_override.restype = ctypes.c_void_p

        self.rlottie_lib.lottie_animation_property_override(
            self.animation_p,
            _type,
            ctypes.c_char_p(keypath.encode("utf-8")),
            *args,
        )

    def lottie_animation_get_markerlist(self) -> Optional[LOTMarkerList]:
        """
        Returns list of markers in the Lottie resource

        LOTMarkerList has a LOTMarker list and size of list

        LOTMarker has the marker's name, start frame, and end frame.

        Example for getting content of markerlist: markerlist.ptr.name

        :return: The list of marker. If there is no marker, return None
        :rtype: Optional[LOTMarkerList]
        """
        self.rlottie_lib.lottie_animation_get_markerlist.argtypes = [
            _LottieAnimationPointer
        ]
        self.rlottie_lib.lottie_animation_get_markerlist.restype = ctypes.POINTER(
            LOTMarkerList
        )

        markerlist = self.rlottie_lib.lottie_animation_get_markerlist(self.animation_p)

        try:
            return markerlist.contents
        except ValueError:  # NULL pointer access
            return None

    def lottie_configure_model_cache_size(self, cache_size: int) -> None:
        """
        Configures rlottie model cache policy.

        Provides Library level control to configure model cache policy.

        Setting it to 0 will disable
        the cache as well as flush all the previously cached content.

        To disable Caching, configure with 0 size.

        To flush the current Cache content, configure it with 0 and
        then reconfigure with the new size.

        :param int cache_size: Maximum Model Cache size.
        """
        self.rlottie_lib.lottie_configure_model_cache_size.argtypes = [ctypes.c_size_t]
        self.rlottie_lib.lottie_configure_model_cache_size.restype = ctypes.c_void_p
        self.rlottie_lib.lottie_configure_model_cache_size(ctypes.c_size_t(cache_size))

    def render_pillow_frame(
        self,
        frame_num: int = 0,
        buffer_size: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        bytes_per_line: Optional[int] = None,
    ) -> "Image.Image":
        """
        Create Pillow Image at frame_num

        :param int frame_num: the frame number needs to be rendered.
            Defaults to 0.
        :param Optional[int] buffer_size: size of surface buffer use for rendering
        :param Optional[int] width: width of the surface
        :param Optional[int] height: height of the surface
        :param Optional[int] bytes_per_line: stride of the surface in bytes.

        :return: rendered Pillow Image
        :rtype: PIL.Image.Image
        """
        from PIL import Image

        if width is None or height is None:
            width, height = self.lottie_animation_get_size()

        buffer = self.lottie_animation_render(
            frame_num=frame_num,
            buffer_size=buffer_size,
            width=width,
            height=height,
            bytes_per_line=bytes_per_line,
        )

        im = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA")  # type: ignore

        return im

    def save_frame(
        self,
        save_path: str,
        frame_num: int = 0,
        buffer_size: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        bytes_per_line: Optional[int] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Save Image at frame_num to save_path

        :param str save_path: path to save the Pillow Image
        :param int frame_num: the frame number needs to be rendered.
            Defaults to 0.
        :param Optional[int] buffer_size: size of surface buffer use for rendering
        :param Optional[int] width: width of the surface
        :param Optional[int] height: height of the surface
        :param Optional[int] bytes_per_line: stride of the surface in bytes.
        :param Any *args: additional arguments passing to im.save()
        :param Any **kwargs: additional arguments passing to im.save()
        """
        im = self.render_pillow_frame(
            frame_num=frame_num,
            buffer_size=buffer_size,
            width=width,
            height=height,
            bytes_per_line=bytes_per_line,
        )
        im.save(save_path, *args, **kwargs)

    def save_animation(
        self,
        save_path: str,
        fps: Optional[int] = None,
        frame_num_start: Optional[int] = None,
        frame_num_end: Optional[int] = None,
        buffer_size: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        bytes_per_line: Optional[int] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Save Image from frame_num_start to frame_num_end and save it to save_path.

        It is possible to save animation as apng, gif or webp.

        For .gif, maximum framerate is capped at 50.

        Users may override this by specifying fps, at risk of breaking their gif.

        :param str save_path: Path to save the Pillow Image
        :param Optional[int] fps: Set fps of output image.
            Will skip frames if lower than original.
        :param Optional[int] frame_num_start: the starting frame number
            needs to be rendered.
        :param Optional[int] frame_num_end: the ending frame number
            needs to be rendered.
        :param Optional[int] buffer_size: size of surface buffer use for rendering
        :param Optional[int] width: width of the surface
        :param Optional[int] height: height of the surface
        :param Optional[int] bytes_per_line: stride of the surface in bytes.
        :param Any *args: additional arguments passing to im.save()
        :param Any **kwargs: additional arguments passing to im.save()
        """
        fps_orig = self.lottie_animation_get_framerate()
        duration = self.lottie_animation_get_duration()

        export_ext = os.path.splitext(save_path)[-1].lower()

        if not fps:
            fps = fps_orig

            # For .gif, maximum framerate is capped at 50
            # Users may override this by specifying fps, at risk of breaking their gif
            # Reference: https://wunkolo.github.io/post/2020/02/buttery-smooth-10fps/
            if export_ext == ".gif" and fps_orig > 50:
                fps = 50

        if export_ext == ".gif" and kwargs.get("disposal") is None:
            kwargs["disposal"] = 2

        if kwargs.get("loop") is None:
            kwargs["loop"] = 0

        frames = int(duration * fps)
        frame_duration = 1000 / fps

        if frame_num_start is None:
            frame_num_start = 0
        if frame_num_end is None:
            frame_num_end = frames

        im_list: List[Image.Image] = []
        for frame in range(frame_num_start, frame_num_end):
            pos = frame / frame_num_end
            frame_num = self.lottie_animation_get_frame_at_pos(pos)
            im_list.append(
                self.render_pillow_frame(
                    frame_num=frame_num,
                    buffer_size=buffer_size,
                    width=width,
                    height=height,
                    bytes_per_line=bytes_per_line,
                ).copy()
            )

        im_list[0].save(
            save_path,
            save_all=True,
            append_images=im_list[1:],
            duration=int(frame_duration),
            *args,
            **kwargs,
        )
