import requests
import numpy as np
import cv2
from datetime import datetime

class Download:
    @staticmethod
    def baixar_imagem(url):
        try:
            # Simula um navegador
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            response.raise_for_status()
            
            # Gera nome do arquivo
            filename = url.split("/")[-1].split('?')[0]
            if len(filename) > 30 or not filename.endswith(('.jpg', '.png', '.jpeg')):
                filename = f"imagem_{int(datetime.now().timestamp())}.jpg"
            
            # Converte bytes para imagem
            image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            img_decoded = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if img_decoded is None: return None, None

            # Salva no disco
            cv2.imwrite(filename, img_decoded)
            return filename, img_decoded
        except Exception as e:
            print(f"Erro no download: {e}")
            return None, None