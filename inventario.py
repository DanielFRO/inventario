from configparser import ConfigParser
import mysql.connector as MsqlConnect
import tkinter as tk
from tkinter import Tk, ttk
from PIL import Image, ImageTk

# Clase encargada de establecer un canal de comunicacion estable con la BD
class ConectarConMySQL():
    def __init__(self):
        super().__init__()
        self.mycursor = None

    @staticmethod
    def conectarMySQL():
        global mydb
        global mycursor
        host = None
        user = None
        password = None
        flag_reconexion = False

        # Intenta establecer una conexión con el gestor de la base de datos MYSQL lanzado por XAMPP
        try:
            host, user, password = ConectarConMySQL.extractVarsConnect()
            mydb = MsqlConnect.connect(
                host=host,
                user=user,
                password=password
            )
            mycursor = mydb.cursor()

            if flag_reconexion is False:
                ConectarConMySQL.crearBD(mydb, mycursor)
            else:
                mycursor.execute("USE inventario")
        except Exception as e:
            # Se le informa al usuario el error en la conexión
            print('Error en la conexión:', str(e))
        
        return mydb, mycursor

    @staticmethod
    def crearBD(mydb, mycursor):
        try:
            mycursor.execute("CREATE DATABASE IF NOT EXISTS inventario")
            mycursor.execute("USE inventario")

            # Usamos nuestro objeto para poder ejecutar el comando
            mycursor.execute('''CREATE TABLE IF NOT EXISTS productos 
                                (id_product INT AUTO_INCREMENT PRIMARY KEY,
                                modelo VARCHAR(20),
                                precio VARCHAR(20),
                                serial VARCHAR(20) NOT NULL,
                                fecha_ingreso TIMESTAMP DEFAULT NOW(),
                                proveedor VARCHAR(20) NOT NULL,
                                caracteristicas VARCHAR(30))''')
            mycursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                                (id_user INT AUTO_INCREMENT PRIMARY KEY,
                                user VARCHAR(20),
                                password VARCHAR(20))''')

            # Guarda los cambios en BD
            mydb.commit()
        except Exception as e:
            # Se le informa al usuario el error en la conexión
            print('Error al crear las tablas de la base de datos:', str(e))

    @staticmethod
    def extractVarsConnect():
        file = 'inventario.ini'

        config = ConfigParser()
        config.read(file)

        host = config.get('server', 'host')
        user = config.get('server', 'user')
        password = config.get('server', 'password')

        return host, user, password

    @staticmethod
    def procesarquery(query):
        if query[0] == 'S':
            mycursor.execute(query)
            resultados = mycursor.fetchall()
            return resultados
        else:
            mycursor.execute(query)
            mydb.commit()
            
class IniciarSesion(ConectarConMySQL):
    def __init__(self):
        super().__init__()
        self.user = None
        self.password = None

    @staticmethod
    def autentication(entry_username, entry_password):
        comprobante_usuario = ("SELECT COUNT(*) FROM USUARIOS WHERE user = '{}'".format(entry_username))
        result_1 = ConectarConMySQL.procesarquery(comprobante_usuario)

        comprobante_password = ("SELECT COUNT(*) FROM USUARIOS WHERE password = '{}'".format(entry_password))
        result_2 = ConectarConMySQL.procesarquery(comprobante_password)

        if result_1[0][0] == 1 and result_2[0][0] == 1:
            return True
        else:
            return False
        
class CrearVentanasGraficas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.mycursor = None

    def create_login_window(self):
        self.title("Inicio de sesion")

        # Fija el tamaño de la ventana en 800x600 pixeles y lo deshabilita para redimensionar
        self.geometry("800x600")
        self.resizable(False, False)
        
        # Obtiene el tamaño de la pantalla
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        
        # Calcula las coordenadas para centrar la ventana
        x = int((self.screen_width / 2) - (800 / 2))
        y = int((self.screen_height / 2) - (600 / 2))
        
        self.geometry(f"800x600+{x}+{y}")  # Establece la geometria de la ventana
        
        # Marco para centrar verticalmente los elementos
        self.frame = tk.Frame(self)
        self.frame.pack(pady=200)
        
        # Elementos de la interfaz de inicio de sesion
        self.label_username = tk.Label(self.frame, text="Nombre de usuario:", font=("Arial", 16))
        self.label_username.pack()
        
        self.entry_username = tk.Entry(self.frame, font=("Arial", 16), width=20)
        self.entry_username.pack()
        
        self.label_password = tk.Label(self.frame, text="Contraseña:", font=("Arial", 16))
        self.label_password.pack()
        
        self.entry_password = tk.Entry(self.frame, show="*", font=("Arial", 16), width=20)
        self.entry_password.pack()
        
        self.button_login = tk.Button(self.frame, text="Iniciar sesion", command = self.login_button_clicked, font=("Arial", 16))
        self.button_login.pack()
        
        self.label_status = tk.Label(self, text="", font=("Arial", 16))
        self.label_status.pack()

        self.mainloop()

    def login_button_clicked(self):
        if IniciarSesion.autentication(self.entry_username.get(), self.entry_password.get()):
            self.label_status.config(text="Credenciales correctas", fg="green")
            self.destroy()
          
            # Aqui se debe llamar la creacion de la una nueva ventana de bienvenida de inicio
            self.mostrar_tabla_inventario()
        else:
            self.label_status.config(text="Credenciales incorrectas", fg="red")

    def mostrar_tabla_inventario(self):

        self.id_seleccionados = []

        # Crea la nueva ventana
        self.ventana_tabla = tk.Tk()
        self.ventana_tabla.title("Inventario")

         # Crea un contenedor para los botones
        self.contenedor_botones = tk.Frame(self.ventana_tabla)
        self.contenedor_botones.pack(anchor="nw", padx=20, pady=10)

        imagen_boton_actualizar = Image.open("actualizar.png")  
        imagen_boton_actualizar = imagen_boton_actualizar.resize((20, 20))  # Ajusta el tamaño de la imagen según sea necesario
        imagen_boton_actualizar = ImageTk.PhotoImage(imagen_boton_actualizar)
        boton_actualizar = tk.Button(self.contenedor_botones, image=imagen_boton_actualizar, command=lambda:[self.actualizar_tabla_inventario()])
        boton_actualizar.image = imagen_boton_actualizar  
        boton_actualizar.pack(side="left", padx=5)


        imagen_boton_editar = Image.open("editar.png")  
        imagen_boton_editar = imagen_boton_editar.resize((20, 20))  # Ajusta el tamaño de la imagen según sea necesario
        imagen_boton_editar = ImageTk.PhotoImage(imagen_boton_editar)
        boton_editar = tk.Button(self.contenedor_botones, image=imagen_boton_editar, command=self.editar_datos)
        boton_editar.image = imagen_boton_editar
        boton_editar.pack(side="left", padx=5)


        imagen_boton_borrar = Image.open("borrar.png")  
        imagen_boton_borrar = imagen_boton_borrar.resize((20, 20))  # Ajusta el tamaño de la imagen según sea necesario
        imagen_boton_borrar = ImageTk.PhotoImage(imagen_boton_borrar)
        boton_borrar = tk.Button(self.contenedor_botones, image=imagen_boton_borrar, command=lambda:[self.borrar_datos(), self.actualizar_tabla_inventario()])
        boton_borrar.image = imagen_boton_borrar
        boton_borrar.pack(side="left", padx=5)


        boton_guardar = tk.Button(self.contenedor_botones, text="Guardar", command=lambda:[self.guardar_datos(),self.actualizar_tabla_inventario()])
        boton_guardar.pack(side="right", padx=20)        
        

        # Crear un contenedor Frame de Entries
        frame_Entries = tk.Frame(self.ventana_tabla)
        frame_Entries.pack(side="bottom")

        # Crear un contenedor Frame de Labels
        frame_labels = tk.Frame(self.ventana_tabla)
        frame_labels.pack(side="bottom")

        # Crear las etiquetas y entradas para cada campo
        label_modelo = tk.Label(frame_labels, text="Modelo:")
        label_modelo.pack(side="left", padx=30)
        self.entry_modelo = tk.Entry(frame_Entries)
        self.entry_modelo.pack(side="left", padx=10)

        label_serial = tk.Label(frame_labels, text="Serial:")
        label_serial.pack(side="left", padx=60)
        self.entry_serial = tk.Entry(frame_Entries)
        self.entry_serial.pack(side="left", padx=10)

        label_precio = tk.Label(frame_labels, text="Precio:")
        label_precio.pack(side="left", padx=50)
        self.entry_precio = tk.Entry(frame_Entries)
        self.entry_precio.pack(side="left", padx=10)

        label_proveedor = tk.Label(frame_labels, text="Proveedor:")
        label_proveedor.pack(side="left", padx=30)
        self.entry_proveedor = tk.Entry(frame_Entries)
        self.entry_proveedor.pack(side="left", padx=10)

        label_caracteristicas = tk.Label(frame_labels, text="Características:")
        label_caracteristicas.pack(side="left", padx=50)
        self.entry_caracteristicas = tk.Entry(frame_Entries)
        self.entry_caracteristicas.pack(side="left", padx=10)


        self.tabla = tk.ttk.Treeview(self.ventana_tabla, columns=(0, 1, 2, 3, 4, 5, 6, 7), show="headings")
        self.tabla.pack()

        self.tabla.heading(0, text="Check")
        self.tabla.heading(1, text="ID")
        self.tabla.heading(2, text="modelo")
        self.tabla.heading(3, text="precio")
        self.tabla.heading(4, text="serial")
        self.tabla.heading(5, text="fecha_ingreso")
        self.tabla.heading(6, text="provedor")
        self.tabla.heading(7, text="caracteristicas")

        #configura el ancho de una casilla/columna
        self.tabla.column(0, width=50)
        self.tabla.column(1, width=50)

        mycursor.execute("SELECT * FROM productos")
        datos = mycursor.fetchall()

        for dato in datos:
            self.tabla.insert("", "end", values=(" ",) + dato)


        def toggle_check(event):
            # Obtener el índice de la columna del check
            col_index = self.tabla["columns"].index("0")

            # Obtener el índice de la fila seleccionada
            self.selected_item = self.tabla.focus()
            selected_index = self.tabla.index(self.selected_item)

            # Obtener el estado actual de la casilla de verificación
            current_state = self.tabla.set(self.selected_item, col_index)

            # Cambiar el estado de la casilla de verificación
            new_state = not bool(current_state)
            self.tabla.set(self.selected_item, col_index, "✓" if new_state else "")

            if new_state:
                self.id_seleccionados.append(self.tabla.item(self.selected_item)['values'][1])
            else:
                self.id_seleccionados.remove(self.tabla.item(self.selected_item)['values'][1]) 

        self.tabla.bind("<Button-1>", toggle_check)


        def ajustar_ventana(event):
            self.tabla.update()
            self.ventana_tabla.geometry(f"{self.tabla.winfo_width()+20}x600")

            # Configura el tamaño de la ventana
            self.ventana_tabla.bind("<Configure>", ajustar_ventana)
            self.ventana_tabla.geometry(f"{self.tabla.winfo_width()+20}x600")

            # Ajusta la ventana al ancho de la tabla
            self.ventana_tabla.update()

    def actualizar_tabla_inventario(self):
        # Limpiar la tabla
        mydb.commit()
        self.tabla.delete(*self.tabla.get_children())

        mycursor.execute("SELECT * FROM productos")
        datos = mycursor.fetchall()
        for dato in datos:
            self.tabla.insert("", "end", values=(" ",) + dato)

    def guardar_datos(self):
        # Obtener los valores de las entradas
        modelo = self.entry_modelo.get()
        serial = self.entry_serial.get()
        precio = self.entry_precio.get()
        proveedor = self.entry_proveedor.get()
        caracteristicas = self.entry_caracteristicas.get()


        # Insertar los datos en la tabla
        query = "INSERT INTO productos(modelo, serial, precio, proveedor, caracteristicas) VALUES (%s, %s, %s, %s, %s)"
        values = (modelo, serial, precio, proveedor, caracteristicas)
        mycursor.execute(query, values)

        # Confirmar los cambios
        mydb.commit()
        

        # Limpiar las entradas después de guardar los datos
        self.entry_modelo.delete(0, tk.END)
        self.entry_serial.delete(0, tk.END)
        self.entry_precio.delete(0, tk.END)
        self.entry_proveedor.delete(0, tk.END)
        self.entry_caracteristicas.delete(0, tk.END)

    def borrar_datos(self):
        for id in self.id_seleccionados:
            query = "DELETE FROM productos WHERE id_product = %s"
            values = (id,)
            mycursor.execute(query, values)
        self.id_seleccionados.clear()

    def editar_datos(self):
        selected_item = self.tabla.focus()
        if selected_item:
            # Obtener los valores de la fila seleccionada
            values = self.tabla.item(selected_item)['values']
            
            # Mostrar una ventana de edición de datos
            ventana_edicion = tk.Tk()
            ventana_edicion.title("Editar datos")
            
            # Crear etiquetas y entradas para cada campo
            label_modelo = tk.Label(ventana_edicion, text="Modelo:")
            label_modelo.grid(row=0, column=0)
            entry_modelo = tk.Entry(ventana_edicion)
            entry_modelo.grid(row=0, column=1)
            entry_modelo.insert(tk.END, values[2])  # Rellenar la entrada con el valor existente
            
            label_serial = tk.Label(ventana_edicion, text="Serial:")
            label_serial.grid(row=1, column=0)
            entry_serial = tk.Entry(ventana_edicion)
            entry_serial.grid(row=1, column=1)
            entry_serial.insert(tk.END, values[4])
            
            label_precio = tk.Label(ventana_edicion, text="Precio:")
            label_precio.grid(row=2, column=0)
            entry_precio = tk.Entry(ventana_edicion)
            entry_precio.grid(row=2, column=1)
            entry_precio.insert(tk.END, values[3])
            
            label_proveedor = tk.Label(ventana_edicion, text="Proveedor:")
            label_proveedor.grid(row=3, column=0)
            entry_proveedor = tk.Entry(ventana_edicion)
            entry_proveedor.grid(row=3, column=1)
            entry_proveedor.insert(tk.END, values[6])
            
            label_caracteristicas = tk.Label(ventana_edicion, text="Características:")
            label_caracteristicas.grid(row=4, column=0)
            entry_caracteristicas = tk.Entry(ventana_edicion)
            entry_caracteristicas.grid(row=4, column=1)
            entry_caracteristicas.insert(tk.END, values[7])

            def guardar_edicion(values):
                # Obtener los nuevos valores de las entradas
                nuevo_modelo = entry_modelo.get()
                nuevo_serial = entry_serial.get()
                nuevo_precio = entry_precio.get()
                nuevo_proveedor = entry_proveedor.get()
                nuevo_caracteristicas = entry_caracteristicas.get()
                
                # Actualizar los valores en la base de datos
                query = "UPDATE productos SET modelo = %s, serial = %s, precio = %s, proveedor = %s, caracteristicas = %s WHERE id_product = %s"
                update_values = (nuevo_modelo, nuevo_serial, nuevo_precio, nuevo_proveedor, nuevo_caracteristicas, values[1])
                mycursor.execute(query, update_values)
                mydb.commit()
                
                # Cerrar la ventana de edición
                ventana_edicion.destroy()
            boton_guardar_e = tk.Button(ventana_edicion, text="Guardar", command=lambda: guardar_edicion(values))
            boton_guardar_e.grid(row=5, column=0, columnspan=2)
        print()


try:
    # Crea un objeto de la clase ConectarConMySQL para conectarnos con la base de datos
    connect_BD = ConectarConMySQL()
    connect_BD.conectarMySQL()
except:
    print('Error al establecer conexion con la base de datos')


# Crear una instancia de la ventana principal
ventana = CrearVentanasGraficas()
ventana.create_login_window()