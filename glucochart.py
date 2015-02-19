# -*- encoding: utf-8 -*-
import csv
import sys
import re
import datetime as dt
from subprocess import call
import time
from pprint import pprint
#15/02/2015, 1.Después, Almuerzo, 23:34, 116 mg/dL, , , ,
#16/02/2015, 0.Antes, Solo glucosa, 03:19, 120 mg/dL, , , ,
#16/02/2015, 0.Antes, Desayuno, 08:54, 121 mg/dL, 2.00u, 2.00u, 50 gramos,
#16/02/2015, 0.Antes, Almuerzo, 10:59, 133 mg/dL, , , 10 gramos,


def load_csv():

	rapida_dict   = {}
	hidratos_dict = {}
	unidadesRapida_dict  = {}
	unidadesLenta_dict = {}
	glucosa_dict = {}

	matche = re.compile("^\d.*")
	with open('tests.csv', 'rb') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=';')

		for row in spamreader:
			
			fecha = row[0]
			if not matche.match(fecha): continue

		 	ingesta = row[1]
			tipo_medida = row[2]
		        hora = row[3]
			glucosa_T = row[4]
			unidades_rapida_T = row[5]
			unidades_lenta_T = row[6]
			hidratos_T = row[7]
			observaciones = row[8]	

			# campos normalizados	
			dia  = fecha.split('/')[0]
			mes  = fecha.split('/')[1]
			anio = fecha.split('/')[2]
		 	horas = hora.split(':')[0]
			minutos = hora.split(':')[1]
			segundos = 0
			

			# hidratos de carbono		
			if hidratos_T:
				hidratos = hidratos_T.split(' ')[0]	
				valor_hidrato =  "[Date.UTC(%s, %s, %s, %s, %s), %s]" % (anio,mes,dia,horas,minutos, hidratos)				
				if hidratos_dict.has_key(fecha):
					hidratos_dict[fecha].append(valor_hidrato)	
				else:
					hidratos_dict[fecha] = [valor_hidrato]
			# unidades rapida
			if unidades_rapida_T:
				unidades_rapida = unidades_rapida_T.split('u')[0]
				valor_unidades_rapida = "[Date.UTC(%s, %s, %s, %s, %s), %s]" % (anio,mes,dia,horas,minutos, unidades_rapida)
				if unidadesRapida_dict.has_key(fecha):
					unidadesRapida_dict[fecha].append(valor_unidades_rapida)
				else:
					unidadesRapida_dict[fecha] = [valor_unidades_rapida]


				# rango en %				
	                        if rapida_dict.has_key(fecha):
       		                        rapida_dict[fecha].append(retorna_tres_horas(anio, mes, dia, horas, minutos, segundos))
	                        else:
	                                rapida_dict[fecha] = [retorna_tres_horas(anio, mes, dia, horas, minutos, segundos)]

                        # unidades lenta
                        if unidades_lenta_T:
                                unidades_lenta = unidades_lenta_T.split('u')[0]
                                valor_unidades_lenta = "[Date.UTC(%s, %s, %s, %s, %s), %s]" % (anio,mes,dia,horas,minutos, unidades_lenta)
                                if unidadesLenta_dict.has_key(fecha):
                                        unidadesLenta_dict[fecha].append(valor_unidades_lenta)
                                else:
                                        unidadesLenta_dict[fecha] = [valor_unidades_lenta]
			# glucosa
			if glucosa_T:
				glucosa = glucosa_T.split(' ')[0]
				if glucosa != "0":
					valor_glucosa = "[Date.UTC(%s, %s, %s, %s, %s), %s]" % (anio,mes,dia,horas,minutos, glucosa)
					if glucosa_dict.has_key(fecha):
						glucosa_dict[fecha].append(valor_glucosa)
					else:
						glucosa_dict[fecha] = [valor_glucosa]
	
				
	#pprint(rapida_dict)	
	#pprint(hidratos_dict)
	#pprint(unidadesRapida_dict)	
	#pprint(glucosa_dict)

	return rapida_dict, hidratos_dict, unidadesRapida_dict, glucosa_dict
		

def header():

	m = '''
	<!DOCTYPE html>
	<html>
	<head>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8">
	<title> Gluco Chart </title>
	<script type='text/javascript' src='//code.jquery.com/jquery-1.9.1.js'></script>
	<link rel="stylesheet" type="text/css" href="/css/result-light.css">
	<style type='text/css'>
	</style>
	<script type='text/javascript'>
	$(function () {

	'''

	return m

def footer(dias):


	current_time = time.strftime("%d/%m/%Y %H:%M:%S")
	total_containers = []	
	for i in sorted(dias, reverse=True):	
		dia =  i.replace('/','-')
		container = '<div id="D%s" style="min-width: 310px; height: 400px; margin: 0 auto"></div>' % dia
		total_containers.append(container)

	total_containers_string = '\n'.join(total_containers)
		

	m = '''
	
	
	});
	</script>
	</head>
	<body>

	<script src="http://code.highcharts.com/highcharts.js"></script>
	<script src="http://code.highcharts.com/modules/exporting.js"></script>
	Last update: %s
	<div>
		%s
	<div>


	</body>


	</html>
	''' % (current_time, total_containers_string)

	return m

def retorna_tres_horas(anio, mes, dia, horas, minutos, segundos):

	''' Dado una hora, generamos 4 registros con horas consecutivas
        [Date.UTC(2015, 1, 15, 1, 15), 1],
        [Date.UTC(2015, 1, 15, 2, 15), 50],
        [Date.UTC(2015, 1, 15, 3, 15), 100],
        [Date.UTC(2015, 1, 15, 4, 15), 0],
	'''

	valores = []
	horas_incremento = [ '0', '1', '2', '3']
	pasada = 0
	for i in horas_incremento:
		pasada = pasada + 1
		a = dt.datetime(int(anio), int(mes), int(dia), int(horas), int(minutos), int(segundos))

		delta = dt.timedelta(hours = int(i))
		fecha_mas_uno_T = str((dt.datetime.combine(dt.date(int(anio),int(mes),int(dia)),a.time()) + delta))
		# 2015-02-18 01:59:55
		fecha_mas_uno = fecha_mas_uno_T.split(' ')[0]
		hora_mas_uno = fecha_mas_uno_T.split(' ')[1]
		anio_mas_uno = fecha_mas_uno.split('-')[0]
		mes_mas_uno = fecha_mas_uno.split('-')[1]
		dia_mas_uno = fecha_mas_uno.split('-')[2]
		horas_mas_uno = hora_mas_uno.split(':')[0]
		minutos_mas_uno = hora_mas_uno.split(':')[1]
		segundos_mas_uno = hora_mas_uno.split(':')[2]


                if pasada == 1:
                        valor_porciento = 0
		elif pasada == 2:
			valor_porciento = 50
		elif pasada == 3:
			valor_porciento = 100
		elif pasada == 4:
			valor_porciento = 0
		else:
			pass


		valor = "[Date.UTC(%s, %s, %s, %s, %s), %s]" % (anio_mas_uno,
								mes_mas_uno,
								dia_mas_uno,
								horas_mas_uno,
								minutos_mas_uno,
								valor_porciento)
		

		valores.append(valor)
	return valores	


def build_javascript(dia_T, rapida, hidratos, unidadesRapida, glucosa):

	dia =  dia_T.replace('/','-')
	javascript = """
    $('#D%s').highcharts({
        title: {
            text: 'Glucemia %s',
	"fontSize": "12px",
            x: -20 //center
        },
        subtitle: {
            text: '-----',
            x: -20
        },
	 alignTicks: false,
        xAxis: {
            type: 'datetime',
        },

        yAxis: [{ // Primary yAxis

            gridLineWidth: 0,
            lineWidth: 0.5,
            gridLineColor: '#D8D8D8',
            max: 100,
            min: 0,
            title: {
                text: 'Insulina %%',
                style: {
                    color: '#D8D8D8'
                }
            },
            labels: {
		enabled: false,
                format: '{value} %%',
                style: {
                    color: '#D8D8D8'
                }
            },
            opposite: true

        }, { // Secondary yAxis
	    max: 60,
            min: 0,
	    tickInterval: 2,
            endOnTick: false,

            title: {
                text: 'Hidratos de Carbono (gr)',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            },
            labels: {
                format: '{value} gr',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            },
            opposite: true
        }, { // Tertiary yAxis
	    max: 250,
	    min: 40,
            labels: {
                format: '{value} mg/dL',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            },
            title: {
                text: 'Glucosa (mg/dL)',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            }

        }, { //Cuat y Axis
		min: 0,
		max: 8,
		tickInterval: 1,
		endOnTick: false,
            labels: {
                format: '{value} U',
		
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            },
            title: {
                text: 'Insulina U',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            },
            opposite: true


	}],
        tooltip: {
            backgroundColor: 'white',
            borderWidth: 0,
            borderRadius: 0,
            headerFormat: '{point.key} ',
            pointFormat: ' | <span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b></br>',
            positioner: function () {
		return { x: 450, y: 30 };
            },
            shadow: false
             //shared: true,
             //crosshairs: [true,true],
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        series: [

        {
            name: 'Rapida',
            tooltip: { valueSuffix: " %%", },
            type: 'spline',
 	    marker: { enabled: false },
            yAxis: 0,
            lineColor: '#D8D8D8',
            lineWidth: 1,
            data: [
		
			%s

                ]
        },

        {
            name: 'hidratos',
            tooltip: { valueSuffix: " gr", },
            type: 'column',
            yAxis: 1,
            color: '#00FF40',
            data: [
			%s

                ]

        },




        {
            name: 'UnidadesRapida',
            tooltip: { valueSuffix: " U", },
            type: 'column',
            yAxis: 3,
            borderWidth: 0.2,
            data: [
			%s
                ]


        },
        {
            name: 'Glucosa',
            tooltip: { valueSuffix: " mg/dL", },
            yAxis: 2,
	    color: '#B40404',
            data: [
			%s
                ]
        },


        //{
        //    name: 'desayuno',
        //    type: 'scatter',
        //    data: [
        //           [Date.UTC(2015, 1, 15, 1, 15),50],
	//
         //       ]

	 //       },






        ],

        credits: { enabled: false }
    });
	""" % (dia, dia, rapida, hidratos, unidadesRapida, glucosa) 


	return javascript	



def get_csv():
	
	call(["./get_csv.sh"])


if __name__ == '__main__':


	get_csv()

	print header()

	rapida_dict, hidratos_dict, unidadesRapida_dict, glucosa_dict = load_csv()

	keys = rapida_dict.keys()
	for dia in sorted(keys):
		unifica_rapida = []
		
		for t in rapida_dict[dia]:
			for total in t:
				unifica_rapida.append(total)

		#for rap in unifica_rapida:
		#	print rap
		rapida   = ',\n'.join(unifica_rapida)
		hidratos = ',\n'.join(hidratos_dict[dia])
		unidadesRapida = ',\n'.join(unidadesRapida_dict[dia])
		glucosa = ',\n'.join(glucosa_dict[dia])


		print build_javascript(dia, rapida, hidratos, unidadesRapida, glucosa)	
	
	print footer(sorted(keys))
