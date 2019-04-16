import os
import shutil
from PyQt4.QtGui import QProgressDialog, QProgressBar
from qgis.core import QgsProject
from PyQt4.QtCore import QFileInfo
import os
import processing
from PyQt4.QtGui import QProgressDialog, QProgressBar
from qgis.core import QgsProject
from PyQt4.QtCore import QFileInfo
import os
from qgis.analysis import *
from osgeo import gdal
import glob
import numpy as np

#variables globales 
rootdir='C:/Users/gigabyte/Desktop/Sentinel2'#chemin d acces au reperoire de travail
Rrootdir = "C:/Users/gigabyte/Desktop/Sentinel2/2017"#chmein d acces au reperoire qui contient les images satellitaires
Vrootdir =  "C:/Users/gigabyte/Desktop/Sentinel2/Terroir"#chemin d acces au repertoire qui contient les fichiers vecteur(AOC, regions, parcelles,...)
TypeR="Raster"
TypeV="Vector"
crs_base = QgsCoordinateReferenceSystem( 32631, QgsCoordinateReferenceSystem.EpsgCrsId )#systeme de coordonnes du projet : UTM-WGS84 zone 31
ClipFolder_Cloud="Clip_Cloud" #un repertoire qui va etre cree et contenir les fichier vecteur(regions, parcelles,...) apres l enlevement de la partie nuageuse
ClipFolder_Terroir ="Clip_Terroir" # un repertoire qui va etre cree et contenir les images decoupees par les fichiers du repertoire ClipFolder_Cloud

#Delete_files function : supprimer tous les reperoires crees  : Clip_Cloud, Clip_Terroir, NDVI
def delete_files():
	for root, dirs, files in os.walk(Rrootdir):#parcourir le dossier Sentinel2
	  for name in dirs:
		if name=="Clip_Cloud" or name=="Clip_Terroir"  or name=="NDVI" or name=="MSI"  or name=="NDII"   :
			 shutil.rmtree(os.path.join(root,name).replace("\\","/"))
	print "les dossiers et fichiers du derniers traitement ont ete supprimes"



#Delete_mask function 
def delete_mask_cloud():
	#supprimer tous les fichier Mask_Cloud qui sont crees avec le script polygonize_cloud
	for root, dirs, files in os.walk(Rrootdir):#parcourir le dossier Sentinel2
	  for name in files:
		if name=="Mask_Cloud.prj" or name=="Mask_Cloud.dbf" or name=="Mask_Cloud.shp" or name=="Mask_Cloud.shx"  :
			   os.remove(os.path.join(root,name).replace("\\","/"))
	print "le fichier mask du dernier traitement a ete supprime"


#polygonize_cloud function
def polygonize_cloud():

	#Loop raster
	for Rsubdir, Rdirs, Rfiles in os.walk(Rrootdir):#parcourir le dossier Sentinel2
		for Rfile in Rfiles:
			Rfile,Rextension =os.path.splitext(os.path.join(Rsubdir,Rfile).replace("\\","/"))
			if Rextension == '.tif' :
				RfileName = os.path.join(Rsubdir, Rfile).replace("\\","/")+".tif"
				if os.path.isfile(RfileName) :
					RfileInfo = QFileInfo(RfileName)
					RbaseName = RfileInfo.baseName()
					Rlyr = QgsRasterLayer(RfileName, RbaseName)
					Rlyr.setCrs(crs_base)
					newpath = os.path.join(Rsubdir).replace("\\","/")+"/"
					name=Rlyr.name()
					if name[-7:]=='_CLM_R1':
						print newpath
						processing.runalg('gdalogr:polygonize', str(Rlyr.source()) , "bande",str(newpath).split("Raster")[0]+"/"+"Mask_Cloud"+".shp" )
				else :
					print "Fichier .tif non trouve"
	print "Polygonisation de l'image Nuage est faite"

		
#No_Cloud_Polygone function
def No_Cloud_Polygone():
	#crsDest = crs_base

	for subdir, dirs, files in os.walk(Rrootdir):#parcourir le dossier Sentinel2
		for file in files:
			file,extension =os.path.splitext(os.path.join(subdir,file).replace("\\","/"))
			if extension == '.shp' :
				fileName = os.path.join(subdir, file).replace("\\","/")+".shp"
				if os.path.isfile(fileName) :
					fileInfo = QFileInfo(fileName)
					baseName = fileInfo.baseName()#return the base name of the file without the path
					lyr = QgsVectorLayer(fileName, baseName,'ogr')#create a vector layer with the same name
					newpath = os.path.join(subdir).replace("\\","/")+"/Image_Clip_Cloud/"
					#print lyr.source()
					with edit(lyr):
						request = QgsFeatureRequest().setFilterExpression('"bande" = 0')#filtre de la requete
						request.setSubsetOfAttributes([])#
						request.setFlags(QgsFeatureRequest.NoGeometry)#return all features , no extent is defined
						for f in lyr.getFeatures(request):#executer la requete
							lyr.deleteFeature(f.id())# supprimer les entites(features) resultat de la requete --> avec l'attribut bande=0
				else :
					 print "Fichier shp non trouve"
	print "No Cloud polygonize was executed successfully"


#Clip_Cloud function
def Clip_Cloud():
	#Conteur
	i=0
	j=0
	vertices=[]

	#Loop raster
	global i
	global  j
	for Rsubdir, Rdirs, Rfiles in os.walk(Rrootdir):#parcourir le dossier 2018
		for Rfile in Rfiles:
			Rfile,Rextension =os.path.splitext(os.path.join(Rsubdir,Rfile).replace("\\","/"))
			if Rextension == '.shp' :#chercher le ficheir shp : Mask_Cloud
				RfileName = os.path.join(Rsubdir, Rfile).replace("\\","/")+".shp" #construire le chemin d'acces au fichier Mask_Cloud
				if os.path.isfile(RfileName) :#tester si fichier et non pas un repertoire
					RfileInfo = QFileInfo(RfileName)
					RbaseName = RfileInfo.baseName()
					Rlyr = QgsVectorLayer(RfileName, RbaseName,'ogr')#selectionner le fichier vecteur Mask_Cloud
					Rlyr.setCrs(crs_base)
					InfoFile = os.stat(RfileName)
					newpath = os.path.join(Rsubdir).replace("\\","/")+"/"+ClipFolder_Cloud+"/"+TypeV+"/"
					if not os.path.exists(newpath):#si le repertoire Clip_Cloud/Vector n existe pas, le creer
						os.makedirs(newpath)
				 #Loop vector
					for Vsubdir, Vdirs, Vfiles in os.walk(Vrootdir):#parcourir le dossier Terroir
						for Vfile in Vfiles:
							Vfile,Vextension =os.path.splitext(os.path.join(Vsubdir,Vfile).replace("\\","/"))
							if Vextension == '.shp' :#choisir que es fichiers shp
								VfileName = os.path.join(Vsubdir, Vfile).replace("\\","/")+".shp"#construire le chemin d'acces au fichier shp
								if os.path.isfile(VfileName) :#tester si fichier et non pas un repertoire
									VfileInfo = QFileInfo(VfileName)
									VbaseName = VfileInfo.baseName()
									Vlyr = QgsVectorLayer(VfileName, VbaseName,'ogr')#selectionner le fichier shp dans le dossier Terroir
									Vlyr.setCrs(crs_base)#definir le systeme de coordonnes
									if InfoFile.st_size>428 :
										out=processing.runalg("qgis:difference", str(Vlyr.source()) ,str(Rlyr.source()) ,1, newpath+Vlyr.name()+"_"+ClipFolder_Cloud+".shp" )#le parametre 0 pour ignorer les geometries non valides
										print "difference calculee :"+newpath+RbaseName#difference entre les fichiers terroir et le ficheir mask cloud 
									else :
										writer = QgsVectorFileWriter.writeAsVectorFormat(Vlyr,newpath+str(Vlyr.name())+"_"+ClipFolder_Cloud+".shp","utf-8",None,"ESRI Shapefile", False)
										print "difference non calculee : "+newpath+RbaseName
										if writer !=QgsVectorFileWriter.NoError:
											print "Error when creating  shapefile : "+writer.hasError()
				else :
					print "Fichier .jp2 non trouve"
	
	print "Clip Cloud l'enlevement de la partie nuageuse est fait"


#Progress_bar function 
def progdialog(progress):
	dialog = QProgressDialog()
	dialog.setWindowTitle("Calcul")
	dialog.setLabelText("Veuillez patienter...")
	bar = QProgressBar(dialog)
	bar.setTextVisible(True)
	bar.setValue(progress)
	dialog.setBar(bar)
	dialog.setMinimumWidth(300)
	dialog.show()
	return dialog, bar


#Clip_Image function
def Clip_Image():
	#Conteur
	i=0
	j=0

	dialog, bar = progdialog(0)#Initialiser la Progress Bar
	bar.setValue(0)
	bar.setMaximum(100)
	sum = 0
	progress = 0

	global i
	global  j
	for Rsubdir, Rdirs, Rfiles in os.walk(Rrootdir):#parcourir le dossier 2018
		for Rfile in Rfiles:
			Rfile,Rextension =os.path.splitext(os.path.join(Rsubdir,Rfile).replace("\\","/")) #separer le nom de fichier de l'extention
			if Rextension == '.tif' :#seulement les fichiers .tif
				RfileName = os.path.join(Rsubdir, Rfile).replace("\\","/")+".tif" #construire le chemin d'acces au fichier 
				if os.path.isfile(RfileName) :#tester si fichier et non pas un repertoire
					RfileInfo = QFileInfo(RfileName)
					RbaseName = RfileInfo.baseName()#le nom du fichier dans la legende
					Rlyr = QgsRasterLayer(RfileName, RbaseName)#selectionner le fichier raster tif
					newpath = os.path.join(Rsubdir).replace("\\","/")+"/"+ClipFolder_Terroir+"/"+TypeR+"/"#le chemin ou le fichier clip terroir raster va etre cree : Clip_Terroir/Raster
					ListDirR=os.path.dirname(RfileName)#le chemin d'acces au fichier

					Vrootdir= ListDirR+"/"+ClipFolder_Cloud+"/"+TypeV#chemin dossier Clip_Cloud/Vector
					
					if not os.path.exists(newpath): # si le dossier Clip_Terroir/Raster n existe pas --> le creer
						os.makedirs(newpath)
				 #Loop vector--> acceder au dossier  Clip_Cloud/Vector
					for Vsubdir, Vdirs, Vfiles in os.walk(Vrootdir): #entre pas dans la boucle -->le dossier ClipCloud/Vector est vide
						for Vfile in Vfiles:
							Vfile,Vextension =os.path.splitext(os.path.join(Vsubdir,Vfile).replace("\\","/"))
							if Vextension == '.shp' :# si l'extension du fichier est shp
								VfileName = os.path.join(Vsubdir, Vfile).replace("\\","/")+".shp"
								if os.path.isfile(VfileName) :#tester si fichier et non pas un repertoire
									VfileInfo = QFileInfo(VfileName)
									VbaseName = VfileInfo.baseName()
									Vlyr = QgsVectorLayer(VfileName, VbaseName,'ogr')#selectionne rle fichier vecteur shp
									Vlyr.setCrs(crs_base)#definir le systeme de coordonnees
									j=j+1
									i=i+1
									progress = (float(i) / float(j)) * 100
									bar.setValue(progress)
									name=Rlyr.name()
									if name[-2:]=='B8' or name[-2:]=='B4':#si bande 4 ou 8
										os.popen("gdalwarp -dstnodata -10000 -q -cutline " + str(Vlyr.source())  +" -crop_to_cutline "+ " -of GTiff " + str(Rlyr.source()) + " " + ListDirR+ "/" +ClipFolder_Terroir +"/"+TypeR+"/" +str(Rlyr.name())+"_"+str(Vlyr.name()).split(ClipFolder_Cloud)[0]+ClipFolder_Terroir+ ".tif")
										#dstnodata -1000 : set nodata values for output bands
										#-q : be quiet
										#-cutline : enable use of a blend cutlien from datasource
										#-crop_to_cutline : crop the extent of the target dataset to the extent of the cutline
										#-of GTiff : select the output format
										#le chemin apres: destination file name
										print "gdalwarp -dstnodata -10000 -q -cutline " + str(Vlyr.source())  +" -crop_to_cutline "+ " -of GTiff " + str(Rlyr.source()) + " " + ListDirR+ "/" +ClipFolder_Terroir +"/"+TypeR+"/" +str(Rlyr.name())+"_"+str(Vlyr.name()).split(ClipFolder_Cloud)[0]+ClipFolder_Terroir+ ".tif"
				else :
					print "Fichier .jp2 non trouve"

	print "function clip_Image executed"

#NDVI function
def NDVI():

	#Fichiers
	ClipFolder ="NDVI"
	#liste des fichiers de chaque bande 4 et 8
	ListeB4= []
	ListeB8= []
	#Conteur
	k=0
	#NDVI Formule
	NDVI_syntax = '(A-B)/(A+B)'
	#Progress Bar

	global k
	for Rsubdir, Rdirs, Rfiles in os.walk(Rrootdir):#parcourir le dossier 2018
		for Rfile in Rfiles:
			Rfile,Rextension =os.path.splitext(os.path.join(Rsubdir,Rfile).replace("\\","/"))
			if Rextension == '.tif' :#selectionner les ficheir tif dans le dossier 2018
				RfileName = os.path.join(Rsubdir, Rfile).replace("\\","/")+".tif"
				if os.path.isfile(RfileName) :
					RfileInfo = QFileInfo(RfileName)
					RbaseName = RfileInfo.baseName()
					Rlyr = QgsRasterLayer(RfileName, RbaseName)#charger le fichier raster avec le chemin d acces obtenu
					if ClipFolder_Terroir in Rlyr.name():#Pour selctionner seulement  les fichiers raster dans le dossier Clip_Terroir (obtenus apres les deux derniers scripts)
						newpath =Rlyr.source().split(ClipFolder_Terroir)[0]+ClipFolder+"/"  #construire le chemin d'acces au fichier --> creation du dossier NDVI
#                        print newpath
						print Rlyr.name()
						if not os.path.exists(newpath):#si le dossier n existe pas --> le creer
							os.makedirs(newpath)
						if "B4" in Rlyr.name():
							ListeB4.append(Rlyr.source())#ajouter la bande B4 a la liste
							print Rlyr.source()
						if "B8" in Rlyr.name():
							ListeB8.append(Rlyr.source())#ajouter la bande B8 a la liste
							print Rlyr.source()
							#processing.runalg('gdalogr:polygonize', str(Rlyr.source()) , "bande",str(newpath).split("Raster")[0]+ClipFolder_Terroir+"/"+Rlyr.name()+".shp" )
				else :
					print "Fichier .tif non trouve"

	while k < len(ListeB4):
		#B04
		B4fileName=ListeB4[k]
		B4fileInfo = QFileInfo(B4fileName)
		B4baseName = B4fileInfo.baseName()
		B4lyr = QgsRasterLayer(B4fileName, B4baseName)#charger le fichier raster de la bande 4

		#B08
		B8fileName=ListeB8[k]
		B8fileInfo = QFileInfo(B8fileName)
		B8baseName = B8fileInfo.baseName()
		B8lyr = QgsRasterLayer(B8fileName, B8baseName)#charger le fichier raster de la bande 8

		#NDVI
		lyr = processing.getObject(ListeB4[k])
		entries=[]
		rasterCalcEntry=QgsRasterCalculatorEntry()#creer une entree pour la bande 4 dans la calculatrice raster
		rasterCalcEntry.ref='R@1'#definir le nom de la bande dans la calculatrice de raster
		rasterCalcEntry.raster=lyr
		rasterCalcEntry.bandNumber=1
		entries.append(rasterCalcEntry)#ajouter l'entree a la calculatrice de raster 

		lyr = processing.getObject(ListeB8[k])
		rasterCalcEntry=QgsRasterCalculatorEntry()#creer une entree pour la bande 8 dans la calculatrice raster
		rasterCalcEntry.ref='NIR@1'#definir le nom de la bande dans la calculatrice de raster
		rasterCalcEntry.raster=lyr
		rasterCalcEntry.bandNumber=1
		entries.append(rasterCalcEntry)#ajouter l'entree a la calculatrice de raster 
		
		filename=B8lyr.name().split("B8")[-1].split(ClipFolder_Terroir)[0]
		outImage=B8lyr.source().split(ClipFolder_Terroir)[0]+ClipFolder+"/"+filename+"_NDVI"+".tif"#definir le nom et le chemin d'acces au ficheir 
		print outImage
		noData=0
		calc=QgsRasterCalculator('1.0*(NIR@1 - R@1)/(NIR@1 + R@1)+0.0', outImage, "GTiff",  lyr.extent(), lyr.crs(), lyr.width(), lyr.height(), entries)#definir la formule de calcul de NDVI dans la calculatrice de raster 
		calc.processCalculation()#Executer la commande pour la creation du fichier de sortie
		k += 1# passer au fichier suivant 

	print "Calcul NDVI est fait !"



#File_NDVI_v3 function --> fichier de sortie
def File_NDVI_v3():

	#Fichiers
	ClipFolder ="NDVI"
	#Conteur
	k=0
	i=0
	j=0
	e=0
	f=0
	p=0
	p_s=0
	mean=0
	ind=0
	s=0
	ecartype=0
	pixels=0
	mod=[]
	#Variables
	ListDir=[]
	NdviMean=[]
	NdviZone=[]
	NdviZoneUpdate=[]
	NdviDate=[]
	NdviScene=[]
	NdviMax=[]
	NdviMin=[]
	NdviCell=[]
	NdviEcartType=[]
	DataSupp=[]
	modif=[]
	ListArea=[]
	ListZone=[]

	#area function
	ListArea=[]
	ListZone=[]
	surface=0

	#Loop raster
	dialog, bar = progdialog(0)
	bar.setValue(0)
	bar.setMaximum(100)
	sum = 0
	progress = 0
	global i , j ,k ,e ,f,lien,p,p_s,ListDir,DataSupp,mean,ind,modif,ecartype,mod,pixels,NdviMean,NdviZone,NdviZoneUpdate,NdviDate,NdviScene,NdviMax,NdviMin,NdviCell,NdviEcartType,ListZone,ListArea

	for Rsubdir, Rdirs, Rfiles in os.walk(Rrootdir): #parcourir le dossier 2018
		for Rfile in Rfiles:
			Rfile,Rextension =os.path.splitext(os.path.join(Rsubdir,Rfile).replace("\\","/"))
			if Rextension == '.tif' :#selectionner que les fichiers raster .tif mais normalement on doit selectionner que les ficheir dans le dossier Clip_Cloud
				RfileName = os.path.join(Rsubdir, Rfile).replace("\\","/")+".tif"#construire le chemin d'acces a ce fichier 
				if os.path.isfile(RfileName) :#verifier si fichier et non pas un repertoire
					RfileInfo = QFileInfo(RfileName)#recuperer les informations sur le fichier 
					RbaseName = RfileInfo.baseName()
					Rlyr = QgsRasterLayer(RfileName, RbaseName)#charger le fichier RasterLayer 
					output_stat=Rlyr.source().split("NDVI")[0]+ClipFolder+"/"+Rlyr.name()+".html" #le chemin du fichier statistiques generales 
					output_area=Rlyr.source().split("NDVI")[0]+ClipFolder+"/"+Rlyr.name()+"_area"+".html" #le chemin du fichier area statistiques de superficie
					output=Rlyr.source().split("NDVI")[0]+ClipFolder+"/"+Rlyr.name()
					extent = Rlyr.extent()#extent=emprise
					xmin = extent.xMinimum()
					xmax = extent.xMaximum()
					ymin = extent.yMinimum()
					ymax = extent.yMaximum()
					if "NDVI" in Rlyr.name():#ne traiter que les fichiers dans le dossier NDVI
						ListDir=os.path.dirname(Rlyr.source()).split('/')#obtenir les repertoires dans lesqeuls se situe le fihcier : decouper le chemin d acces par le caractere /
						print ListDir
						raster_stat =processing.runalg('qgis:rasterlayerstatistics', str(Rlyr.source()), output_stat)#calculer les statistiques generales 
						raster_area =processing.runalg('grass7:r.surf.area',str(Rlyr.source()),1,2,"%f,%f,%f,%f" %(xmin, xmax, ymin, ymax),output_area,output)#calculer la superficie 

						if raster_stat['MEAN']!=0:#si moyennen != 0  donc il y a au moins une valeur !=0  dans la zone 
							NdviZone.append(Rlyr.name())#ajouter e fnom du fichier dans la liste NdviZone
							NdviMean.append(raster_stat['MEAN'])# ajouter la moyenne ede NDVI dans la zozne a la liste NdviMean
							NdviMax.append(raster_stat['MAX'])#ajouter la valeur max du NDVI dans la zone a la liste NdviMax
							NdviMin.append(raster_stat['MIN'])# ajouter la valeur min du NDVI dans la zone a la liste NdviMin
							NdviCell.append(raster_stat['COUNT']) #ajouter  nombre de pixels dans la zone a ala liste NdviCell
							NdviEcartType.append(raster_stat['STD_DEV']) # ajouter la valeur de l ecart type de NDVI dans la zone a la liste NdviEcartType
							NdviDate.append(ListDir[-3]) # ajouter la date de prise de photo a la liste NdviDate
							NdviScene.append(ListDir[-2])# ajouter l emprise  a  la liste NdviScene
							#print "Min : "+ str(raster_stat['MIN'])+" Max : "+ str(raster_stat['MAX'])+" Sum : "+ str(raster_stat['SUM'])+" Mean : "+ str(raster_stat['MEAN'])
				else :
					print "Fichier .tif non trouve"
	output_file = open("/".join (ListDir[0:-4])+"/"+"NDVI_"+str(ListDir[-4])+".csv", 'w')# definir le nom et le chemin du fichier de sortie
	output_file.write("Zone;Moyenne;Max;Min;Ecart_Type;Nombre_pixels;Date;Scene;Surface_scene(ha);Surface_total(ha);pourcentage_couverture"+"\n")#remplir le fichier : la premiere ligne : les titres des colonnes
	ListZone,ListArea=AreaImage()
	while p_s < len(ListZone):#parcourir les listes deja remplies 
		p=0
		while p < len(NdviZone):#remplir les colonnes du fichier avec les differents valeurs dans les differentes listes
			if NdviZone[p].split(ClipFolder_Terroir)[0]=="_"+ListZone[p_s]+"__NDVI":
				output_file.write(str(ListZone[p_s])+";"+str(NdviMean[p]).replace('.', ',')+";"+str(NdviMax[p]).replace('.', ',')+";"+str(NdviMin[p]).replace('.', ',')+";"+str(NdviEcartType[p]).replace('.', ',')+";"+str(NdviCell[p]).replace('.', ',')+";"+str(NdviDate[p]).replace('_', '/')+";"+str(NdviScene[p])+";"+str(NdviCell[p]*0.01).replace('.', ',')+";"+str(ListArea[p_s]).replace('.', ',')+";"+str((NdviCell[p]*0.01)*100/ListArea[p_s]).replace('.', ',')+"\n")
			p=p+1#passer a la ligne suivante 
		p_s=p_s+1
	output_file.close()#fermer l acces au fichier 
	print "fichier de sortie est cree"


#Finction area : fonction pour calculer les superfiecies des entitees dans le dossier Terroir (superficie avant d'enlever la partie nuageuse)
def AreaImage():
	ListArea=[]
	ListZone=[]
	area=0
	for Vsubdir, Vdirs, Vfiles in os.walk(Vrootdir):#parcourir le dossier Terroir
		for Vfile in Vfiles:
			Vfile,Vextension =os.path.splitext(os.path.join(Vsubdir,Vfile).replace("\\","/"))
			if Vextension == '.shp' :#selectionner que les fichiers Shp 
				VfileName = os.path.join(Vsubdir, Vfile).replace("\\","/")+".shp"#construire le chemin d acces au fichier
				if os.path.isfile(VfileName) :#veifier si fichier et non pas un repertoire
					VfileInfo = QFileInfo(VfileName)
					VbaseName = VfileInfo.baseName()
					Vlyr = QgsVectorLayer(VfileName, VbaseName,'ogr')#charger le fichier shp comme vecorLayer
					Vlyr.setCrs(crs_base)#definir le systeme de coordonnes
					feature = Vlyr.getFeatures()#recuperer toutes les entites dans le ficher dans une liste
					for f in feature:
						geom = f.geometry()#recuperer le geometrie de l entite
						area=area+geom.area()#calculer a superfice 
					ListZone.append(Vlyr.name())#ajouter le nom du  fichier vecteur a la liste  ListeZone
					surface= area*0.0001
					ListArea.append(surface)#ajouter la superficie du  fichier vecteur a la liste  ListeArea
					area=0#reinitialiser la valeur la variable area  a zero
				else :
					print "Fichier .jp2 non trouve"
	return ListZone ,ListArea

#Execution des fonctions
delete_files()
delete_mask_cloud()
polygonize_cloud()
No_Cloud_Polygone()
Clip_Cloud()
Clip_Image()
NDVI()
File_NDVI_v3()