#!/usr/bin/env python
# -*- coding: utf-8 -*-​

# Autor: 		Enrique Andrade González - NeTTinG
# Web:			blog.netting.es
# email:		netting(at)netting(dot)es

# Licencia: 
# Creative commons (cc) - creativecommons.org
# Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

import sys, os, glob

VERBOSE = True

#----------->>>>>>> FALTA METER ERRORES

#|||||||||||||||||||[ CONFIGURACION DE INTERFAZ ]|||||||||||||||||||||||

def existe_interfaz(interfaz):
	if (interfaz == ""):
		return False
	return (os.path.isdir("/sys/class/net/" + interfaz))
	

def esta_modo_monitor(interfaz):
	try:
		salida = os.popen("iw dev " + interfaz + " info | grep type").read()
	except OSError as e:
		if (VERBOSE):
			print "[!] Error en Popen, al comprobar el estado (mode) de la interfaz.\n"
		sys.exit(-5)
	if "monitor" in salida:
		return True
	elif "managed" in salida:
		return False
	else:
		if (VERBOSE):
			print "[!] Error al ejecutar iw, al comprobar el estado (mode) de la interfaz."
		sys.exit(-6)


# Solo para rasperry Pi con nexmon pi		
def modo_monitor_ON():
	try:
		salida = os.popen("monstart").read()
	except OSError as e:
		if (VERBOSE):
			print "[!] Error al lanzar monstart."
		sys.exit(-7)
	return ("setting monitoring mode" in salida)
	
	
# Solo para rasperry Pi con nexmon pi		
def verificar_interfaz(interfaz):
	lista_fichs = glob.glob("/sys/class/net/wlan*")
	for fich in lista_fichs:
		int_aux = os.path.basename(fich)
		if esta_modo_monitor(int_aux):
			if interfaz != int_aux:
				param["interfaz"] = int_aux
				if (VERBOSE):
					print "[!] Error, La interfaz " + interfaz + " NO está en modo monitor."
					print "[*] Se ha cambiado la interfaz a: " + int_aux + " (mode MONITOR)..."


# Solo para raspberry pi con nexmon pi
def modo_monitor_nexmon():
	if modo_monitor_ON():
		'''	Al comando monstart no se le pasa la interfaz. Por lo que la interfaz pasada como argumento 
		a este programa puede no ser la misma que la interfaz que se ha puesto en en modo monitor.'''
		verificar_interfaz(param["interfaz"])
	else:
		if (VERBOSE):
			print "[!] Error en monstart, no es posible activar el modo monitor."
		sys.exit(-12)		



def modo_monitor():
	if not esta_modo_monitor(param["interfaz"]):
		# Solo para raspberry pi con nexmon pi
		modo_monitor_nexmon()

#|||||||||||||||||||[ /CONFIGURACION DE INTERFAZ ]||||||||||||||||||||||
