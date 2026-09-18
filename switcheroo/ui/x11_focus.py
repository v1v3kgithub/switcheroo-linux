"""X11 helper to force window activation and bypass focus-stealing prevention."""

import ctypes
import logging

logger = logging.getLogger(__name__)


class XClientMessageData(ctypes.Union):
    _fields_ = [
        ("b", ctypes.c_char * 20),
        ("s", ctypes.c_short * 10),
        ("l", ctypes.c_long * 5),
    ]


class XClientMessageEvent(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),
        ("serial", ctypes.c_ulong),
        ("send_event", ctypes.c_int),
        ("display", ctypes.c_void_p),
        ("window", ctypes.c_ulong),
        ("message_type", ctypes.c_ulong),
        ("format", ctypes.c_int),
        ("data", XClientMessageData),
    ]


try:
    _x11 = ctypes.CDLL("libX11.so.6")
    _x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    _x11.XOpenDisplay.restype = ctypes.c_void_p
    _x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    _x11.XCloseDisplay.restype = ctypes.c_int
    _x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
    _x11.XDefaultRootWindow.restype = ctypes.c_ulong
    _x11.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    _x11.XInternAtom.restype = ctypes.c_ulong
    _x11.XSendEvent.argtypes = [
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.c_int,
        ctypes.c_long,
        ctypes.c_void_p,
    ]
    _x11.XSendEvent.restype = ctypes.c_int
    _x11.XSetInputFocus.argtypes = [
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.c_int,
        ctypes.c_ulong,
    ]
    _x11.XSetInputFocus.restype = ctypes.c_int
    _x11.XFlush.argtypes = [ctypes.c_void_p]
    _x11.XFlush.restype = ctypes.c_int
    _x11_available = True
except Exception as e:
    logger.warning("Could not load libX11: %s", e)
    _x11_available = False


def force_window_focus(xid: int, current_active_xid: int = 0) -> bool:
    """Forces X11 focus and activates the window using EWMH source indication 2 (pager)."""
    if not _x11_available or not xid:
        return False

    disp = _x11.XOpenDisplay(None)
    if not disp:
        return False

    try:
        root = _x11.XDefaultRootWindow(disp)
        net_active_win = _x11.XInternAtom(disp, b"_NET_ACTIVE_WINDOW", 0)

        # 1. Send EWMH _NET_ACTIVE_WINDOW message with source indication = 2 (Pager/Switcher)
        # Window managers (Muffin, Mutter, KWin) always honor pager activation
        event = XClientMessageEvent()
        event.type = 33  # ClientMessage
        event.serial = 0
        event.send_event = 1
        event.display = disp
        event.window = xid
        event.message_type = net_active_win
        event.format = 32
        event.data.l[0] = 2  # Source indication: 2 = Pager / Task Switcher
        event.data.l[1] = 0  # CurrentTime
        event.data.l[2] = current_active_xid
        event.data.l[3] = 0
        event.data.l[4] = 0

        mask = (1 << 20) | (1 << 21)  # SubstructureRedirectMask | SubstructureNotifyMask
        _x11.XSendEvent(disp, root, 0, mask, ctypes.byref(event))

        # 2. Directly request X server keyboard focus
        _x11.XSetInputFocus(disp, xid, 2, 0)  # 2 = RevertToParent, 0 = CurrentTime
        _x11.XFlush(disp)
        return True
    except Exception as e:
        logger.error("Failed to force window focus via X11: %s", e)
        return False
    finally:
        _x11.XCloseDisplay(disp)
