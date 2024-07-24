from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.logger import Logger
from kivy.config import Config
import logging
from sqlqueries import QueriesSQLite
from Signin.Signin import SigninWindow
from Groups.Groups import GroupsWindow
from Home.Home import HomeWindow
from Student.Student import StudentWindow
import os, sys

#from kivy.resources import resource_add_path

# Configura el nivel de registro de Kivy
Logger.setLevel("INFO")
Config.set('kivy', 'log_level', 'info')

# Configura el nivel de registro de logging
logging.basicConfig(level=logging.ERROR)

# Ajusta el límite de recursión
sys.setrecursionlimit(100000)

class MainWindow(BoxLayout):
	def __init__(self, **kwargs):
		super().__init__(*kwargs)
		self.student_widget=StudentWindow()
		self.groups_widget=GroupsWindow(self.student_widget.cargar_datosiniciales)
		self.home_widget=HomeWindow(self.groups_widget.cargar_gruposspinner)
		self.signin_widget=SigninWindow(self.home_widget.poner_usuario)
		
		self.ids.scrn_home.add_widget(self.home_widget)
		self.ids.scrn_signin.add_widget(self.signin_widget)
		self.ids.scrn_groups.add_widget(self.groups_widget)
		self.ids.scrn_student.add_widget(self.student_widget)
	
	#def resource_path(relative_path):
		#try:
			#base_path=sys.MEIPASS
		#except Exception:
			#base_path = os.path.abspath('.')
		#return os.path.join(base_path, relative_path)
		

class MainApp(App):
	def build(self):
		return MainWindow()
	

if __name__=="__main__":
	#if hasattr(sys, '_MEIPASS'):
		#resource_add_path(os.path.join(sys._MEIPASS))
	MainApp().run()