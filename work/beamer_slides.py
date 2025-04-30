from common.convert import pt_to_cm
from common.image import get_image_size

legend_dict = {
    "page1_img1.png": "Commerce Accessoire",
    # "page1_img10.png": "Terrasse Fermée",
    "page1_img2.png": "Contre-Etalage",
    "page1_img3.png": "Etalage",
    "page1_img5.png": "Terrasse Fermée",
    "page1_img6.png": "Contre-Terrasse",
    "page1_img7.png": "Terrasse Ouverte",
    # "page1_img9.png": "background",
}


latex_content = (
    """
\\documentclass{beamer}
\\usepackage[utf8]{inputenc}
\\usepackage{graphicx}
\\usepackage{array}

\\begin{document}

\\begin{frame}
\\frametitle{Tableau d'images avec légendes}
\\begin{columns}
    \\begin{column}{0.5\\textwidth}
    \\begin{tabular}{m{"""
    + str(pt_to_cm(get_image_size("page1_img1.png")[0]) + 1)
    + """cm} l}
"""
)

for img, legend in legend_dict.items():
    latex_content += f"\\includegraphics[scale=1]{{{img}}} & {legend} \\\\ \n"

latex_content += """
    \\end{tabular}
    \\end{column}
    \\begin{column}{0.5\\textwidth}
    % Contenu de la deuxième colonne (vous pouvez ajouter du texte ou d'autres éléments ici)
    \\end{column}
\\end{columns}
\\end{frame}

\\end{document}
"""

with open("beamer_slide.tex", "w", encoding="utf-8") as file:
    file.write(latex_content)

print("Le fichier LaTeX a été généré avec succès.")
