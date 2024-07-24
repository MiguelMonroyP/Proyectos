
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.dropdown import DropDown # esto se agrego
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.spinner import Spinner
from kivy.properties import StringProperty
from kivy.logger import Logger
from kivy.config import Config
from kivy.uix.button import Button


import logging
from functools import partial
from sqlqueries import QueriesSQLite
from datetime import datetime, timedelta
import csv
from pathlib import Path
import os
import sys

# Configura el nivel de registro de Kivy
Logger.setLevel("INFO")
Config.set('kivy', 'log_level', 'info')

# Configura el nivel de registro de logging
logging.basicConfig(level=logging.ERROR)

# Ajusta el límite de recursión
sys.setrecursionlimit(100000)

Builder.load_file('Groups/Groups.kv')

class SelectableRecycleBoxLayoutgroup(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    touch_deselect_last = BooleanProperty(True) 

class SelectableBoxLayoutDetalles(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
    	self.index = index
    	self.ids['_hashtag'].text = str(1+index)
    	self.ids['_Cedula'].text = str(data.get('Cedula', ''))
    	self.ids['_Nombre'].text = data.get('Nombre', '')
    	self.ids['_Banco'].text = data.get('Banco', '').capitalize()
    	self.ids['_Numero'].text = str(data.get('Numero', ''))
    	self.ids['_Grupo'].text = str(data.get('grupo', ''))
    	total_text = str(data.get('total', ''))  # Convertir a cadena
    	self.ids['_total'].text = total_text
    	if total_text:
            interes = float(total_text) * 1.7
            self.ids['_interes'].text = str(interes)
    	else:
            self.ids['_interes'].text = ''   
    	return super(SelectableBoxLayoutDetalles, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayoutDetalles, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
        	rv.data[index]['seleccionado']=True
        else:
        	rv.data[index]['seleccionado']=False

class GroupsRV(RecycleView):
    def __init__(self, **kwargs):
        super(GroupsRV, self).__init__(**kwargs)
        self.data=[]

    def agregar_datos(self,datos):
        if datos is not None:
            for dato in datos:
                dato['seleccionado']=False
                self.data.append(dato)
            self.refresh_from_data()

    def dato_seleccionado(self):
        indice=-1
        for i in range(len(self.data)):
            if self.data[i]['seleccionado']:
                indice=i
                break
        return indice
	
class ConfirmacionPopups(Popup):
	def __init__(self, _eliminar_callback, **kwargs):
		super(ConfirmacionPopups, self).__init__(**kwargs)
		self.eliminar_estudiante=_eliminar_callback	

		def abrir(self, eliminar, grupo=None):
			self.open()

class AgregarEstudiantePopup(Popup):
	def __init__(self, _agregar_callback, **kwargs):
		super(AgregarEstudiantePopup, self).__init__(**kwargs)
		self.agregar_estudiante=_agregar_callback
				
		
	def abrir(self, agregar, valor_spinner, estudiante=None):
		self.valor_spinner = valor_spinner
		
		if agregar:
			self.ids.usuario_info_1.text='Agregar Estudiante nuevo'
			self.ids.estudiante_cedula.disabled=False
		else:
			self.ids.usuario_info_1.text='Modificar Usuario'
			self.ids.estudiante_cedula.text=estudiante['Cedula']
			self.ids.estudiante_cedula.disabled=True
			self.ids.estudiante_nombre.text=estudiante['Nombre']
			self.ids.estudiante_nombre.disabled=True
			self.ids.estudiante_banco.text=estudiante['Banco']
			self.ids.estudiante_numero.text=estudiante['Numero de cuenta']
			self.ids.estudiante_total.text=estudiante['total']
			self.ids.estudiante_grupo.text = valor_spinner
			
		self.open()

	def verificar(self, estudiante_cedula, estudiante_nombre, estudiante_banco, estudiante_numero, estudiante_grupo, estudiante_total):
		alert1 = 'Falta: '
		alert2=''
		validado = {}

		if not estudiante_cedula:
			alert1+='Cedula. '
			validado['Cedula']=False
		else:
			try:
				numeric=int(estudiante_cedula)
				validado['Cedula']=estudiante_cedula
			except:
				alert2+='Numero no válida. '
				validado['Cedula']=False
				
		
		if not estudiante_nombre:
			alert1+='Nombre del Estudiante. '
			validado['Nombre']=False
		else:
			validado['Nombre']=estudiante_nombre

		if not estudiante_banco:
			alert1+='Banco de la cuenta. '
			validado['Banco']=False
		else:
			validado['Banco']=estudiante_banco

		if not estudiante_numero:
			alert1+='Numero. '
			validado['Numero']=False
		else:
			try:
				numeric=int(estudiante_numero)
				validado['Numero']=estudiante_numero
			except:
				alert2+='Numero no válida. '
				validado['Numero']=False
		
		if  self.valor_spinner == "Selecciona un Grupo":
			# print('el valor de spinner:', self.valor_spinner)
			alert1+='Grupo. '
			validado['grupo']=False
		
		else:
			validado['grupo']=self.valor_spinner
		
		if estudiante_total == '':
			validado['total']= estudiante_total
		
		
		valores = list(validado.values())

		if False in valores:
			self.ids.no_valid_notif.text=alert1+alert2
		else:
			self.ids.no_valid_notif.text=''
			self.agregar_estudiante(True,validado)
			self.dismiss()
			
class GroupsWindow(BoxLayout):
      
	def __init__(self,cargar_datosiniciales_callback, **kwargs):
		super().__init__(**kwargs)
		self.cargar_estudiantes()
		self.valor_seleccionado = None
		self.cargar_datosiniciales=cargar_datosiniciales_callback
		Clock.schedule_once(self.cargar_estudiantes, 1)
		Clock.schedule_once(partial(self.spinner_callback, text='Selecciona un Grupo'), 1)
		
		
	def cargar_estudiantes(self,  *args):
		_estudiantes = []
		_showest = None
		spinner_value = self.ids.Grupo_label.text
		valor_busqueda= spinner_value
		# print(valor_busqueda)
		connection=QueriesSQLite.create_connection("BankDB.sqlite")
		estudiante_sql = QueriesSQLite.execute_read_query(connection, "SELECT * from Estudiantes")
		if estudiante_sql:  # agregado!!!
			_showest = []  # Inicializar _showest fuera del bucle
			for estudiante in estudiante_sql:
				_estudiantes.append({'Cedula': estudiante[0], 'Nombre': estudiante[1], 'Banco': estudiante[2], 'Numero': estudiante[3], 'grupo': estudiante[4], 'total': estudiante[5]})
				# print('estoy aca',_estudiantes)
			for alumno in _estudiantes:						
					if alumno['grupo'] == valor_busqueda:	
							# print('llegue', valor_busqueda)
							_showest.append(alumno)
			_showest = sorted(_showest, key=lambda x: x['Nombre'])
		# print(_showest)
		 # Limpiar los datos existentes en rv antes de agregar nuevos datos
		self.ids.rv.data = []
		self.ids.rv.agregar_datos(_showest)

				
	def cargar_gruposspinner(self,  *args):
		opciones = []
		self._grupos = []  # Hacer _grupos una variable de instancia
		connection = QueriesSQLite.create_connection("BankDB.sqlite")
		inventario_sql = QueriesSQLite.execute_read_query(connection, "SELECT * from Grupos")
		# total_sql = QueriesSQLite.execute_read_query(connection, f"SELECT * from Estudiantes where Grupo={text=self.spinner_callback}")
		if inventario_sql:  # agregado!!!
			for grupo in inventario_sql:
				self._grupos.append({'grupo': grupo[1], 'codigo': grupo[0], 'estudiantes': grupo[2], 'fecha': grupo[3]})
				opciones.append(grupo[1])  # Añade solo el nombre del grupo
		spinner = self.ids.Grupo_label
		spinner.values = opciones  # Establece las opciones del Spinner
		spinner.bind(text=self.spinner_callback)
		

	def spinner_callback( self, dt, text='default_value'):
		self.cargar_gruposspinner() # Después de guardar los datos de un nuevo grupo en la base de datos
		self.valor_seleccionado = text 
		valor_spinner = text
		# print(valor_spinner)		
		for grupo in self._grupos:
			if grupo['grupo'] == text:
				codigo = grupo['codigo']
				self.ids.Codigo_grupo.text ='Grupo N°: '+codigo
				break  # Salir del bucle una vez que se haya encontrado el código
		Grupo_spinner="'"+str(valor_spinner)+"'"
		connection=QueriesSQLite.create_connection("BankDB.sqlite")
		total_sql = QueriesSQLite.execute_read_query(connection, f"SELECT * from Estudiantes where Grupo={Grupo_spinner}")
		self.total = 0
		if total_sql:  # agregado!!!
			for estudiante in total_sql:
				try:
					self.total += int(str(estudiante[5]))
				except ValueError:
    # Manejar el caso donde el valor no se puede convertir a entero.
    # Por ejemplo, podrías asignar un valor por defecto, como 0:
					self.total += 0
		interes = self.total*1.7 
			# print(self.buscartabla)
		self.ids.total.text = "$" + str(self.total)
		self.ids.interes.text = "$" + str(interes)

			
	def agregar_estudiante(self, agregar=False, validado=None):
		spinner_value = self.ids.Grupo_label.text 
		if agregar:
			estudiante_tuple=tuple(validado.values())
			connection=QueriesSQLite.create_connection("BankDB.sqlite")
			crear_grupo = """
			INSERT INTO
				Estudiantes (Cedula, Nombre, Banco, Numero, Grupo, total)
			VALUES
				(?,?,?,?,?,?);
			"""
			QueriesSQLite.execute_query(connection, crear_grupo, estudiante_tuple)
			self.ids.rv.data.append(validado)
			self.ids.rv.refresh_from_data()
		else:
			popup=AgregarEstudiantePopup(self.agregar_estudiante)
			popup.abrir(True, spinner_value)
			# print(spinner_value)

	def confirmar_eliminar(self):
			popup = ConfirmacionPopups(self.eliminar_estudiante)
			popup.open()

	def eliminar_estudiante(self, eliminar=False):
		indice = self.ids.rv.dato_seleccionado()
		if indice>=0:
			estudiante_tuple=(self.ids.rv.data[indice]['Cedula'],)
			borrartabla = "'"+str(self.ids.rv.data[indice]['Cedula'])+"'"
			connection=QueriesSQLite.create_connection("BankDB.sqlite")
			borrar = """DELETE from Estudiantes where Cedula = ?"""
			QueriesSQLite.execute_query(connection, borrar, estudiante_tuple)
			QueriesSQLite.execute_read_query(connection, f""" DROP TABLE IF EXISTS {borrartabla}""")
			menos_precio = int(self.ids.rv.data[indice]['total'])
			self.total -= menos_precio
			self.ids.rv.data.pop(indice)
			interes = self.total*0.7 + self.total
			self.ids.total.text = "$" + str(self.total)
			self.ids.interes.text = "$" + str(interes)
			self.ids.rv.refresh_from_data()

			
	def volver_inicio(self):
		self.parent.parent.current='scrn_home'
		self.ids.Grupo_label.text='Selecciona un Grupo'
		self.ids.Codigo_grupo.text ='Grupo N°: '
		

	def detalle_estudiantes(self):
		indice = self.ids.rv.dato_seleccionado()
		if indice>=0:
			_estudiante=self.ids.rv.data[indice]
			estudiante = {}
			estudiante['Cedula'] = _estudiante['Cedula']
			estudiante['Nombre'] = _estudiante['Nombre']
			estudiante['Banco'] = _estudiante['Banco']
			estudiante['Numero'] = _estudiante['Numero']
			estudiante['grupo'] = _estudiante['grupo']
			Tabla_tuple = "'"+str(estudiante['Cedula'])+"'"
			connection = QueriesSQLite.create_connection("BankDB.sqlite")
			crear_studentview = f"""
           		CREATE TABLE IF NOT EXISTS {Tabla_tuple}(                
                Valor REAL NOT NULL,
				Fecha DATE PRIMARY KEY
            );
        	"""
			QueriesSQLite.execute_query(connection, crear_studentview, tuple())
			# print(estudiante, Tabla_tuple)
			self.cargar_datosiniciales(estudiante)
			self.ids.Grupo_label.text='Selecciona un Grupo'
			self.ids.Codigo_grupo.text ='Grupo N°: '
			self.parent.parent.current='scrn_student'



class GroupsApp(App):
	def build(self):
		return GroupsWindow()

if __name__=="__main__":
    GroupsApp().run() 