"""Shared editorial data. Shop prices/formats are explicit examples, not offers."""
MENU_GROUPS={'wochenkarte':'Wochenkarte','klassiker':'Unsere Klassiker','weisswein':'Weißwein','rotwein':'Rotwein'}
RAW_MENU={
'wochenkarte':[
('Coca de espinacas a la catalana con olivada','Blätterteiggebäck mit Spinat nach katalanischer Art',650),
('Croquetas caseras','Tageskroketten',690),
('Timbal de remolacha asada, queso de cabra y pesto de rúcula','Gebackene Rote Bete, Ziegenkäse, Rucolapesto, Cashewkerne und Limette',920),
('Carrilleras de ternera','Langsam geschmorte Rinderbäckchen mit cremigem Kartoffel-Parmentier',1350),
('Conejo al horno con mostaza','Kaninchen aus dem Ofen mit Senf-Zitrus-Soße und Hummus',1050),
('Pulpo a la gallega','Oktopus nach galizischer Art mit Kartoffeln, Paprikapulver und Olivenöl',1590),
('Buñuelos de maruca con salsa de pimiento asado','Lengfisch-Windbeutel mit gerösteter Paprika',1250),
('Arroz de rebozuelos con alcachofas','Paella mit Pfifferlingen, Artischocken und frischen Kräutern',1590),
('Arroz de papada al vermút','Paella mit Schweinekinn und Wermutreduktion',1590),
('Gambas al ajillo','Garnelen in Knoblauch',1390),
('Chipirones frescos a la plancha','Frische kleine Tintenfische vom Grill · kleine Portion',990),
('Chipirones frescos a la plancha','Frische kleine Tintenfische vom Grill · große Portion',2290),
('Argentinisches Entrecôte','Mit Kartoffeln und Salat',2790)],
'klassiker':[
('Ensalada mixta','Gemischter Salat · kleine Portion',790),
('Tortilla de patatas','Spanisches Kartoffelomelett',590),
('Queso de cabra, miel con chili, cebolla caramelizada','Ziegenkäsebällchen, karamellisierte Zwiebeln und Chili-Honig',590),
('Patatas bravas','Oder All i Oli',620),('Patatas bravas und All i Oli','Mit beiden Soßen',620),
('Ciruelas con bacon','Pflaumen im Speckmantel',590),('Chorizo picante frito','Gebratene scharfe Paprikawurst',680),
('Olivas','',520),('Getrocknete Tomaten oder Kapern','',640),
('Boquerones en vinagre','Sardellenfilets, in Olivenöl und Knoblauch eingelegt',760),
('Jamón Serrano','Serrano-Schinken',850),('Plato de quesos españoles','Spanische Käseplatte · klein',950),
('Plato mixto','Schinken, Wurst, Käse und Oliven · klein',990),('Plato mixto','Schinken, Wurst, Käse und Oliven · groß',2490),
('Crema catalana','Hausgemachtes Dessert',590),('Postre de la semana','Dessert der Woche',590)],
'weisswein':[
('Bujanda Blanco 2019 · D.O. Rioja','0,2 l · Viura',680),
('Blanco Nieva Sauvignon Blanc 2019 · D.O. Rueda','0,2 l · Sauvignon Blanc',720),
('Vanidade 2019 · D.O. Rías Baixas','0,2 l · Albariño',820)],
'rotwein':[
('Egiarte Crianza 2016 · D.O. Navarra','0,2 l · Tempranillo, Merlot, Cabernet Sauvignon · 12 Monate Barrique',740),
('Lezaun Tempranillo 2019 · D.O. Navarra','0,2 l · Tempranillo',680),
('Terrae Finca Vasallo 2019 · Bajo Aragón','0,2 l · Garnacha',720),
('Nuestro 2018 · D.O. Ribera del Duero','0,2 l · Tempranillo · 8 Monate französische Eichenfässer',990)]}
MENU=[{'id':f'{cat}-{i+1}','category':cat,'name':name,'description':desc,'price_cents':price,'active':True} for cat,rows in RAW_MENU.items() for i,(name,desc,price) in enumerate(rows)]
PRODUCTS=[
{'id':'mejillones','name':'Mejillones en escabeche','subtitle':'Miesmuscheln mit Apfelweinessig','brand':'Agromar','category':'conservas','price_cents':1290,'amount':110,'unit':'g','pack':'110 g','description':'Eine Konserven-Referenz für die geplante Auswahl. Produktetikett und tatsächlich gelieferte Charge werden vor Verkaufsstart geprüft.','source':'https://www.agromar.es/tienda/','pickup':False},
{'id':'caviar-de-oricios','name':'Caviar de oricios','subtitle':'Seeigelrogen aus Asturien','brand':'Agromar','category':'conservas','price_cents':2690,'amount':68,'unit':'g','pack':'68 g','description':'Asturische Spezialität als Sortimentsvorschlag. Zutaten, Allergene und Nährwerte müssen anhand des endgültigen Etiketts ergänzt werden.','source':'https://www.agromar.es/tienda/','pickup':False},
{'id':'chorizo-asturiano','name':'Chorizo asturiano','subtitle':'Asturische Paprikawurst','brand':'Vallina','category':'embutidos','price_cents':690,'amount':250,'unit':'g','pack':'250 g','description':'Referenzprodukt zur gekühlten Aufbewahrung und zum Durchgaren. Im Entwurf nur Abholung; kein ungekühlter Paketversand.','source':'https://puxa.es/chorizo-extra-asturiano/35-chorizo-extra-paq-250-g.html','pickup':True},
{'id':'cecina-loncheada','name':'Cecina loncheada','subtitle':'Rinderschinken, fein aufgeschnitten','brand':'Cecinas Pablo','category':'embutidos','price_cents':890,'amount':100,'unit':'g','pack':'100 g','description':'Kleine Packung als Sortimentsvorschlag. Bis zur Prüfung von Etikett, Lagerung und Versandbedingungen ausschließlich Abholung.','source':'https://www.cecinaspablo.com/','pickup':True}]
WINES=[
('bujanda-blanco','Bujanda Blanco','Rioja · Viura','weisswein',1290,7350,'2019'),
('blanco-nieva','Blanco Nieva Sauvignon Blanc','Rueda · Sauvignon Blanc','weisswein',1590,9090,'2019'),
('vanidade','Vanidade','Rías Baixas · Albariño','weisswein',1790,10200,'2019'),
('egiarte-crianza','Egiarte Crianza','Navarra · Tempranillo, Merlot, Cabernet Sauvignon','rotwein',1690,9600,'2016'),
('lezaun-tempranillo','Lezaun Tempranillo','Navarra · Tempranillo','rotwein',1290,7350,'2019'),
('terrae-finca-vasallo','Terrae Finca Vasallo','Bajo Aragón · Garnacha','rotwein',1390,7900,'2019'),
('nuestro','Nuestro','Ribera del Duero · Tempranillo','rotwein',2190,12490,'2018')]
for slug,name,region,cat,price,case,year in WINES:
 PRODUCTS.append({'id':slug,'name':name,'subtitle':region,'brand':'Aus unserer Weinkarte','category':cat,'price_cents':price,'case_price_cents':case,'case_count':6,'amount':750,'unit':'ml','pack':'0,75 l','description':f'Auswahl aus der Restaurantkarte. Dort genannter Jahrgang: {year}; lieferbarer Jahrgang und Etikett noch nicht bestätigt. Flasche und 6er-Karton sind Planungsformate mit Beispielpreisen.','source':'https://vineriaytapas.de/','pickup':False,'menu_year':year})
for p in PRODUCTS:
 p.setdefault('case_price_cents',0);p.setdefault('case_count',0);p['stock']=120;p['active']=True;p['labels_verified']=False;p['image']='wine-art.webp' if p['category'] in ['weisswein','rotwein'] else 'collage.webp'
SETTINGS={'shipping_standard_cents':690,'shipping_wine_cents':990,'wine_per_box':6,'delivery_text':'3–5 Werktage · unverbindliche Planung','mode':'review'}
MAP='https://www.google.com/maps/place/Restaurant+Vineria+Del+Este/@52.5186994,13.464087,92m/data=!3m2!1e3!5s0x47a84e6198e1e723:0xedc45fa97ad4c2ae!4m15!1m8!3m7!1s0x47a84e61996e490d:0xa39a3db28d27a3d6!2sBänschstraße+41,+10247+Berlin-Bezirk+Friedrichshain-Kreuzberg!3b1!8m2!3d52.5187399!4d13.4644068!16s%2Fg%2F11c239j60n!3m5!1s0x47a84e61989fede3:0x991b34f6490b7bf4!8m2!3d52.5185729!4d13.4642961!16s%2Fg%2F1thkqqrb?entry=ttu&g_ep=EgoyMDI2MDkxNi4wIKXMDSoASAFQAw%3D%3D'
