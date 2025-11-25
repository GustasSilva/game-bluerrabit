import pygame
import os

# --- CONFIGURAÇÃO ---
LARGURA_FINAL = 48
ALTURA_FINAL = 48
PASTA_IMAGENS = 'images'

print(f"Iniciando padronização das imagens na pasta '{PASTA_IMAGENS}' para {LARGURA_FINAL}x{ALTURA_FINAL}...")

# Inicializa o pygame (necessário para manipular imagens)
pygame.init()
pygame.display.set_mode((1, 1)) # Janela invisível necessária

# Percorre todos os arquivos da pasta
for nome_arquivo in os.listdir(PASTA_IMAGENS):
    if nome_arquivo.endswith(".png"):
        caminho_completo = os.path.join(PASTA_IMAGENS, nome_arquivo)
        
        try:
            # 1. Carrega a imagem como ela está agora
            img_original = pygame.image.load(caminho_completo).convert_alpha()
            w, h = img_original.get_size()
            
            # Verificação opcional: Se já estiver 48x48, avisa e pula
            if w == LARGURA_FINAL and h == ALTURA_FINAL:
                print(f"[PULADO] {nome_arquivo} já está correto ({w}x{h}).")
                continue
            
            # 2. FORÇA o redimensionamento para 48x48 (transform.scale)
            # Isso vai esticar ou encolher a imagem para caber exatamente no quadrado
            img_nova = pygame.transform.scale(img_original, (LARGURA_FINAL, ALTURA_FINAL))
            
            # 3. Salva substituindo o arquivo original
            pygame.image.save(img_nova, caminho_completo)
            print(f"[CORRIGIDO] {nome_arquivo}: {w}x{h} -> {LARGURA_FINAL}x{ALTURA_FINAL}")
            
        except Exception as e:
            print(f"[ERRO] Não foi possível alterar {nome_arquivo}: {e}")

print("\nConcluído! Todas as imagens agora são 48x48.")
pygame.quit()