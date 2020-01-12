import arcpy,sys
from arcpy import env
env.overwriteOutput = True

#Input must be in English
Workspace = sys.argv[1]
oriShp = sys.argv[2]
newShp = sys.argv[3]
env.workspace = Workspace
arcpy.MakeFeatureLayer_management(newShp,'new')
arcpy.MakeFeatureLayer_management(oriShp,'ori')

arcpy.AddField_management(oriShp,"MLEIold","DOUBLE")
arcpy.AddField_management(newShp,"MLEI","DOUBLE")
desc = arcpy.Describe(oriShp)
flds = desc.fields
index = 0
for fld in flds:
    if fld.name == "MLEI":
        index = 1
        break
if index == 1:
    oldcur = arcpy.da.UpdateCursor(oriShp,("MLEIold","MLEI"))
    for row in oldcur:
        row[0] = row[1]
        oldcur.updateRow(row)
    del oldcur
else:
    oldcur = arcpy.da.UpdateCursor(oriShp,"MLEIold")
    for row in oldcur:
        row[0] = 100
        oldcur.updateRow(row)
    del oldcur

cur = arcpy.da.UpdateCursor(newShp,"MLEI")
n = 0
buffer_dist = 50
for row in cur:
    SQL = '"FID" = %d'%n
    myselect = arcpy.SelectLayerByAttribute_management('new',"NEW_SELECTION",SQL)
    mybuffer = arcpy.Buffer_analysis(myselect,'buffer',buffer_dist,"OUTSIDE_ONLY")
    arcpy.CalculateField_management(mybuffer, 'area', 'float(!SHAPE.area!)',"PYTHON_9.3")
    buffer_area = 0.0
    buffer_cursor = arcpy.da.SearchCursor(mybuffer,("area"))
    for cursor in buffer_cursor:
        buffer_area = buffer_area + cursor[0]
    myintersect = arcpy.Intersect_analysis([mybuffer,oriShp],'intersect')
    arcpy.CalculateField_management(myintersect, 'area', 'float(!SHAPE.area!)',"PYTHON_9.3")
    cursors = arcpy.da.SearchCursor(myintersect,("MLEIold",'area'))
    myarea = 0.0
    for cursor in cursors:
        myarea = myarea + float(cursor[0])*float(cursor[1])
    row[0] = myarea / buffer_area
    cur.updateRow(row)
    n = n+1
    del myselect,mybuffer,myintersect,buffer_cursor,cursors

