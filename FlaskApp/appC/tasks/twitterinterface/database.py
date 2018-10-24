from flaskext.mysql import MySQL
from appC.tasks.twitterinterface import cluster as cl
from math import radians, cos, sin, asin, sqrt
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km
mysql = MySQL()
conn=None
cursor=None
def init(app):
	global cursor,conn,mysql
	print("initialized!!!!")
	mysql.init_app(app)
	conn = mysql.connect()
	cursor= conn.cursor()
	print(cursor)

def commit():
	global conn
	conn.commit()
def create():
    cursor.execute('create table user (id auto increment,lat numeric,lon numeric,resuceid varchar(20))')
    cursor.execute('create table ngo (id int auto increment,email varchar(20),name varchar(20),password varchar(20),lat numeric,lon numeric)')
    cursor.execute('create table ngocurr(id int, rescuelat number,rescuelon number,rescueid int)')

def insertngo(name,email,password,lat,lng):
    global cursor
    cursor.execute("INSERT INTO ngo (email,name,pass,lat,lon) VALUES(%s,%s,%s,%s,%s)",(_email,_name,_password,str(lat),str(lon)))

def insertuser(lat,lon):
	global cursor    
	cursor.execute("INSERT INTO user (lat,lon) VALUES(%s,%s)",(str(lat),str(lon)))
	checkusertable()

def insertngocurr(ids,rescuelat,rescuelon,rescueid):
    global cursor
    cursor.execute("SELECT COUNT(1) FROM ngo_saver WHERE rescue_id = {};".format(rescueid))
    if cursor.fetchone()[0]:
        return
    cursor.execute("INSERT INTO ngo_saver (id, rescue_lat, rescue_lon, rescue_id) VALUES(%s,%s,%s,%s)",(str(ids),str(rescuelat),str(rescuelon),str(rescueid)))
    
def insertrescuengo(idstr,resuceid):
    global cursor
    print(type(resuceid))
    print(type(idstr))
    cursor.execute("UPDATE user set rescue_id = {} where id = {}".format(int(resuceid),int(idstr)))

def delentryuser(idstr):
    global cursor
    cursor.execute('delete from user where id='+idstr)
    cursor.execute('delete from ngo_saver where rescueid='+idstr)
    #####
    """
    make ngo go after next relevent user
    """

    #######
def deleteentryngo(idstr):
    global cursor
    cursor.execute('delete from ngo where id='+idstr)
    

def getlatlongofuserandngo(username):
	global cursor	
	cursor.execute('select * from ngo where name=%s',username)
	data=cursor.fetchall()
	id=data[0][0]
	lat=data[0][4]
	lon=data[0][5]
	cursor.execute("select * from ngo where id="+str(id))
	data2=cursor.fetchall()
	curlat=float(data2[0][4])
	curlon=float(data2[0][5])
	min=haversine(lon,lat,curlat,curlon)	
	minlat=data[0][4]
	minlon=data[0][5]	
	for i in data2:
		print(type(i))
		dist=haversine(float(i[5]),float(i[4]),lon,lat)
		if dist<min:
			min=dist
			minlat=i[4]
			minlon=i[5]
	return float(minlat),float(minlon),float(lat),float(lon)
		
def updatelocngo(idstr,newlat,newlong):
    global cursor
    cursor.execute('update ngo set lat=%s where id=%d'+(newlat,idstr))
    cursor.execute('update ngo set lon=%s where id=%d'+(newlong,idstr))
    cursor.execute('select * from ngo_save where id='+idstr)
    people=cursor.fetchall()
    for p in people:
        dist=haversine(double(p[2]),double(p[1]),newlong,newlat)
        if dist<1:
            delentryuser(p[0])
def checkusertable():
    global cursor
    cursor.execute('select * from user where rescue_id=NULL')
    data=cursor.fetchall()
    if(len(data)>0):
        newdata=[]
        for i,d in enumerate(data):
            newdata.append(list(data[i]))
            print(type(newdata[i]))
            newdata[i][1]=float(d[1])
            newdata[i][2]=float(d[2])
        cursor.execute('select * from ngo')
        datango=cursor.fetchall()
        newdatango=[]
        for i,d in enumerate(datango):
            newdatango.append(list(datango[i]))
            newdatango[i][4]=float(d[4])
            newdatango[i][5]=float(d[5])
        cl.precluster(newdata,newdatango)
#aniket
