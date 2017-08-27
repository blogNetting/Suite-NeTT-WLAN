#!/usr/bin/env python
# -*- coding: utf-8 -*-​

# Autor: 		Enrique Andrade González - NeTTinG
# Web:			blog.netting.es
# email:		netting(at)netting(dot)es

# Suite NeTT-WLAN: modo_monitor.py\

# Licencia: 
# Creative commons (cc) - creativecommons.org
# Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

import os, time, sys, glob
from subprocess import call
from platform import system



def existe_interfaz(interfaz):
	return (os.path.isdir("/sys/class/net/" + interfaz))		


def is_root():
	if (os.geteuid() != 0):
		print("\n[!] Debes de ejcutar el script como root.\n")
		exit(1)

		
def OS_check():
    if (system() != "Linux"):
		print "\n[!] La herramienta solo es compatible con GNU/Linux.\n"
		exit(1)

		
def esta_modo_monitor(inter_monitor):
	return (os.path.isdir("/sys/class/net/" + inter_monitor))


def estado():
	lista_fichs = glob.glob("/sys/class/net/mon*")
	lista = []
	if (lista_fichs == []):
		lista = ["Ninguna"]
	else:
		for fich in lista_fichs:
			lista.append(os.path.basename(fich))
	print "\n\tInterfaces en modo monitor: " + ", ".join(lista) + ".\n"

	
def monitor(interfaz):
	inter_monitor = "mon0"
	if not (esta_modo_monitor(inter_monitor)):
		# Creamos interfaz en modo monitor con iw
		salida = os.system("iw dev " + interfaz + " interface add " + inter_monitor + " type monitor")
		if (salida==0):
			time.sleep(0.5)
			print "\n[*]Creada la interfaz en modo MONITOR " + inter_monitor + " sobre " + interfaz + ".,," 
			sal = os.system("ifconfig " + inter_monitor + " up")
			if (salida==0):
				print "\n[*]La interfaz " + inter_monitor + " está levantada.\n" 
			else:
				print "\n[!] No se ha podido levantar la interfaz " + inter_monitor + ".\n" 
		else:
			print "[!] No se ha podido crear la interfaz en modo monitor " + inter_monitor + "-\n"
			sys.exit(1)
	else:
		print "\n[!] Ya existe una interfaz mon0 en modo MONITOR.\n"
	
	
def stop(interfaz):
	if (esta_modo_monitor(interfaz)):
		os.system("iw dev " + interfaz + " del")
		print "\n[*]Interfaz " + interfaz + " eliminada.\n"
	else:
		print "\n[!]No existe la interfaz " + interfaz + ".\n"

		
def uso():
	print "\n\tSuite NeTT-WLAN: modo_monitor.py\n" 
	print "\tCreative commons (cc) - creativecommons.org"
	print "\tAttribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)\n\n"
	
	print "\tUso: modo_monitor.py con\n"
	print "\t  [estado] Muestra las interfaces en modo MONITOR."
	print "\t  [interfaz] mo|monitor: Activa el modo MONITOR en la inteffaz seleccionada."
	print "\t  [interfaz] parar|stop: Activa el modo managed en la inteffaz seleccionada.\n"
	exit(1)
	
	
def main(args):
	if (len(args) == 0):
		estado()
	elif (len(args) == 1):
		if args[0] in ["st", "estado"]:
			estado()
		else:
			uso()
	elif(len(args)== 2):
		if (existe_interfaz(args[0])):
			if args[1] in ["mo", "monitor"]:
				monitor(args[0])
			elif args[1] in ["parar", "stop"]:
				stop(args[0])
			else:
				uso()
		else:
			print "\n[!] No existe la interfaz \"" + args[0] + "\".\n"
	else:
		uso()
		
		
if __name__ == '__main__':
	OS_check()
	is_root()
	main(sys.argv[1:])
