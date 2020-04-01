
import os  # clsFTP, copia(), clsUAC
import sys  # clsUAC
import ctypes   # clsUAC

import shutil      # copia()
from distutils.dir_util import copy_tree   # copia()

from ftplib import FTP   # clsFTP

class clsFTP():
    def __init__(self):
        self.DirLocal = os.getcwd()
        self.Servidor = ""
        self.Usuario = ""
        self.Password = ""
        self.DirRemoto = ""
        self.bolConectado = False
    
    def conecta(self, strServidor, strUsuario, strPassword):
        try:
            self.Servidor = strServidor
            self.strUsuario = strUsuario
            self.Password = strPassword
            
            self.ftp =  FTP(strServidor,strUsuario,strPassword)
            self.DirRemoto = self.ftp.pwd()
            self.bolConectado = True
            print(self.ftp.getwelcome())
        except Exception as err:
            self.bolConectado = False
            print("ERROR DE CONEXION")
            print(err)

    def desconecta(self):
        self.ftp.quit()
        self.bolConectado = False

    def dirLocal(self, strDirLocal):
        if not os.path.isdir(strDirLocal):
            os.makedirs(strDirLocal, exist_ok=True)
        os.chdir(strDirLocal)        
    def descarga(self, ruta, filename):
        print("DESCARGAR ", ruta + "/" + filename, " a ", os.getcwd())
        try:
            with open(filename, "wb") as fp:
                self.ftp.retrbinary("RETR " + ruta + "/" + filename, fp.write)
            # print(self.ftp.size(filename))
            # print(os.path.getsize(filename))

        except Exception as e:
            print("Error " + str(e))
            try:
                self.ftp.cwd(ruta + "/" + filename)
                try:
                    fp.close()
                except:
                    pass
                try:
                    os.remove(filename)
                except:
                    pass
                os.makedirs(filename, exist_ok=True)
                os.chdir(filename)
                listaD = self.ftp.nlst()
                for i in range(len(listaD)):
                    self.descarga(self.ftp.pwd(), listaD[i])
                self.ftp.cwd("..")
                os.chdir("..")
            except Exception as e:
                print("Error Download" + str(e))
    def interactivo(self):
        while 1:
            self.listarRemoto()
            self.DirRemoto = self.ftp.pwd()
            self.DirLocal = os.getcwd()
            print("\nFTP  by UCLA")
            print("Servidor:",self.Servidor)
            print("Directorio Local:",self.DirLocal)
            print("Directorio Remoto:",self.DirRemoto)
            #print("\n")
            strOpcion = input("Opción (H ayuda): ")
            if strOpcion.lower().strip() == "q":
                break
            self.evaluaOpcion(strOpcion)
    def evaluaOpcion(self, strOpcion):
        strOpcion = strOpcion.lower().strip()
        dicOpciones = {"ll" : "self.listarLocal()", "lr" : "self.listarRemoto()",
                       "cr" : "self.cdRemoto()", 
                       "h" : "self.Ayuda()"
                        }
        if strOpcion[0] == "d":
            if strOpcion[0:3] == "dir":
                self.listarLocal()
            else:
                intOpcion = int(strOpcion.replace("d",""))
                self.descarga(self.ftp.pwd(), self.lstDirectorio[intOpcion][1])
        if strOpcion[0:2] == "..":
            self.ftp.cwd("..")
        if strOpcion.isdigit():
            intOpcion = int(strOpcion)
            try:
                self.ftp.cwd(self.lstDirectorio[intOpcion][1])
            except Exception as e:
                print("Error al cambiar directorio remoto: " + str(e))
        if strOpcion[0:2] == "cd":
            try:
                os.chdir(strOpcion[3:])
            except Exception as e:
                print("error al cambiar directorio local " + str(e))
        
        if strOpcion in dicOpciones.keys():
            eval(dicOpciones[strOpcion])
        
            
    def Ayuda(self):
        print("\nUn poco de AYUDA:")
        print("""
<numero> - Cambia Directorio Remoto
D <numero> - Descarga Archivo/Directorio Remoto
CD <Directorio> - Cambia Directorio Local
DIR - Listar Directorio Local Actual.
Q - Termina Interactivo\n
        """)

    def listarLocal(self):
        for elemento in os.listdir():
            if os.path.isdir(elemento):
                print("\t<DIR>", elemento)
            else:
                print("\t", elemento)

    def listarRemoto(self):
        if self.bolConectado:
            self.lstDir = []
            self.lstDirectorio = []
            self.lstnlst = self.ftp.nlst()
            self.ftp.dir(self.ftp.pwd(), self.lstDir.append)
            for i in range(len(self.lstDir)):
                try:
                    intSize = self.ftp.size(self.lstnlst[i])
                    strType = "F"
                except:
                    intSize = 0
                    strType = "D"
                self.lstDirectorio.append([self.lstDir[i], self.lstnlst[i], strType, intSize])
                print(i,self.lstDirectorio[i][0])
    
    def cdRemoto(self):
        pass
# ********************************************************************************************8
class clsUAC:
    def __init__ (self):
        try:
            self.UACStatus = ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as error:
            print("NO es posible obtener privilegios UAC: %s" % error)
            self.UACStatus = 0
        self.set()
    def get (self):
        return bool(self.UACStatus)
    
    def set (self):
        if not self.get():
            try:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable,os.path.abspath(sys.argv[0]), None, 1)
            except Exception as error:
                print("NO es posible ELEVAR privilegios UAC: %s" % error)
# ********************************************************************************************8
# FUNCION copia()

def copia(strOrigen="", strDestino=""):
    if strOrigen == "":           # Si no se pasa origen
        strOrigen = os.getcwd()   # se toma el directorio actual 
    if os.path.exists(strOrigen):  # Si existe el origen let's play...
        if strDestino == "":   # si no se pasa el destino entonces será origen_copia
            strDestino = os.path.splitext(strOrigen)[0] + "_Copia" + os.path.splitext(strOrigen)[1]
        
        if os.path.splitext(strDestino)[1] == "":  #  posible directorio
            os.makedirs(strDestino, exist_ok=True) # Crea los directorios

        if os.path.isfile(strOrigen):  # si queremos copiar un solo archivo
            os.makedirs(os.path.dirname(os.path.abspath(strDestino)), exist_ok=True)
            shutil.copy(strOrigen, strDestino)
            
        if os.path.isdir(strOrigen):  # si lo que queremos copiar es un directorio
            copy_tree(strOrigen, strDestino)

 