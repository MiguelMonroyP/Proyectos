from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.dropdown import DropDown # this was added
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.config import Config
from kivy.uix.button import Button


import logging
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
Builder.load_file ('Home/Home.kv')



class SelectableRecycleBoxLayouthome(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    touch_deselect_last = BooleanProperty(True)


class SelectableBoxLayouthome(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
    	self.index = index
    	self.ids['_hashtag'].text = str(1+index)
    	self.ids['_codigo'].text = data.get('codigo', '')
    	self.ids['_grupo'].text = data.get('grupo', '').capitalize()
    	self.ids['_numero de estudiantes'].text = str(data.get('estudiantes', ''))
    	self.ids['_fecha de ingreso'].text = str(data.get('fecha', ''))
    	return super(SelectableBoxLayouthome, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayouthome, self).on_touch_down(touch):
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

class RV(RecycleView):	
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = []

    def agregar_datos(self,datos):
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
	
class ConfirmacionPopup(Popup):
	def __init__(self, _eliminar_callback, **kwargs):
		super(ConfirmacionPopup, self).__init__(**kwargs)
		self.eliminar_grupo=_eliminar_callback	

		def abrir(self, eliminar, grupo=None):
			self.open()


class AgregargrupoPopup(Popup):
	def __init__(self, _agregar_callback, **kwargs):
		super(AgregargrupoPopup, self).__init__(**kwargs)
		self.agregar_grupo=_agregar_callback
	
	def abrir(self, agregar, grupo=None):
		if agregar:
			self.ids.usuario_info_1.text='Agregar Grupo nuevo'
			self.ids.grupo_username.disabled=False
		else:
			self.ids.usuario_info_1.text='Modificar Usuario'
			self.ids.grupo_username.text=grupo['grupo']
			self.ids.grupo_username.disabled=True
			self.ids.grupo_codigo.text=grupo['codigo']
			self.ids.grupo_numero.text=grupo['estudiantes']
			self.ids.grupo_fecha.text=grupo['fecha']
		self.open()

	def verificar(self, grupo_username, grupo_codigo, grupo_numero, grupo_fecha):
		alert1 = 'Falta: '
		alert2=''
		validado_grupo = {}

		if not grupo_codigo:
			alert1+='Codigo. '
			validado_grupo['codigo']=False
		else:
			validado_grupo['codigo']=grupo_codigo.lower()

		if not grupo_username:
			alert1+='Nombre del Grupo. '
			validado_grupo['grupo']=False
		else:
			validado_grupo['grupo']=grupo_username

		if not grupo_numero:
			alert1+='Numero de estudiantes. '
			validado_grupo['estudiantes']=False
		else:
			try:
				numeric=int(grupo_numero)
				validado_grupo['estudiantes']=grupo_numero
			except:
				alert2+='Cantidad no válida. '
				validado_grupo['estudiantes']=False
		if not grupo_fecha:
			alert1+='Fecha de ingreso DD/MM/AA. '
			validado_grupo['fecha'] = False
		else:
			try:
				date = datetime.strptime(grupo_fecha, '%d/%m/%y')
				validado_grupo['fecha']=grupo_fecha
			except:
				alert2+='Fecha no válida recuerda el formato  DD/MM/AA. '
				validado_grupo['fecha'] = False
	       	
		
		valores = list(validado_grupo.values())

		if False in valores:
			self.ids.no_valid_notif.text=alert1+alert2
		else:
			self.ids.no_valid_notif.text=''
			self.agregar_grupo(True,validado_grupo)
			self.dismiss()

class HomeWindow(BoxLayout,):
	
	def __init__(self, cargar_gruposspinner_callback, **kwargs,):
		super().__init__(**kwargs)
		self.cargar_gruposspinner=cargar_gruposspinner_callback
		self.ahora=datetime.now()
		self.total = '0.00'
		self.ids.fecha.text=self.ahora.strftime("%d/%m/%y")
		Clock.schedule_interval(self.actualizar_hora, 1)
		Clock.schedule_once(self.cargar_grupos, 1)
		
	def cargar_grupos(self, *args):	
		_grupos=[]
		_showgir = None
		connection=QueriesSQLite.create_connection("BankDB.sqlite")
		inventario_sql=QueriesSQLite.execute_read_query(connection, "SELECT * from Grupos")
		if inventario_sql: # agregado!!!
			for grupo in inventario_sql:
				_grupos.append({'grupo': grupo[1], 'codigo': grupo[0], 'estudiantes': grupo[2], 'fecha': grupo[3]})
		connection=QueriesSQLite.create_connection("BankDB.sqlite")
		total_sql = QueriesSQLite.execute_read_query(connection, "SELECT * from Estudiantes")
		self.total = 0
		if total_sql:  # agregado!!!
			for estudiante in total_sql:
				try:
					self.total += int(str(estudiante[5]))
				except ValueError:
    # Manejar el caso donde el valor no se puede convertir a entero.
    # Por ejemplo, podrías asignar un valor por defecto, como 0:
					self.total += 0
			#for estudiante in total_sql:
				# self.total += int(str(estudiante[5]))
				# print('estoy aca',str(self.total))
		self.ids.rvs.data = []
		interes = self.total*1.7 
			# print(self.buscartabla)
		self.ids.total.text = "$" + str(self.total)
		self.ids.interes.text = "$" + str(interes)
		self.ids.rvs.agregar_datos(_grupos)
		
	def actualizar_BD(self, *args):
		self.cargar_grupos()
		# print("hola")

	def agregar_grupo(self, agregar=False, validado_grupo=None):
		if agregar:
			usuario_tuple=tuple(validado_grupo.values())
			connection=QueriesSQLite.create_connection("BankDB.sqlite")
			crear_grupo = """
			INSERT INTO
				Grupos (codigo, nombre, fecha, Numero)
			VALUES
				(?,?,?,?);
			"""
			QueriesSQLite.execute_query(connection, crear_grupo, usuario_tuple)
			self.ids.rvs.data.append(validado_grupo)
			self.ids.rvs.refresh_from_data()
		else:
			popup=AgregargrupoPopup(self.agregar_grupo)
			popup.abrir(True)

	def confirmar_eliminar(self):
			popup = ConfirmacionPopup(self.eliminar_grupo)
			popup.open()

	def eliminar_grupo(self, eliminar=False):
			indice = self.ids.rvs.dato_seleccionado()
			if indice>=0:
				mostrartabla="'"+str(self.ids.rvs.data[indice]['grupo'])+"'"
				# print(mostrartabla)
				connection=QueriesSQLite.create_connection("BankDB.sqlite")			
				inventario_sql=QueriesSQLite.execute_read_query(connection, f""" SELECT * from Estudiantes WHERE Grupo= {mostrartabla}""")
				# print(inventario_sql)
				if inventario_sql: # agregado!!!
						for cedula in inventario_sql:	
							borrartabla="'"+str(cedula[0])+"'"
							# print(borrartabla)
							QueriesSQLite.execute_read_query(connection, f""" DROP TABLE IF EXISTS {borrartabla}""")
				grupo_tuple=(self.ids.rvs.data[indice]['grupo'],)
				connection=QueriesSQLite.create_connection("BankDB.sqlite")
				borrar = """DELETE from Estudiantes where Grupo = ?"""
				QueriesSQLite.execute_query(connection, borrar, grupo_tuple)
				usuario_tuple=(self.ids.rvs.data[indice]['codigo'],)
				connection=QueriesSQLite.create_connection("BankDB.sqlite")
				borrar = """DELETE from Grupos where codigo = ?"""
				QueriesSQLite.execute_query(connection, borrar, usuario_tuple)
				self.ids.rvs.data.pop(indice)
				self.ids.rvs.refresh_from_data()
				
				
	def detalle_grupo(self):
		self.cargar_gruposspinner()
		self.parent.parent.current='scrn_groups'

	
	def crear_csv(self):		    
    # Verifica si hay datos en la tabla
		if self.ids.rvs.data:
			path = Path(__file__).absolute().parent
			buscartabla="Base de Datos"

        # Nombre completo del archivo CSV
			csv_nombre = path / f'{buscartabla}_csv' / f'{buscartabla}.csv'

        # Verifica si el directorio existe, si no, créalo
			csv_nombre.parent.mkdir(parents=True, exist_ok=True)

        # Lista para almacenar los datos
			_estudiantes = []
			self.total = 0
        
        # Obtiene los datos de la tabla
			connection=QueriesSQLite.create_connection("BankDB.sqlite")
			estudiante_sql = QueriesSQLite.execute_read_query(connection, "SELECT * from Estudiantes")
			if estudiante_sql:  # agregado!!!
				for estudiante in estudiante_sql:
					_estudiantes.append({'Cedula': estudiante[0], 'Nombre': estudiante[1], 'Banco': estudiante[2], 'Numero': estudiante[3], 'grupo': estudiante[4], 'total': estudiante[5]})
				

        # Encabezados del archivo CSV
			fieldnames = ['Cedula', 'Nombre', 'Banco', 'Numero', 'grupo', 'total']

        # Escribe los datos en el archivo CSV
			with open(csv_nombre, 'w', encoding='UTF8', newline='') as f:
				writer = csv.DictWriter(f, fieldnames=fieldnames)
				writer.writeheader()
				writer.writerows(_estudiantes)

			self.ids.notificacion_exito.text = 'CSV creado y guardado en ' + str(csv_nombre)
		else:
			self.ids.notificacion_exito.text = 'No hay datos que guardar'	

	def poner_usuario(self, usuario):
		self.ids.bienvenido_label.text='Bienvenido '+usuario['nombre']
		self.ids.bienvenido_Usuario.text='Usuario '+usuario['nombre']
			
	def actualizar_hora(self, *args):
		self.ahora=self.ahora+timedelta(seconds=1)
		self.ids.hora.text=self.ahora.strftime("%H:%M:%S")

	
class HomeApp(App):
	def build(self):
		return HomeWindow()

if __name__=='__main__':
	HomeApp().run()