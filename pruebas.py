###########################import tkinter as tk
import tkinter as tk
# Crear la ventana
ventana = tk.Tk()

# Crear los elementos
elemento1 = tk.Label(ventana, text="Elemento 1")
elemento2 = tk.Label(ventana, text="Elemento 2")
elemento3 = tk.Label(ventana, text="Elemento 3")
elemento4 = tk.Label(ventana, text="Elemento 4")

# Posicionar los elementos en la parte inferior
elemento1.pack(side="bottom")
elemento2.pack(side="bottom")
elemento3.pack(side="bottom")
elemento4.pack(side="bottom")

# Iniciar el bucle principal de la ventana
ventana.mainloop()
