import tkinter as tk
from PIL import Image, ImageTk
import io
import base64

# Fonction pour créer une image de fond dégradé bleu ciel
def create_gradient_background(width=1200, height=800):
    """Crée une image de fond avec un dégradé bleu ciel"""
    from PIL import Image, ImageDraw
    
    # Créer une nouvelle image avec un fond transparent
    image = Image.new('RGBA', (width, height), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Couleurs pour le dégradé (bleu ciel uniquement)
    colors = [
        (135, 206, 235),  # Bleu ciel
        (176, 224, 230),  # Bleu ciel poudré
        (173, 216, 230),  # Bleu ciel clair
        (240, 248, 255)   # Bleu ciel très clair
    ]
    
    # Créer un dégradé
    segments = len(colors) - 1
    segment_height = height // segments
    
    for i in range(segments):
        color1 = colors[i]
        color2 = colors[i+1]
        
        # Dessiner un rectangle pour chaque segment du dégradé
        for y in range(segment_height):
            # Calculer la couleur du pixel en fonction de la position
            r = int(color1[0] + (color2[0] - color1[0]) * y / segment_height)
            g = int(color1[1] + (color2[1] - color1[1]) * y / segment_height)
            b = int(color1[2] + (color2[2] - color1[2]) * y / segment_height)
            
            # Dessiner une ligne horizontale avec cette couleur
            draw.line([(0, i*segment_height + y), (width, i*segment_height + y)], fill=(r, g, b, 180))
    
    # Ajouter quelques cercles décoratifs semi-transparents
    for i in range(20):
        import random
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(20, 100)
        opacity = random.randint(30, 70)
        r, g, b = colors[random.randint(0, len(colors)-1)]
        draw.ellipse((x, y, x+size, y+size), fill=(r, g, b, opacity))
    
    return image

# Fonction pour charger l'image de fond
def get_background_image(width=1200, height=800):
    """Renvoie une image de fond bleu ciel pour l'interface"""
    try:
        # Générer une image de fond
        image = create_gradient_background(width, height)
        
        # Convertir en PhotoImage pour Tkinter
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Erreur lors de la création de l'image de fond: {e}")
        return None

# Fonction pour créer un canvas de fond
def create_background_canvas(root, width=1200, height=800):
    """Crée un canvas avec une image de fond dégradée bleu ciel"""
    # Créer le canvas
    canvas = tk.Canvas(root, width=width, height=height, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Obtenir l'image de fond
    bg_image = get_background_image(width, height)
    
    if bg_image:
        # Ajouter l'image au canvas
        canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)
        # Garder une référence à l'image (sinon elle sera collectée par le garbage collector)
        canvas.image = bg_image
    
    return canvas

# Fonction pour appliquer un style bleu ciel aux widgets
def apply_blue_style(widget):
    """Applique un style bleu ciel aux widgets Tkinter"""
    colors = {
        "primary": "#87CEEB",    # Bleu ciel
        "secondary": "#B0E0E6",  # Bleu ciel poudré
        "accent": "#ADD8E6",     # Bleu ciel clair
        "light": "#F0F8FF",      # Bleu ciel très clair
        "white": "#FFFFFF"       # White
    }
    
    # Configurer les widgets selon leur type
    widget_type = widget.winfo_class()
    
    if widget_type in ("Button", "TButton"):
        widget.configure(
            bg=colors["primary"], 
            fg=colors["white"],
            activebackground=colors["secondary"],
            activeforeground=colors["white"]
        )
    elif widget_type in ("Label", "TLabel"):
        widget.configure(
            bg=colors["light"], 
            fg=colors["primary"]
        )
    elif widget_type in ("Frame", "TFrame"):
        widget.configure(bg=colors["light"])
    elif widget_type in ("Entry", "TEntry"):
        widget.configure(
            bg=colors["white"],
            fg=colors["primary"],
            insertbackground=colors["primary"]
        )
    
    # Appliquer récursivement aux widgets enfants
    for child in widget.winfo_children():
        apply_blue_purple_style(child)

# Test du module
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test de fond bleu ciel")
    root.geometry("800x600")
    
    # Créer le canvas de fond
    canvas = create_background_canvas(root, 800, 600)
    
    # Ajouter quelques widgets de test
    frame = tk.Frame(canvas, bg="white", bd=2, relief=tk.RAISED)
    canvas.create_window(400, 300, window=frame, width=400, height=300)
    
    label = tk.Label(frame, text="Interface AniData VPN", font=("Helvetica", 16, "bold"))
    label.pack(pady=20)
    
    button = tk.Button(frame, text="Connecter", padx=20, pady=10)
    button.pack(pady=20)
    
    # Appliquer le style bleu
    apply_blue_style(frame)
    
    root.mainloop()