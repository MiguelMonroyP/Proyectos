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
Builder.load_file('Student/Student.kv')

class SelectableRecycleBoxLayoutstudent(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    touch_deselect_last = BooleanProperty(True) 

class SelectableBoxLayoutGiros(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rve, index, data):
    	self.index = index
    	self.ids['_hashtag'].text = str(1+index)
    	self.ids['_Valor'].text ="$"+str(data.get('Valor', ''))
    	self.ids['_Fecha'].text = str(data.get('Fecha', ''))
          
    	return super(SelectableBoxLayoutGiros, self).refresh_view_attrs(
            rve, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayoutGiros, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rve, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
        	rve.data[index]['seleccionado']=True
        else:
        	rve.data[index]['seleccionado']=False

class EstudentRV(RecycleView):
    def __init__(self, **kwargs):
        super(EstudentRV, self).__init__(**kwargs)
        self.data=[]

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

class AgregarGiroPopup(Popup):
	def __init__(self, _agregar_callback, **kwargs):
		super(AgregarGiroPopup, self).__init__(**kwargs)
		self.agregar_giro=_agregar_callback
				
		
	def abrir(self, agregar, estudiante=None):
				
		if agregar:
			self.ids.usuario_info_1.text='Agregar Giro nuevo'
			self.ids.estudiante_Fecha.disabled=False
		else:
			self.ids.usuario_info_1.text='Modificar Giro'
			self.ids.estudiante_Valor.text=str(estudiante['Valor'])
			self.ids.estudiante_Fecha.disabled=True
			self.ids.estudiante_Fecha.text=estudiante['Fecha']
					
		self.open()
	
	# def actualizar_label_spinner(self, text):
	# 	self.spinner_callback()
	# 	self.ids.estudiante_grupo.text = text

	def verificar(self, estudiante_Fecha, estudiante_Valor):
		alert1 = 'Falta: '
		alert2=''
		validado = {}

		if not estudiante_Valor:
			alert1+='Valor. '
			validado['Valor']=False
		else:
			try:
				numeric=int(estudiante_Valor)
				validado['Valor']=estudiante_Valor
			except:
				alert2+='Numero no válida. '
				validado['Valor']=False
		
		if not estudiante_Fecha:
			alert1+='Fecha DD/MM/AA. '
			validado['Fecha'] = False
		else:
			try:
				date = datetime.strptime(estudiante_Fecha, '%d/%m/%y')
				validado['Fecha']=estudiante_Fecha
			except:
				alert2+='Fecha no válida recuerda el formato  DD/MM/AA. '
				validado['Fecha'] = False
	       	

		valores = list(validado.values())

		if False in valores:
			self.ids.no_valid_notif.text=alert1+alert2
		else:
			self.ids.no_valid_notif.text=''
			self.agregar_giro(True,validado)
			self.dismiss()
			
class StudentWindow(BoxLayout):
      
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.buscartabla = None
		self.total = '0.00'
		Clock.schedule_once(self.cargar_giros, 1)
	
	def cargar_giros(self, *args):
		if self.buscartabla:
			_giro = []
			self.total = 0
			connection = QueriesSQLite.create_connection("BankDB.sqlite")
			giro_sql = QueriesSQLite.execute_read_query(connection, f""" SELECT * from {self.buscartabla}""")
			if giro_sql:
				for giro in giro_sql:					
					_giro.append({'Valor': giro[0], 'Fecha': giro[1]})
					try:
						self.total += int(giro[0])
					except ValueError:
						self.total += 0
					#self.total += int(giro[0])
			self.ids.rve.data = []
			self.ids.rve.agregar_datos(_giro)
			interes = self.total*0.7 + self.total
			# print(self.buscartabla)
			self.ids.total.text = "$" + str(self.total)
			self.ids.interes.text = "$" + str(interes)
				
	def agregar_giro(self, agregar=False, validado=None ):
		buscartabla=self.buscartabla
		if agregar:
			estudiante_tuple=tuple(validado.values())
			connection=QueriesSQLite.create_connection("BankDB.sqlite")

			crear_grupo = f"""
			INSERT INTO
				{buscartabla} (Valor, Fecha)
			VALUES
				(?,?);
			"""
			QueriesSQLite.execute_query(connection, crear_grupo, estudiante_tuple)
			self.ids.rve.data.append(validado)
			self.total += int(validado['Valor'])
			interes = self.total*0.7 + self.total
			self.ids.total.text = "$" + str(self.total)
			self.ids.interes.text = "$" + str(interes)
			self.ids.rve.refresh_from_data()
		else:
			popup=AgregarGiroPopup(self.agregar_giro)
			popup.abrir(True)

	def eliminar_giro(self):
		indice = self.ids.rve.dato_seleccionado()
		
		if indice>=0:
			estudiante_tuple=(self.ids.rve.data[indice]['Fecha'],)
			connection=QueriesSQLite.create_connection("BankDB.sqlite")
			borrar = f"""DELETE from {self.buscartabla} where Fecha = ?"""
			QueriesSQLite.execute_query(connection, borrar, estudiante_tuple)
			menos_precio = int(self.ids.rve.data[indice]['Valor'])
			self.total -= menos_precio
			self.ids.rve.data.pop(indice)
			interes = self.total*0.7 + self.total
			self.ids.total.text = "$" + str(self.total)
			self.ids.interes.text = "$" + str(interes)
			self.ids.rve.refresh_from_data()
			
	def volver_inicio(self):
		
		self.parent.parent.current='scrn_groups'
		if self.ids.total.text:
			connection=QueriesSQLite.create_connection("BankDB.sqlite")
			crear_grupo = f"""
			UPDATE Estudiantes
				SET Total = {self.total}
				WHERE Cedula = {self.buscartabla};
			"""
			QueriesSQLite.execute_query(connection, crear_grupo,  tuple())
	
	def modificar_giro(self, modificar=False, validado=None):		
		indice = self.ids.rve.dato_seleccionado()
		self.total=0		
		if modificar:
			estudiante_tuple = (validado['Valor'], validado['Fecha'])
			connection = QueriesSQLite.create_connection("BankDB.sqlite")

			crear_grupo = f"""
        UPDATE  {self.buscartabla}
        SET Valor=?
        WHERE Fecha=?
        """
			QueriesSQLite.execute_query(connection, crear_grupo, estudiante_tuple)
			self.ids.rve.data[indice]['Valor'] = validado['Valor']
			self.ids.rve.refresh_from_data()
			self.total = sum(int(item['Valor']) for item in self.ids.rve.data)
			interes = self.total*0.7 + self.total
			self.ids.total.text = "$" + str(self.total)
			self.ids.interes.text = "$" + str(interes)
		else:
			if indice >= 0:
				estudiante = self.ids.rve.data[indice]
				popup = AgregarGiroPopup(self.modificar_giro)
				popup.abrir(False, estudiante)

	def cargar_datosiniciales(self,  estudiante):
		# print(estudiante)
		self.ids.Nombre_label.text='Nombre: '+estudiante['Nombre']
		self.ids.Cedula_label.text='Cedula: '+str(estudiante['Cedula'])
		self.ids.Banco_label.text='Banco: '+estudiante['Banco']
		self.ids.Numero_label.text='Numero: '+str(estudiante['Numero'])
		self.buscartabla="'"+str(estudiante['Cedula'])+"'"
		self.cargar_giros()
	
	def crear_csv(self):
		
    
    # Verifica si hay datos en la tabla
		if self.ids.rv.data:
			path = Path(__file__).absolute().parent

        # Nombre completo del archivo CSV
			csv_nombre = path / f'{self.buscartabla}_csv' / f'{self.buscartabla}.csv'

        # Verifica si el directorio existe, si no, créalo
			csv_nombre.parent.mkdir(parents=True, exist_ok=True)

        # Lista para almacenar los datos
			_giro = []
			self.total = 0
        
        # Obtiene los datos de la tabla
			connection = QueriesSQLite.create_connection("BankDB.sqlite")
			giro_sql = QueriesSQLite.execute_read_query(connection, f"SELECT * from {self.buscartabla}")
			if giro_sql:
				for giro in giro_sql:
					_giro.append({'Valor': giro[0], 'Fecha': giro[1]})
					self.total += int(giro[0])

        # Encabezados del archivo CSV
			fieldnames = ['Valor', 'Fecha']

        # Escribe los datos en el archivo CSV
			with open(csv_nombre, 'w', encoding='UTF8', newline='') as f:
				writer = csv.DictWriter(f, fieldnames=fieldnames)
				writer.writeheader()
				writer.writerows(_giro)

			self.ids.notificacion_exito.text = 'CSV creado y guardado en ' + str(csv_nombre)
		else:
			self.ids.notificacion_exito.text = 'No hay datos que guardar'
	


class EstudentApp(App):
	def build(self):
		return StudentWindow()

if __name__=="__main__":
    EstudentApp().run() 