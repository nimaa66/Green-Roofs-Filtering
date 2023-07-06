# Green-Roofs-Filtering
Automizing the process of identifying potential rooftops for intensive and extensive planting based on area and slope criteria and calculating the total area of suitable surfaces in each district of a city.
In this model, we have some prerequisites:
•	footprint and solar potential shapefile must contain fields of buildings’ ID and area.
•	District shapefile must contain a field explaining the name of each district
•	All the shapefiles should be pre-processed and clean. For example, duplicated buildings or null values should be dropped.
Loading the data in QGIS:
1.	Create a folder in a directory
2.	Load the shapefile
3.	Open the attributes table of each shapefile and write down the field of:
a.	Districts: 
i.	The field containing the name of each district
b.	Footprint: 
i.	The field containing the ID of each building
ii.	the field of area of each building
c.	solar potential:
i.	The field containing the ID of each building
ii.	the field of area of each section of the roof
Model setting:
1.	Building footprint shapefile
2.	District shapefiles
3.	Solar potential shapefile
4.	Area field of building footprint shapefile 
a.	Can be found in the attribute table of footprint
5.	Area field of Filtered shapefile (the same as area field of solar potential)
a.	Since the algorithm uses the solar potential shapefile to filter data, hence the fields’ names are the same as the solar potential shapefile.
6.	Area field of solar potential
a.	Can be found in the attribute table of solar potential
7.	Building ID Field of Filtered Shapefile (the same as buildings’ ID field of solar potential)
a.	Since the algorithm uses the solar potential shapefile to filter data, hence the fields’ names are the same as the solar potential shapefile.
8.	Building ID of solar potential 
9.	Districts name of statistics output (same as the field with district name of district shapefile)
10.	Field with Districts name
11.	Folder to save Filtered Shapefile
12.	Slope field of solar potential
Output shapefiles:
1.	“Proper buildings” which represents the area of each building where suitable for green roofs. In this output's attribute table, two shapefiles have been added. 
a.	A field with the same name as in the district shapefile (field on districts’ name) which contain the name of districts. 
b.	A field called “sum” is the total areas in each building (based on buildings ID) where are suitable for green roof.
2.	“final district shapefile” which shows the districts of the city with two new field coparing the original district shapefile.
a.	“Footprint_areasum” is the total area of existing buildings in a district.
b.	“ST_areasum” is total area in a district which is proper for green roof.
