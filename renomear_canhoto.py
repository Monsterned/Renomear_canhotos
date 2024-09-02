import cv2
from pyzbar.pyzbar import decode
import os
import tkinter as tk
from tkinter import messagebox

# Caminho para a pasta contendo as imagens
caminho_imagem = os.path.join(os.getcwd(), 'IMAGENS')

# Extensões de arquivos aceitas
extensoes_aceitas = {".jpg", ".jpeg", ".jfif", ".png"}

# Função para processar a imagem e tentar decodificar QR codes
def processar_imagem(image):
    # Converter a imagem para escala de cinza
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar um filtro de borrão (blur)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    
    # Aplicar limiarização adaptativa (adaptive thresholding)
    thresh_image = cv2.adaptiveThreshold(blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Tentar decodificar QR codes em diferentes variações da imagem
    for img in [image, gray_image, blurred_image, thresh_image]:
        # Ajuste de contraste e brilho
        alpha = 1.5  # Contraste (1.0-3.0)
        beta = 0  # Brilho (0-100)
        adjusted_image = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
        
        # Tentar diferentes rotações
        (h, w) = adjusted_image.shape[:2]
        center = (w // 2, h // 2)
        for angle in range(0, 360, 15):
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated_image = cv2.warpAffine(adjusted_image, M, (w, h))
            
            # Decodificar o QR code
            decoded_objects = decode(rotated_image)
            if decoded_objects:
                return decoded_objects
    
    return None

# Percorrer todos os arquivos na pasta
for nome_arquivo in os.listdir(caminho_imagem):
    # Verificar a extensão do arquivo
    ext = os.path.splitext(nome_arquivo)[1].lower()
    if ext in extensoes_aceitas:
        # Caminho completo do arquivo
        caminho_atual = os.path.join(caminho_imagem, nome_arquivo)
        
        # Carregar a imagem
        image = cv2.imread(caminho_atual)
        
        if image is None:
            print(f"Erro ao carregar a imagem {nome_arquivo}. Verifique o caminho do arquivo.")
            continue
        
        # Processar a imagem para tentar decodificar o QR code
        decoded_objects = processar_imagem(image)
        
        if not decoded_objects:
            print(f"Nenhum QR code encontrado na imagem {nome_arquivo}.")
            continue
        
        # Extrair números das Notas Fiscais
        numeros_notas_fiscais = []
        for obj in decoded_objects:
            chave_de_acesso = obj.data.decode("utf-8")
            print(f"Chave de Acesso encontrada na imagem {nome_arquivo}: {chave_de_acesso}")
            
            # Verificar se a chave tem o formato esperado e extrair o número
            if len(chave_de_acesso) >= 34:
                numero_nota_fiscal = chave_de_acesso[25:34]
                numeros_notas_fiscais.append(numero_nota_fiscal)
                print(f"Número da Nota Fiscal: {numero_nota_fiscal}")
            else:
                print(f"Chave de Acesso {chave_de_acesso} não tem o comprimento esperado.")
        
        if not numeros_notas_fiscais:
            print(f"Nenhum número de Nota Fiscal válido encontrado na imagem {nome_arquivo}.")
            continue
        
        # Definir o novo nome para a imagem com todos os números encontrados
        novo_nome = "_".join(numeros_notas_fiscais) + ".jpeg"
        print(f"Novo nome proposto: {novo_nome}")
        
        # Definir o caminho completo com o novo nome
        caminho_novo = os.path.join(caminho_imagem, novo_nome)
        
        try:
            # Renomear a imagem
            os.rename(caminho_atual, caminho_novo)
            print(f"Imagem '{nome_arquivo}' renomeada para '{novo_nome}'")
        except FileExistsError:
            print(f"Erro: O arquivo '{novo_nome}' já existe.")
        except Exception as e:
            print(f"Erro ao renomear '{nome_arquivo}': {e}")

print("Processo de renomeação concluído.")

# Mostrar caixa de aviso usando tkinter
root = tk.Tk()
root.withdraw()  # Oculta a janela principal
messagebox.showinfo("Aviso", "Processo finalizado com sucesso!")
