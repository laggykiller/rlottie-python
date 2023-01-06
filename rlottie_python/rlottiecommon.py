from ctypes import *

# References: rlottie/inc/rlottiecommon.h

# LOTMarkerList -> LOTMarker
class LOTMarker(Structure):
    _fields_ = [
        ('name', c_char_p),
        ('startframe', c_size_t),
        ('endframe', c_size_t)
    ]

# LOTMarkerList
class LOTMarkerList(Structure):
    _fields_ = [
        ('ptr', POINTER(LOTMarker)),
        ('size', c_size_t)
    ]

# LOTLayerNode
class LOTLayerNode(Structure):
    pass

# mClipPath -> mMaskList -> LOTMask -> mPath
class mPath(Structure):
    _fields_ = [
        ('ptPtr', POINTER(c_float)),
        ('ptCount', c_size_t),
        ('elmPtr', c_char_p),
        ('elmCount', c_size_t)
    ]

# mClipPath -> mMaskList -> LOTMask
class LOTMask(Structure):
    _fields_ = [
        ('mPath', mPath),
        ('mMode', c_int),
        ('mAlpha', c_ubyte)
    ]

# mClipPath -> mMaskList
class mMaskList(Structure):
    _fields_ = [
        ('ptr', POINTER(LOTMask)),
        ('size', c_size_t)
    ]

# LOTLayerNode -> mClipPath
class mClipPath(Structure):
    _fields_ = [
        ('ptPtr', POINTER(c_float)),
        ('ptCount', c_size_t),
        ('elmPtr', c_char),
        ('elmCount', c_size_t)
    ]

# LOTLayerNode -> mLayerList
class mLayerList(Structure):
    _fields_ = [
        ('ptr', POINTER(POINTER(LOTLayerNode))),
        ('size', c_size_t)
    ]

# LOTLayerNode -> mNodeList -> LOTNode -> mColor
class mColor(Structure):
    _fields_ = [
        ('r', c_ubyte),
        ('g', c_ubyte),
        ('b', c_ubyte),
        ('a', c_ubyte)
    ]

# LOTLayerNode -> mNodeList -> LOTNode -> mStroke
class mStroke(Structure):
    _fields_ = [
        ('enable', c_ubyte),
        ('width', c_float),
        ('cap', c_int),
        ('join', c_int),
        ('miterLimit', c_float),
        ('dashArray', c_float),
        ('dashArraySize', c_int)
    ]

# LOTLayerNode -> mNodeList -> LOTNode -> mGradient -> LOTGradientStop
class LOTGradientStop(Structure):
    _fields_ = [
        ('pos', c_float),
        ('r', c_ubyte),
        ('g', c_ubyte),
        ('b', c_ubyte),
        ('a', c_ubyte)
    ]

# LOTLayerNode -> mNodeList -> LOTNode -> mGradient -> start,end,center,focal
class coords(Structure):
    _fields_ = [
        ('x', c_float),
        ('y', c_float)
    ]

# LOTLayerNode -> mNodeList -> LOTNode -> mGradient
class mGradient(Structure):
    _fields_ = [
        ('type', c_int),
        ('stropPtr', LOTGradientStop),
        ('stopCount', c_size_t),
        ('start', coords),
        ('end', coords),
        ('center', coords),
        ('focal', coords),
        ('cradius', c_float),
        ('fradius', c_float)
    ]

# LOTLayerNode -> mNodeList -> LOTNode -> mImageInfo -> mMatrix
class mMatrix(Structure):
    _fields_ = [
        ('m11', c_float),
        ('m12', c_float),
        ('m13', c_float),
        ('m21', c_float),
        ('m22', c_float),
        ('m23', c_float),
        ('m31', c_float),
        ('m32', c_float),
        ('m33', c_float)
    ]

# LOTLayerNode -> mNodeList -> LOTNode -> mImageInfo
class mImageInfo(Structure):
    _fields_ = [
        ('data', c_ubyte),
        ('width', c_size_t),
        ('height', c_size_t),
        ('mAlpha', c_ubyte),
        ('mMatrix', mMatrix)
    ]

# LOTLayerNode -> mNodeList -> LOTNode
class LOTNode(Structure):
    _fields_ = [
        ('mPath', mPath),
        ('mColor', mColor),
        ('mStroke', mStroke),
        ('mGradient', mGradient),
        ('mImageInfo', mImageInfo),
        ('mFlag', c_int),
        ('mBrushType', c_int),
        ('mFillRule', c_int),
        ('keypath', c_char_p)
    ]

# LOTLayerNode -> mNodeList
class mNodeList(Structure):
    _fields_ = [
        ('ptr', POINTER(POINTER(LOTNode))),
        ('size', c_size_t)
    ]

LOTLayerNode._fields_ = [
        ('mMaskList', mMaskList),
        ('mClipPath', mClipPath),
        ('mLayerList', mLayerList),
        ('mNodeList', mNodeList),
        ('mMatte', c_int),
        ('mVisible', c_int),
        ('mAlpha', c_ubyte),
        ('keypath', c_char_p)
    ]
