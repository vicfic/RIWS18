# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from competiciones.items import Competicion
from scrapy.exceptions import CloseSpider
import re

class CompeticionSpider(CrawlSpider):
    """ Competicion spider """
    # nombre del spider cuando se invoque desde terminal --> scrapy crawl competicion
    name = 'competicion'
    count = 0
    item_count = 0
    custom_settings = {
        'ITEM_PIPELINES': {
             'competiciones.pipelines.CompeticionesPipeline': 0
        }
    }
    # dominios permitidos para crawlear la información
    allowed_domains = ['vamosacorrer.com','runnea.com']
    # semilla de inicio del crawler
    start_urls = ['http://www.vamosacorrer.com/carreras/triatlones/',
                    'http://www.vamosacorrer.com/carreras/marchas-montana/','http://www.vamosacorrer.com/carreras/carreras-montana/',
                    'http://www.vamosacorrer.com/carreras/duatlones/','http://www.vamosacorrer.com/carreras/populares/','https://www.runnea.com/carreras-populares/calendario/']

    # reglas de extracción de información
    rules = {
        Rule(LinkExtractor(allow=(),restrict_xpaths = ('//*[@id="principal"]/div[*]/div')), callback = 'parse_vamos_a_correr', follow = True),
        Rule(LinkExtractor(allow=(),restrict_xpaths = ('//*[@id="carreras"]/div[13]/ul/li[6]/a'))),
        Rule(LinkExtractor(allow=(),restrict_xpaths = ('//*[@id="carreras"]/div[13]/ul/li[8]/a'))),
        Rule(LinkExtractor(allow=(),restrict_xpaths = ('//*[@id="carreras"]/div[*]/div[*]/article/div/div/div/h2/a')), callback = 'parse_runea', follow = True)
    }

    """ ************************************************************************************
            Método para parsear los datos de la página de www.vamosacorrer.com
        ************************************************************************************
    """
    def parse_vamos_a_correr(self, response):
        """ Competiciones information parser """

        compet = Competicion()

        # url que se utiliza como id
        urlId = response.url
        compet['url'] = urlId
        # nombre de la competición
        compet['nombre'] = response.xpath("//*[@id='ficha']/div/div/div[1]/div/dl/dd[1]/text()").extract()[0]
        # URL cartel de la competición
        urlCartel = response.xpath("//*[@id='ficha']/figure/a/img/@src").extract_first()
        if urlCartel:
            compet['urlCartel'] = "http://www.vamosacorrer.com"+urlCartel
        # descripcion de la competición 
        compet['descripcion'] = response.xpath('//*[@id="ficha"]/div/p/text()').extract()    
        # Provincia de la competición
        compet['provincia'] = response.xpath('normalize-space(//*[@id="ficha"]/div/div/div[1]/div/dl/dd[contains(@itemprop,"location")]/text())').extract_first().replace(' ','_')
        # comunidad autónoma donde es la competición
        compet['comunidadAutonoma'] = response.xpath('normalize-space(//*[@id="ficha"]/div/div/div[1]/div/dl/dd[3]/text())').extract_first()
        # Fecha de la competición
        fecha = response.xpath('normalize-space(//*[@id="ficha"]/div/div/div[1]/div/dl/dd[4]/time/text())').extract()
        self.parse_fecha(response,compet,fecha)
        # Distancia de la carrera
        distancia = response.xpath('normalize-space(substring-before(//*[@id="ficha"]/div/div/div[1]/div/dl/dd[5]/text()," "))').extract_first() 
        if("kms." in distancia ):
            compet['distancia'] = float(distancia.replace('kms',''))
        else:
            compet['distancia'] = float(distancia.replace(',','.'))
        # Número de participantes
        compet['participantes'] = response.xpath('normalize-space(//*[@id="ficha"]/div/div/div[1]/div/dl/dd[6]/text())').extract_first()
        # Organizador de la competición 
        compet['organizador'] = response.xpath('normalize-space(//*[@id="ficha"]/div/div/div[1]/div/dl/dd[7]/text())').extract_first()
        # Modalidad de competición
        modalidad = []
        if urlId =='http://www.vamosacorrer.com/carreras/mello-saria-2019-muskiz-20190218/':
            modalidad.append("Carreras_de_Montaña")
        else:
            if urlId =='http://www.vamosacorrer.com/carreras/transgrancanaria-2020--20190604/':
                modalidad.append("Carreras_de_Montaña")
            else:
                if urlId =='http://www.vamosacorrer.com/carreras/mello-saria-2019-carreramarcha-de-montana-20190521/':
                    modalidad.append("Marchas_de_Montaña")
                else:
                    if urlId =='http://www.vamosacorrer.com/carreras/ironman-vitoriagasteiz-2019-20190218/':
                        modalidad.append("Triatlon")
                    else:
                        modalidad.append("Carreras_populares")

        compet['modalidad'] = modalidad
        yield compet

    """ ********************************************************************************************************
            Método para mostrar por consola  los datos de la página de www.vamosacorrer.com que se parsean.
        ********************************************************************************************************
    """
    def parse_vamos_a_correr_print(self, response):
        """ Competiciones information parser """

        compet = Competicion()

        print("************************* VAMOS A CORRER **********************************")
        urlId = response.url
        print("ID: ",urlId)
        nombre = response.xpath("//*[@id='ficha']/div/div/div[1]/div/dl/dd[1]/text()").extract()
        if nombre:
            print("Nombre carrera: ",nombre)
        urlCartel = response.xpath("//*[@id='ficha']/figure/a/img/@src").extract_first()
        if urlCartel:
            print("Cartel url: http://www.vamosacorrer.com"+urlCartel)
        provincia = response.xpath('normalize-space(//*[@id="ficha"]/div/div/div[1]/div/dl/dd[contains(@itemprop,"location")]/text())').extract_first()
        print("Provincia: ",provincia)
        comunidad = response.xpath('normalize-space(//*[@id="ficha"]/div/div/div[1]/div/dl/dd[3]/text())').extract_first()
        print("Comunidad Autónoma: ",comunidad)
        descripcion = response.xpath('//*[@id="ficha"]/div/p/text()').extract()
        print("Descripcion: ",descripcion)
        fecha = response.xpath('normalize-space(//*[@id="ficha"]/div/div/div[1]/div/dl/dd[4]/time/text())').extract()
        print("Fecha-Hora: ",fecha)
        self.parse_fecha(response,compet,fecha)
        print("Fecha formateada: ",compet['fecha'])
        distancia = response.xpath('normalize-space(substring-before(//*[@id="ficha"]/div/div/div[1]/div/dl/dd[5]/text()," "))').extract_first()
        print("Distancia:",float(distancia.replace(',','.')))
        participantes = response.xpath('normalize-space(//*[@id="ficha"]/div/div/div[1]/div/dl/dd[6]/text())').extract_first()
        print("Nº Participantes: ",participantes)
        organizador = response.xpath('normalize-space(//*[@id="ficha"]/div/div/div[1]/div/dl/dd[7]/text())').extract_first()
        print("organizador",organizador)

        modalidad = []
        if urlId =='http://www.vamosacorrer.com/carreras/mello-saria-2019-muskiz-20190218/':
            modalidad.append("Carreras_de_Montaña")
        else:
            if urlId =='http://www.vamosacorrer.com/carreras/transgrancanaria-2020--20190604/':
                modalidad.append("Carreras_de_Montaña")
            else:
                if urlId =='http://www.vamosacorrer.com/carreras/mello-saria-2019-carreramarcha-de-montana-20190521/':
                    modalidad.append("Marchas_de_Montaña")
                else:
                    if urlId =='http://www.vamosacorrer.com/carreras/ironman-vitoriagasteiz-2019-20190218/':
                        modalidad.append("Triatlon")
                    else:
                        modalidad.append("Carreras_populares")
        
        print("Modalidad vamos a correr: ",modalidad)
        print("******************************** FIN VAMOS A CORRER ***************************")

        yield compet

    """ ************************************************************************************
            Método para parsear los datos de la página de www.runnea.com
        ************************************************************************************
    """
    def parse_runea(self, response):
        """ Competiciones information parser """

        compet = Competicion()

        # url que se utiliza como id
        compet['url'] = response.url
        
        # nombre de la competición
        compet['nombre'] = response.xpath("//*[@id='blog-articulo']/h1").extract()
        
        # URL cartel de la competición
        urlCartel = response.xpath("//*[@id='blog-articulo']/div[1]/figure/img/@src").extract_first()
        if urlCartel:
            compet['urlCartel'] = "http://www.runnea.com"+urlCartel
        
        # Provincia de la competición
        compet['provincia'] = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[3]/text())').extract_first().replace(' ','_')
        
        # país donde es la competición
        compet['pais'] = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[3]/text())').extract_first() 
        
        #Descripcion competición
        descripcion = response.xpath('//*[@id="blog-articulo"]/div[*]/span').extract()
        compet['descripcion'] = descripcion

        # Fecha de la competición
        fecha = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[contains(@itemprop,"startDate")]/text())').extract()
        self.parse_fecha(response,compet,fecha)
        # hora = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[6]/text())').extract_first()
       # if hora:
           # compet['fecha'] = fecha+" - "+hora
        #else:
            #compet['fecha'] = fecha
        
        # Distancia de la carrera
        distancia = response.xpath('normalize-space(substring-before(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[4]/text()," "))').extract_first()
        if("Km" in distancia ):
            distancia2 = distancia.replace('Km','')
            compet['distancia'] = float(distancia2.replace(',','.'))
        else:
            compet['distancia'] = float(distancia.replace(',','.'))
        # Número de participantes
        tagParticipante = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dt[7]/text())').extract_first()
        if tagParticipante=="Participantes":
            compet['participantes'] = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[7]/text())').extract_first()
        
        # Organizador de la competición 
        compet['organizador'] = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[contains(@itemprop,"organizer")]/text())').extract_first()
        
        # lugar
        lugarItem = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[2]/span[1]/text())').extract_first()
        if lugarItem:
            compet['lugar'] = lugarItem
        
        # superficie
        compet['superficie'] = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[5]/text())').extract_first()
        
        # página web de la carrera
        tagPaginaWeb = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dt[9]/text())').extract()
        if tagPaginaWeb=='P\xe1gina web':
            paginaweb = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[9]/a/@href)').extract_first()
        paginaweb = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd/a/@href)').extract_first()  
        compet['web'] = paginaweb
        
        # Modalidad de competición
        #modalidad = "Carreras_populares"
       # compet['modalidad'] = modalidad
       # if (("Triatlón").encode('utf-8') in compet['superficie'][0]):
        compet['modalidad'] = compet['superficie']

        yield compet     

    """ *************************************************************************************************
            Método para mostrar por consola  los datos de la página de www.runnea.com que se parsean.
        *************************************************************************************************
    """
    def parse_runea_print(self, response):
        """ Competiciones information parser """

        compet = Competicion()

        print("***************************** RUNNEA ******************************")
        urlId = response.url
        print("ID: ",urlId)
        nombre = response.xpath("//*[@id='blog-articulo']/h1").extract()[0].encode('utf-8')
        if nombre:
            print("Nombre carrera: ",nombre)
        urlCartel = response.xpath("//*[@id='blog-articulo']/div[1]/figure/img/@src").extract_first()
        if urlCartel:
            print("Cartel url: http://www.runnea.com"+urlCartel)
        provincia = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[3]/text())').extract_first()
        print("Provincia: ",provincia)
        pais = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[3]/text())').extract_first() 
        print("Pais: ",pais)
        organizador = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[contains(@itemprop,"organizer")]/text())').extract_first()
        print("Organizador: ",organizador)
        descripcion = response.xpath('//*[@id="blog-articulo"]/div[*]/span').extract()
        print("Descripcion: ",descripcion)
        fecha = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[contains(@itemprop,"startDate")]/text())').extract()
        hora = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[6]/text())').extract_first()
        if hora:
            print("Fecha-Hora",fecha+" - "+hora)
        else:
            print("Fecha-Hora",fecha)
        self.parse_fecha(response,compet,fecha)
        print("Fecha formateada: ",compet['fecha'])
        lugar = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[2]/span[1]/text())').extract_first()
        print("Lugar: ",lugar)
        superficie = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[5]/text())').extract()
        print("Superficie: ",superficie)
        tagParticipante = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dt[7]/text())').extract_first()
        if tagParticipante=="Participantes":
             participantes = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[7]/text())').extract_first()
             print("Participantes",participantes)
        distancia = response.xpath('normalize-space(substring-before(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[4]/text()," "))').extract_first()
        print("Distancia: ",float(distancia.replace(',','.')))

        tagPaginaWeb = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dt[9]/text())').extract()
        if tagPaginaWeb=='P\xe1gina web':
            paginaweb = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd[9]/a/@href)').extract_first()
        paginaweb = response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl/dd/a/@href)').extract_first()
        print("Pagina Web: ",paginaweb)
        if superficie == 'Triatlón':
            print("modalidad",superficie)
        print("Modalidad: Carreras populares")
        print("************ prueba propiedades runea : ", response.xpath('normalize-space(//*[@id="blog-articulo"]/div[1]/aside/div/div/dl)').extract())
        print("**************************FIN RUNNEA *********************************")

        yield compet

    def parse_fecha(self, response, compet,fecha):
        """ parseo de fechas """
        if fecha:
            fechaTrozeada = fecha[0].split()
            dia = fechaTrozeada[0]
            mes = fechaTrozeada[2]
            ano = fechaTrozeada[4]
            mesNum = "1"
            if mes == 'enero':
                mesNum = "1"
            elif mes == 'febrero':
                mesNum = "2"
            elif mes == 'marzo':
                mesNum = "3"
            elif mes == 'abril':
                mesNum = "4"
            elif mes == 'mayo':
                mesNum = "5"
            elif mes == 'junio':
                mesNum = "6"
            elif mes == 'julio':
                mesNum = "7"
            elif mes == 'agosto':
                mesNum = "8"
            elif mes == 'septiembre':
                mesNum = "9"
            elif mes == 'octubre':
                mesNum = "10"
            elif mes == 'noviembre':
                mesNum = "11"
            elif mes == 'diciembre':
                mesNum = "12"
            fechaFormateada = ano+"-"+mesNum+"-"+dia+"T00:00:00Z"
            compet['fecha'] = fechaFormateada

