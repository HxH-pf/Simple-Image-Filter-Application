import os
import cv2
import numpy as np
from PIL import Image, ImageTk

class Imagem:
    def __init__(self, caminho, dados_ja_carregados=None):
        self.caminho = caminho
        self.dados_imagem = dados_ja_carregados
        self.imagem_exibicao = None

    def carregar(self):
        if self.dados_imagem is None:
            if not os.path.exists(self.caminho):
                raise FileNotFoundError("Arquivo não encontrado")
            
            # Leitura segura para Windows
            with open(self.caminho, "rb") as f:
                bytes_img = bytearray(f.read())
                numpy_array = np.asarray(bytes_img, dtype=np.uint8)
                self.dados_imagem = cv2.imdecode(numpy_array, cv2.IMREAD_COLOR)
        
        self.imagem_exibicao = self.dados_imagem.copy()

    def salvar(self, filtro_nome):
        if self.imagem_exibicao is None: return
        nome_base = os.path.basename(self.caminho).split('.')[0]
        if len(nome_base) > 15: nome_base = "imagem"
        novo_nome = f"{nome_base}_{filtro_nome}.jpg"
        cv2.imwrite(novo_nome, self.imagem_exibicao)
        return novo_nome

    def get_tk_image(self, w_max, h_max):
        if self.imagem_exibicao is None: return None
        # Converte BGR (OpenCV) para RGB (Tela)
        img_rgb = cv2.cvtColor(self.imagem_exibicao, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_pil.thumbnail((w_max, h_max))
        return ImageTk.PhotoImage(img_pil)