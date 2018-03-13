#!/usr/bin/python3

from webapp import webApp
import csv
import os

formulario = """<form action="" method = "POST"><input type="text" name="Introduce la URL:" value=""><br><input type="submit"value="Enviar"></form>"""

class Acorta_Url(webApp):

    contador = 0
    diccionario_url_cortas = {} #Clave url, valor url corta
    diccionario_url_largas = {} #Clave url corta, valor url larga

    def leer_fichero (self,fichero):

        if os.stat(fichero).st_size == 0:
            print("Vacío")
        else:
            csvarchivo = open(fichero, 'r')  # Abrir archivo csv
            contenido = csv.reader(csvarchivo)
            for fila in contenido:
                self.diccionario_url_cortas[fila[1]] = int(fila[0])
                self.diccionario_url_largas[int(fila[0])] = fila[1]
            csvarchivo.close()
            #ahora cuento las lineas
            csvarchivo = open(fichero, 'r')
            self.contador = len(csvarchivo.readlines())            
            csvarchivo.close()           
            return None

    def escribir_fichero (self, fichero, clave, valor):

        csvarchivo = open(fichero, "a")
        writer = csv.writer(csvarchivo)
        writer.writerow([clave] + [valor])
        csvarchivo.close() 
        return None
    

    def parse(self,request):

        metodo = request.split()[0] #GET o POST
        recurso = request.split()[1] #/ o /loquesea
        if metodo == "GET":
            cuerpo = "" #si es un GET no tiene cuerpo
        elif metodo == "POST":
            cuerpo = request.split('\r\n\r\n',1)[-1].split("=")[1] #si es POST sí tiene cuerpo, está al final
        return (metodo,recurso,cuerpo)


    def process(self,parsedRequest):

        metodo,recurso,cuerpo = parsedRequest
        codigo_respuesta = ""
        cuerpo_html = ""

        if len(self.diccionario_url_cortas) == 0: #si mi diccionario está vacío, leo el fichero
            self.leer_fichero('fich.csv')
        if metodo == "GET":
            if recurso == "/":
                codigo_respuesta = "200 OK"
                cuerpo_html = "<html> URL a acortar: " + formulario + "<p>" + str(self.diccionario_url_largas) + "</p><html>"
            else: #si es un GET y no es de /, me están pidiendo una dirección que ya tengo, luego redirecciono
                url_corta = recurso.split("/")[1]
                if url_corta in self.diccionario_url_largas: #redirecciono si la tengo, claro
                    codigo_respuesta = "300 Redirect"
                    cuerpo_html = "<html><body><meta http-equiv='refresh'"\
										+ "content='1 url="\
										+ self.diccionario_url_largas[url_corta] + "'>"\
										+ "</p>" + "</body></html>"
                else: #si no la tengo, código de error
                    codigo_respuesta = "404 Not Found"
                    cuerpo_html = "<html><body>"\
										+ "Error: Recurso no disponible"\
										+ "</body></html>"
        elif metodo == "POST":
            if cuerpo == "": #no trae una qs, devuelve una pagina html con un mensaje de error
                httpCode = "404 Not Found"
                htmlBody = "<html><body>"\
								+ "Error: no se introdujo ninguna url"\
		                  + "</body></html>"
            else: #es un post con una dirección a tramitar
                codigo_respuesta = "200_OK"
                if (cuerpo.find("http://") == -1 and cuerpo.find("https://") == -1): #si no lleva el http o el https
                    url = "http://" + cuerpo #se lo añado
                else: #sí lo lleva, no se lo añado
                    url = cuerpo
                if url in self.diccionario_url_cortas: 
                    None #si la url ya la tengo, no la añado
                else: #si no la tengo en el diccionario, la añado a los dos diccionarios y escribo en el fichero
                    self.diccionario_url_largas[str(self.contador)] = url
                    self.diccionario_url_cortas[url] = str(self.contador)
                    self.escribir_fichero('fich.csv', self.contador, url)
                    self.contador = self.contador + 1
                   
                cuerpo_html = "<html>" + "<a href ="+ str(url) + ">" + str(url) + "</a>" + "<br>" + "<a href =" + str(self.diccionario_url_cortas[url]) + ">" + str(self.diccionario_url_cortas[url]) + "</a></html>" + '\n' + "Quieres acortar otra URL?:" + "<html>" + formulario + "<html>"  
        else:
            httpCode = "404 Not Found"
            htmlBody = "<html><body>Metodo no soportado</body></html>"
        return (codigo_respuesta, cuerpo_html) #mando mi página html       

if __name__ == "__main__":
    try:
        testWebApp = Acorta_Url("localhost",1234)
    except KeyboardInterrupt:
        print ("")
