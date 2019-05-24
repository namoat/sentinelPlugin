# sentinelPlugin 
The project was created using Python in order to enable users to calculate agronimic indices like NDVI and NDII using Sentinel2 images
pour la premiere version du script , les repertoires doivent être organisés d'une certaine manière pour que le code fonctionne correctement:
* Un dossier Sentinel2: le dossier de travail qui doit contenir deux dossiers : 
  - Un dossier 'Terroir' qui contient les fichiers vecteurs qui delimte la zone d'étude , par exemple le délimitation des parcelles, les        regions, les communes etc. 
  - Un dossier '2017' par exemple: le dossier contient les images satellitaires Sentinel2. les images doivent etres regroupées premierement      par date, puis par sceène ou emprise (exemple: dans le dossier 2017 contient les dossier '02_05_2017' et '21_10_2017', dans chacun des      dossier, on doit trouver les emprises 31EUP, 31EUQ, ...)
  
 Le script, produit en sortie:
  - des images raster des indices calculés . par exemple des raster de NDVI, de NDII...
  - un fichier CSV qui resument les résultats obtenues en calculant pour chaque fichier vecteur et pour chaque date le min, max, moyenne,     ecart-type, surface scène, nombre de pixels, 
  
    
    
