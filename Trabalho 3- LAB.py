import cv2
import numpy as np
import os
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from abc import ABC, abstractmethod
from datetime import datetime


COR_FUNDO = "#202020"    
COR_TEXTO = "#FFFFFF"    
COR_BOTAO = "#404040"    


class Download:
    @staticmethod
    def baixar_imagem(url):
        try:
            # Simula um navegador para evitar bloqueios
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            response.raise_for_status()
            
            # Pega o nome do arquivo ou gera um genérico
            filename = url.split("/")[-1].split('?')[0]
            if len(filename) > 30 or not filename.endswith(('.jpg', '.png', '.jpeg')):
                filename = f"imagem_{int(datetime.now().timestamp())}.jpg"
            
            # Converte bytes direto para imagem (evita erros de arquivo corrompido)
            image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            img_decoded = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if img_decoded is None: return None, None

            # Salva no disco (Requisito do projeto)
            cv2.imwrite(filename, img_decoded)
            return filename, img_decoded
        except Exception as e:
            print(e)
            return None, None


class Imagem:
    def __init__(self, caminho, dados_ja_carregados=None):
        self.caminho = caminho
        self.dados_imagem = dados_ja_carregados
        self.imagem_exibicao = None

    def carregar(self):
        # Se já baixou, usa a memória. Se não, lê do disco.
        if self.dados_imagem is None:
            if not os.path.exists(self.caminho):
                raise FileNotFoundError("Arquivo não encontrado")
            # Leitura segura para Windows com acentos
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


class Principal:
    def __init__(self):
        self.janela = tk.Tk()
        self.janela.title("Trabalho Final - Editor de Imagens")
        self.janela.geometry("900x650")
        self.janela.configure(bg=COR_FUNDO)

        self.imagem_obj = None
        self.filtros = {
            'Cinza': FiltroCinza(), 'P&B': FiltroPB(),
            'Cartoon': FiltroCartoon(), 'Negativo': FiltroNegativo(),
            'Contorno': FiltroContorno(), 'Blur': FiltroBlur()
        }

        self._criar_interface()

    def _criar_interface(self):
       
        frame_top = tk.Frame(self.janela, bg=COR_FUNDO)
        frame_top.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_top, text="URL ou Caminho:", bg=COR_FUNDO, fg=COR_TEXTO).pack(side="left")
        
        self.entrada = tk.Entry(frame_top, width=50)
        self.entrada.pack(side="left", padx=10)

        tk.Button(frame_top, text="Carregar", command=self.carregar_url, bg="#007acc", fg="white").pack(side="left", padx=5)
        tk.Button(frame_top, text="Buscar Local", command=self.buscar_local, bg="#555", fg="white").pack(side="left")

        
        self.lbl_imagem = tk.Label(self.janela, text="Nenhuma imagem", bg="black", fg="gray")
        self.lbl_imagem.pack(expand=True, fill="both", padx=10, pady=10)

        
        frame_bot = tk.Frame(self.janela, bg=COR_FUNDO)
        frame_bot.pack(fill="x", pady=10)

        tk.Label(frame_bot, text="Filtros:", bg=COR_FUNDO, fg=COR_TEXTO).pack()

        # Cria botões lado a lado
        frame_btns = tk.Frame(frame_bot, bg=COR_FUNDO)
        frame_btns.pack(pady=5)
        
        for nome in self.filtros:
            btn = tk.Button(frame_btns, text=nome, width=10, bg=COR_BOTAO, fg=COR_TEXTO,
                            command=lambda n=nome: self.aplicar_filtro(n))
            btn.pack(side="left", padx=5)

        # Botões extras exigidos (Listar e Sair)
        frame_extras = tk.Frame(self.janela, bg=COR_FUNDO)
        frame_extras.pack(fill="x", pady=10)
        tk.Button(frame_extras, text="Listar Arquivos da Pasta", command=self.listar_arquivos, bg="#444", fg="white").pack(side="left", padx=20)
        tk.Button(frame_extras, text="SAIR", command=self.janela.destroy, bg="red", fg="white", width=10).pack(side="right", padx=20)


    def carregar_url(self):
        url = self.entrada.get()
        if not url: return
        
        nome, dados = Download.baixar_imagem(url)
        if dados is not None:
            self.imagem_obj = Imagem(nome, dados)
            self.imagem_obj.carregar()
            self.mostrar_imagem()
        else:
            messagebox.showerror("Erro", "Erro ao baixar. Tente outro link ou verifique a internet.")

    def buscar_local(self):
        path = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png *.jpeg")])
        if path:
            self.entrada.delete(0, tk.END)
            self.entrada.insert(0, path)
            self.imagem_obj = Imagem(path)
            try:
                self.imagem_obj.carregar()
                self.mostrar_imagem()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def mostrar_imagem(self):
        if self.imagem_obj:
            # Pega o tamanho da janela para ajustar imagem
            w = self.janela.winfo_width() - 50
            h = self.janela.winfo_height() - 200
            img_tk = self.imagem_obj.get_tk_image(max(w, 400), max(h, 300))
            self.lbl_imagem.config(image=img_tk, text="")
            self.lbl_imagem.image = img_tk

    def aplicar_filtro(self, nome_filtro):
        if not self.imagem_obj: return messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
        
        filtro = self.filtros[nome_filtro]
        img_processada = filtro.aplicar(self.imagem_obj.dados_imagem)
        
        # Atualiza a exibição e salva
        self.imagem_obj.imagem_exibicao = img_processada
        self.mostrar_imagem()
        nome_salvo = self.imagem_obj.salvar(nome_filtro)
        print(f"Salvo: {nome_salvo}")

    def listar_arquivos(self):
        arquivos = [f for f in os.listdir('.') if f.endswith(('.jpg', '.png'))]
        msg = "\n".join(arquivos) if arquivos else "Nenhum arquivo encontrado."
        messagebox.showinfo("Arquivos no Diretório", msg)

    def executar(self):
        self.janela.mainloop()

if __name__ == "__main__":
    app = Principal()
    app.executar()