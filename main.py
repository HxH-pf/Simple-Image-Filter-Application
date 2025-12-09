import tkinter as tk
from tkinter import filedialog, messagebox
import os

from constantes import COR_FUNDO, COR_TEXTO, COR_BOTAO
from download import Download
from imagem import Imagem
from filtros import FiltroCinza, FiltroPB, FiltroCartoon, FiltroNegativo, FiltroContorno, FiltroBlur

class Principal:
    def __init__(self):
        self.janela = tk.Tk()
        self.janela.title("Trabalho Final - Editor de Imagens")
        self.janela.geometry("900x650")
        self.janela.configure(bg=COR_FUNDO)

        self.imagem_obj = None
        # Dicionário mapeando nomes aos objetos dos filtros importados
        self.filtros = {
            'Cinza': FiltroCinza(), 
            'P&B': FiltroPB(),
            'Cartoon': FiltroCartoon(), 
            'Negativo': FiltroNegativo(),
            'Contorno': FiltroContorno(), 
            'Blur': FiltroBlur()
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

        frame_btns = tk.Frame(frame_bot, bg=COR_FUNDO)
        frame_btns.pack(pady=5)
        
        for nome in self.filtros:
            btn = tk.Button(frame_btns, text=nome, width=10, bg=COR_BOTAO, fg=COR_TEXTO,
                            command=lambda n=nome: self.aplicar_filtro(n))
            btn.pack(side="left", padx=5)

        frame_extras = tk.Frame(self.janela, bg=COR_FUNDO)
        frame_extras.pack(fill="x", pady=10)
        tk.Button(frame_extras, text="Listar Arquivos da Pasta", command=self.listar_arquivos, bg="#444", fg="white").pack(side="left", padx=20)
        tk.Button(frame_extras, text="SAIR", command=self.janela.destroy, bg="red", fg="white", width=10).pack(side="right", padx=20)

    def carregar_url(self):
        url = self.entrada.get()
        if not url: return
        
        # Usa a classe Download importada
        nome, dados = Download.baixar_imagem(url)
        if dados is not None:
            self.imagem_obj = Imagem(nome, dados)
            self.imagem_obj.carregar()
            self.mostrar_imagem()
        else:
            messagebox.showerror("Erro", "Erro ao baixar. Tente outro link.")

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
            w = self.janela.winfo_width() - 50
            h = self.janela.winfo_height() - 200
            img_tk = self.imagem_obj.get_tk_image(max(w, 400), max(h, 300))
            self.lbl_imagem.config(image=img_tk, text="")
            self.lbl_imagem.image = img_tk

    def aplicar_filtro(self, nome_filtro):
        if not self.imagem_obj: return messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
        
        filtro = self.filtros[nome_filtro]
        img_processada = filtro.aplicar(self.imagem_obj.dados_imagem)
        
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