#!/usr/bin/env python
# -*- coding: utf-8 -*-​

# Autor: 		Enrique Andrade González - NeTTinG
# Web:			blog.netting.es
# email:		netting(at)netting(dot)es

# Licencia: 
# Creative commons (cc) - creativecommons.org
# Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

import threading, os, sys
from threading import Thread

#from manejo_interfaz.manejo_interfaz import existe_interfaz, esta_modo_monitor
from manejo_interfaz import existe_interfaz, esta_modo_monitor

from subprocess import Popen, PIPE
from signal import SIGINT, signal

from time import sleep


############################ CONSTANTES ################################
# Listas de banda completa [1 -13 2.4 Ghz]
LISTA_CANALES_24GHZ = [1, 6, 11, 14, 2, 7, 3, 8, 4, 12, 9, 5, 10, 13]
LISTA_CANALES_5GHZ = [36, 38, 40, 42, 44, 46, 52, 56, 58, 60, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 149, 153, 157, 161, 165]
DN = open(os.devnull, 'w')

############################### ERRORES ################################

class SaltoCanal(Thread):
	
	# Tiempo de espera en segundos.
	def __init__(self, interfaz, espera=4, check=False, _24Ghz=True, _5Ghz=False, verbose=True):
		self.verbose = verbose
		# Comprobamos que se pasa al menos una lista de canales.
		self.__lista_canales_valida(_24Ghz, _5Ghz)
		# Iniciamos el hilo.
		Thread.__init__(self)
		# Hilo de tipo 'daemon'. El hilo principal puede terminar sin esperar por los demás.
		Thread.daemon = True
		
		# Inicializamos variables locales.
		self.interfaz = self.__comprobar_interfaz(interfaz)
		# Dividimos entre 10.0 y casteanos a float
		self.__espera = float(espera/10.0)
		self.__pausar=False
		self.canal_actual=0
		self.__terminar = False
		# Very Important Channels
		self.__lista_VIC = []
		self.__espera_VIC = 0.6
		
		self.lista_canales = []
		if (check):
			self.lista_canales = self.comprobar_canales(_24Ghz, _5Ghz)
		else:
			if (_24Ghz): self.lista_canales.extend(LISTA_CANALES_24GHZ)
			if (_5Ghz): self.lista_canales.extend(LISTA_CANALES_5GHZ)
	
	
	# Empezamos comprando la banda 5Ghz por ser más problemática
	def comprobar_canales(self, _24Ghz=True, _5Ghz=False):
		canales_validos = []
		if (_5Ghz):
			canales_validos.extend(self.__comprobar_canales(LISTA_CANALES_5GHZ))
		if (_24Ghz):
			canales_validos.extend(self.__comprobar_canales(LISTA_CANALES_24GHZ))
		return canales_validos
		
	
	# Solo cuando el metodo run este parado.
	def fijar_canal(self, canal):
		if Thread.isAlive(self):
			if self.verbose: print "El hilo esta corriendo. Pare o termine el hilo primero."
			return False
		else:
			return self.__cambiar_canal(canal)
	
	
	# Tiempo en segundos
	def tiempo_canal(self, espera):
		self.__espera = float(espera/10.0)
	
	
	def lista_VIC(self, vic, espera=6):
		self.__lista_VIC = vic
		self.__espera_VIC = float(espera/10.0)


	def fijar_canales(self, canales):
		self.lista_canales=canales
		
	
	def pausar(self):
		if Thread.isAlive(self):
			if not self.__get_pausar():
				self.__pausar=True
				return True
			else: 
				if self.verbose: print "El hilo ya se encuentra parado."
		else:
			if self.verbose: print "El hilo no se ha ejecutado."
		return False
		
		
	def continuar(self):
		if Thread.isAlive(self):
			if self.__get_pausar(): 
				self.__pausar=False
				return True
			else:
				if self.verbose: print "El hilo ya está en funcionamiento."
		else:
			if self.verbose: print "El hilo no se ha ejecutado."
		return False
					
	
	
	# Se hace el condicional para evitar terminar el hilo antes de lanzarlo.
	def terminar(self):
		if Thread.isAlive(self): self.__terminar=True
				
	
	# RUN - salto de canales.
	def run(self):
		# Bucle infinito
		while not (self.__terminar):
			for canal in self.lista_canales:
					# Si pausar activo entonces pasamos a la siguiente iteracion.
					if (self.__pausar): continue
					# Si hay un error pasamos a la siguiente iteracion.
					if (self.__cambiar_canal(canal)): continue
					# Asignamos el canal actual.
					if not (self.__cambiar_canal(canal)):
						self.canal_actual = canal
					print "Run: " + Thread.getName(self) + " Canal: " + str(self.canal_actual)
					if (canal in self.__lista_VIC):
						sleep(self.__espera_VIC)
					else:
						sleep(self.__espera)	 	
					
	
	
		
#....................... Métodos privados. .............................
	
	
	def __get_pausar(self):
		return self.__pausar 
	
	def __lista_canales_valida(self, _24Ghz, _5Ghz):
		if not (_24Ghz or _5Ghz):
			if (self.verbose):
				print "[!] Error, lista de canales vacia. Activa al menos una de las listas: _4Ghz=True, _5Ghz=True"
			sys.exit(-15)		
		
		
	def __comprobar_interfaz(self, interfaz):
		if not (existe_interfaz(interfaz)):
			if (self.verbose):
				print "[!] Error, la interfaz no existe."
			sys.exit(-16)	
		if not (esta_modo_monitor(interfaz)):
			if (self.verbose):
				print "[!] Error, la interfaz no esta en modo monitor."
			sys.exit(-17)
		return interfaz
	
	
	# Devolemos Error = True / False
	def __cambiar_canal(self, canal):
		try:
			salida = Popen(['iw', 'dev', self.interfaz, 'set',  'channel', str(canal)], stdout=DN, stderr=PIPE)
			error = salida.stderr.read()
			salida.stderr.close()
			return (error!="")
		except OSError as ee:
			if self.verbose: print 'Error, no se ha podido ejecutar iw.'
			os.kill(salida.pid,SIGINT)
			return True


	def __comprobar_canales(self, lista):
		canales_validos = []
		if self.verbose: print "Se empieza con la comprobación de canales..."
		for canal in lista:
			# Si no hay errores guardamos el canal como válido.
			if not (self.__cambiar_canal(canal)): 
				canales_validos.append(canal)
			else:
				print "Fallo en el canal: " + str(canal) + "."
		if canales_validos == []:
			if self.verbose: print "Todos los canales han fallado, lista vacía."
			sys.exit(-19)
		if self.verbose: print canales_validos
		return canales_validos	
		

########################################################################
		
if __name__ == '__main__':
	a = SaltoCanal("wlan1", check = True)
	#a = SaltoCanal("wlan1", check = True, _24Ghz=True, _5Ghz=True)
	#a.start()
	#a.start()
		
	a.start()
	raw_input('Press enter to stop...')
	a.lista_VIC([10, 12], espera=10)
	raw_input('Press enter to stop...')
