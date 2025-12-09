import cv2
from abc import ABC, abstractmethod

class FiltroBase(ABC):
    @abstractmethod
    def aplicar(self, img): pass

class FiltroCinza(FiltroBase):
    def aplicar(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

class FiltroPB(FiltroBase): 
    def aplicar(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, wb = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        return cv2.cvtColor(wb, cv2.COLOR_GRAY2BGR)

class FiltroNegativo(FiltroBase):
    def aplicar(self, img): return cv2.bitwise_not(img)

class FiltroCartoon(FiltroBase):
    def aplicar(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, 9, 300, 300)
        return cv2.bitwise_and(color, color, mask=edges)

class FiltroContorno(FiltroBase):
    def aplicar(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return cv2.cvtColor(cv2.bitwise_not(edges), cv2.COLOR_GRAY2BGR)

class FiltroBlur(FiltroBase):
    def aplicar(self, img): return cv2.GaussianBlur(img, (15,15), 0)