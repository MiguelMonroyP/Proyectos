from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
import random

from sqlqueries import QueriesSQLite

Builder.load_file('Signin/Signin.kv')


class SigninWindow(BoxLayout):
	def __init__(self, poner_usuario_callback, **kwargs):
		super().__init__(*kwargs)
		self.poner_usuario=poner_usuario_callback
		# Lista de frases
		self.phrases = [
            "Tú eres suficiente tal como eres. Tu valía no depende de tus logros, sino de quién eres en tu esencia.",
            "Cada paso que das, por pequeño que parezca, te acerca un poco más a tus metas. Cada esfuerzo cuenta y te lleva más cerca del éxito.",
            "Recuerda que tus sueños son válidos y mereces perseguirlos con todo tu corazón. No dejes que el miedo o las dudas te detengan.",
            "Eres más fuerte de lo que crees y más capaz de lo que imaginas. Confía en ti mismo y en tu capacidad para superar cualquier desafío que se te presente.",
            "El progreso no siempre es lineal, pero cada paso hacia adelante, incluso los pequeños retrocesos, son parte del proceso de crecimiento y aprendizaje.",
            "Nunca subestimes el poder de tu luz interior. Tu presencia en el mundo hace una diferencia, y tus acciones tienen un impacto más grande de lo que puedas imaginar.",
            "Recuerda siempre que eres digno de amor y respeto, tanto de los demás como de ti mismo. Cultiva el amor propio y reconoce tu propio valor."
        ]
		random_phrase = random.choice(self.phrases) 
		self.ids.bienvenido_label.text = f'Bienvenido\n\n{random_phrase}'

	def verificar_usuario(self, username, password):
		connection = QueriesSQLite.create_connection("BankDB.sqlite")
		users=QueriesSQLite.execute_read_query(connection, "SELECT * from usuarios")
		if users:
			if username=='' or password=='':
				self.ids.signin_notificacion.text='Falta nombre de usuario y/o contraseña'
			else:
				usuario={}
				for user in users:
					if user[0]==username:
						usuario['nombre']=user[1]
						usuario['username']=user[0]
						usuario['password']=user[2]
						usuario['tipo']=user[3]
						break
				if usuario:
					if usuario['password']==password:
						self.ids.username.text=''
						self.ids.password.text=''
						self.ids.signin_notificacion.text=''
						if usuario['tipo']=='trabajador':
							self.parent.parent.current='scrn_home'
						else:
							self.parent.parent.current='scrn_home'
						self.poner_usuario(usuario)
					else:
						self.ids.signin_notificacion.text='Usuario o contraseña incorrecta'
				else:
					self.ids.signin_notificacion.text='Usuario o contraseña incorrecta'
		



class SigninApp(App):
	def build(self):
		return SigninWindow()

if __name__=="__main__":
	SigninApp().run()