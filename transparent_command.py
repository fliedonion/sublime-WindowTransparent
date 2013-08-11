import sublime, sublime_plugin
import os

if os.name == 'nt':
    from ctypes import windll, POINTER, byref
    from ctypes.wintypes import c_int32, DWORD, HWND, c_uint16, c_ubyte, BOOL, LONG

    GWL_EXSTYLE = 0xFFFFFFEC
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020 # background clickable 
    LWA_ALPHA = 0x00000002
    LWA_COLORKEY = 0x00000001


    '''SetLayeredWindowAttributes(hWnd, crKey, bAlpha, dwFlags)'''
    SetLayeredWindowAttributes = windll.user32.SetLayeredWindowAttributes
    SetLayeredWindowAttributes.argtypes = [HWND, DWORD, c_ubyte, DWORD]
    SetLayeredWindowAttributes.restypes = BOOL

    '''GetLayeredWindowAttributes(hWnd, *pcrKey, *pbAlpha, *pdwFlags)'''
    GetLayeredWindowAttributes = windll.user32.GetLayeredWindowAttributes
    GetLayeredWindowAttributes.argtypes = [c_int32, POINTER(DWORD), POINTER(c_ubyte), POINTER(DWORD)]
    GetLayeredWindowAttributes.restypes = BOOL


    '''GetWindowLong(hWnd, nIndex)'''
    GetWindowLong = windll.user32.GetWindowLongW
    GetWindowLong.argtypes = [HWND, c_int32]
    GetWindowLong.restypes = LONG

    '''SetWindowLong(hWnd, nIndex, dwNewLong)'''
    SetWindowLong = windll.user32.SetWindowLongW
    SetWindowLong.argtypes = [HWND, c_int32, LONG]
    SetWindowLong.restypes = LONG




class WindowTransparentCommand(sublime_plugin.WindowCommand):
    def set_alpha(self, val):
        hwnd = self.window.hwnd()
        currentLong = GetWindowLong(hwnd, GWL_EXSTYLE)
        SetWindowLong(hwnd, GWL_EXSTYLE, currentLong | WS_EX_LAYERED )

        val = 255 if val > 255 else 150 if val < 150 else val
        SetLayeredWindowAttributes(hwnd, 0, val, LWA_ALPHA)

    def get_alpha(self):
        hwnd = self.window.hwnd()
        d, b, f = DWORD(), c_ubyte(), DWORD()
        GetLayeredWindowAttributes(hwnd, byref(d), byref(b), byref(f))
        print b
        if 0 == f.value:
            return 255
        return b.value

    def increase_alpha(self, *args):
        self.set_alpha(self.get_alpha() * 1 + 10)

    def decrease_alpha(self, *args):
        self.set_alpha(self.get_alpha() - 10)

    def run(self, **kwargs):
        if os.name != 'nt':
            print "windows only."
            return

        opt = ""
        if kwargs.has_key("opt"):
            opt = kwargs["opt"]

        val = 0
        if kwargs.has_key("val"):
            val = int(kwargs["val"])

        {
          "val": self.set_alpha,
          "inc": self.increase_alpha,
          "dec": self.decrease_alpha,
        }.get(opt, self.set_alpha)(val)

