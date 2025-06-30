# animate_tremble_gifs.py

import os
import math
from PIL import Image

def make_tremble_gif(
    input_path: str,
    output_path: str,
    n_frames: int = 10,
    amplitude: int = 3,
    frame_duration: int = 80
):
    """
    Crea un GIF en output_path con n_frames cuadros donde la imagen
    en input_path tiembla ±amplitude píxeles.
    """
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size

    # Añadimos un margen para que el temblor no recorte la imagen
    margin = amplitude + 2
    canvas_w, canvas_h = w + margin*2, h + margin*2

    frames = []
    for i in range(n_frames):
        # Cálculo de desplazamiento senoidal
        theta = 2 * math.pi * i / n_frames
        dx = int(amplitude * math.sin(theta * 2))  # 2 ciclos por bucle
        dy = int(amplitude * math.sin(theta * 3 + math.pi/4))  # fase distinta

        # Creamos fondo transparente y pegamos la imagen con offset
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0,0,0,0))
        x = margin + dx
        y = margin + dy
        canvas.paste(img, (x, y), img)
        frames.append(canvas)

    # Guardamos como GIF animado
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration,
        loop=0,
        disposal=2
    )
    print(f"[✔] GIF creado: {output_path}")

def batch_tremble(
    src_folder: str = "png",
    dst_folder: str = "ducks"
):
    for fname in sorted(os.listdir(src_folder)):
        if not fname.lower().endswith(".png"):
            continue
        in_path  = os.path.join(src_folder, fname)
        name, _ = os.path.splitext(fname)
        out_path = os.path.join(dst_folder, f"{name}.gif")
        make_tremble_gif(in_path, out_path)

if __name__ == "__main__":
    """
    pip install pillow
    - png/   # tus 5 PNG de pato ya recortados
    - ducks/ # aquí caerán los GIFs animados
    """
    batch_tremble()
