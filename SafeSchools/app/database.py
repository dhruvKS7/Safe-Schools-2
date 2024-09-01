import sqlalchemy
from geopy.geocoders import Nominatim
from app import db

def register(username, password, firstname, lastname):
    exe = 'SELECT * FROM Users WHERE Username = "%s"' % username
    conn = db.connect()
    results = conn.execute(sqlalchemy.text(exe))
    conn.close()
    lister = []
    for result in results:
        lister.append(result)
    if len(lister) != 0:
        return 'Username already exists'
    try:
        exe = 'INSERT INTO Users VALUES ("%s", "%s", "%s", "%s")' % (username, password, firstname, lastname)
        conn = db.connect()
        conn.execute(sqlalchemy.text(exe))
        conn.commit()
        conn.close()
        return 'success'
    except:
        return 'Encountered registration error'

def login(username, password):
    exe = 'SELECT * FROM Users WHERE Username = "%s"' % username
    conn = db.connect()
    results = conn.execute(sqlalchemy.text(exe))
    conn.close()
    lister = []
    for result in results:
        lister.append(result)
    if len(lister) == 0:
        return 'Username does not exist'
    realpass = lister[0][1]
    if password == realpass:
        return 'success'
    else:
        return 'Invalid password'

def getSchools():
    exe = 'SELECT * FROM Schools'
    conn = db.connect()
    results = conn.execute(sqlalchemy.text(exe))
    conn.close()
    lister = []
    for result in results:
        lister.append(result)
    return lister

def searchByString(query):
    search = '%' + query + '%'
    exe = 'SELECT * FROM Schools WHERE SchoolName LIKE "%s"' % search
    conn = db.connect()
    results = conn.execute(sqlalchemy.text(exe))
    conn.close()
    lister = []
    for result in results:
        lister.append(result)
    return lister

def getProfile(username):
    exe = 'SELECT * FROM Users WHERE Username = "%s"' % username
    conn = db.connect()
    results = conn.execute(sqlalchemy.text(exe))
    conn.close()
    lister = []
    for result in results:
        lister.append(result)
    first = lister[0][2]
    last = lister[0][3]
    return first, last

def updateProfile(username, firstname, lastname):
    exe = 'UPDATE Users SET FirstName = "%s", LastName = "%s" WHERE Username = "%s"' % (firstname, lastname, username)
    conn = db.connect()
    conn.execute(sqlalchemy.text(exe))
    conn.commit()
    conn.close()
    return firstname, lastname

def getRatings(username):
    exe = 'SELECT SchoolID, SchoolName, SchoolType, Rating FROM Ratings NATURAL JOIN Schools WHERE Username = "%s"' % username
    conn = db.connect()
    results = conn.execute(sqlalchemy.text(exe))
    conn.close()
    lister = []
    for result in results:
        lister.append(result)
    return lister

def removeRating(username, schoolID):
    exe = 'DELETE FROM Ratings WHERE Username = "%s" AND SchoolID = %d' % (username, schoolID)
    conn = db.connect()
    conn.execute(sqlalchemy.text(exe))
    conn.commit()
    conn.close()
    return getRatings(username)

def addRating(username, schoolID, rating):
    exe = 'INSERT INTO Ratings (Username, SchoolID, Rating) VALUES ("%s", %d, %f)' % (username, schoolID, rating)
    conn = db.connect()
    conn.execute(sqlalchemy.text(exe))
    conn.commit()
    conn.close()
    return getRatings(username)

def ratingExists(username, schoolID):
    exe = 'SELECT * FROM Ratings WHERE Username = "%s" AND SchoolID = %d' % (username, schoolID)
    conn = db.connect()
    results = conn.execute(sqlalchemy.text(exe))
    conn.close()
    lister = []
    for result in results:
        lister.append(result)
    if len(lister) != 0:
        return True
    else:
        return False
    
def favoriteExists(username, schoolID):
    exe = 'SELECT * FROM Favorites WHERE Username = "%s" AND SchoolID = %d' % (username, schoolID)
    conn = db.connect()
    results = conn.execute(sqlalchemy.text(exe))
    conn.close()
    lister = []
    for result in results:
        lister.append(result)
    if len(lister) != 0:
        return True
    else:
        return False

def getFavorites(username):
    exe = 'SELECT SchoolID, SchoolName, SchoolType FROM Favorites NATURAL JOIN Schools WHERE Username = "%s"' % username
    conn = db.connect()
    results = conn.execute(sqlalchemy.text(exe))
    conn.close()
    lister = []
    for result in results:
        lister.append(result)
    return lister

def removeFavorite(username, schoolID):
    exe = 'DELETE FROM Favorites WHERE Username = "%s" AND SchoolID = %d' % (username, schoolID)
    conn = db.connect()
    conn.execute(sqlalchemy.text(exe))
    conn.commit()
    conn.close()
    return getFavorites(username)

def addFavorite(username, schoolID):
    exe = 'INSERT INTO Favorites VALUES ("%s", %d)' % (username, schoolID)
    conn = db.connect()
    conn.execute(sqlalchemy.text(exe))
    conn.commit()
    conn.close()
    return getFavorites(username)

def callProd(schoolID):
    exe = 'CALL getSchoolInfo(%d);' % int(schoolID)
    conn = db.connect()
    results = conn.execute(sqlalchemy.text(exe))
    conn.close()
    lister = []
    for result in results:
        lister.append(result)
    print(lister)
    return lister[0][0], lister[0][1]

def schoolInfo(schoolID):
    safety, rating = callProd(schoolID)
    safety = 100 - (safety * 100)
    exe = 'SELECT * FROM Schools WHERE SchoolID = %d' % schoolID
    conn = db.connect()
    results = conn.execute(sqlalchemy.text(exe))
    conn.close()
    lister = []
    for result in results:
        lister.append(result)
    name = lister[0][1]
    schooltype = lister[0][2]
    lon = lister[0][3]
    lat = lister[0][4]
    area = int(lister[0][5])
    exe = 'SELECT LocalPolicePhone FROM PoliceAreas WHERE Area = %d' % area
    conn = db.connect()
    results = conn.execute(sqlalchemy.text(exe))
    conn.close()
    lister = []
    for result in results:
        lister.append(result)
    phone = lister[0][0]
    geolocator = Nominatim(user_agent="SafeSchools")
    coords = str(lat) + ", " + str(lon)
    location = geolocator.reverse(coords)
    return schoolID, name, schooltype, location.address, safety, rating, phone

def createProd():
    prod = '''
CREATE PROCEDURE getSchoolInfo (IN givenID INT)
BEGIN
	DECLARE done INT DEFAULT 0;
    DECLARE safety DECIMAL(7, 2);
    DECLARE getaveragerating DECIMAL(7, 2);
	DECLARE crimeWeight DECIMAL(2,1);
	DECLARE weaponWeight DECIMAL(2,1);
	DECLARE count INT;
    DECLARE weapon VARCHAR(50);
	DECLARE crime VARCHAR(100);
    DECLARE tempname VARCHAR(100);
	DECLARE cur CURSOR FOR SELECT COUNT(*), WeaponUsed, CrimeDescription FROM Crimes cr JOIN CrimeCodes co ON cr.CrimeCode = co.CrimeCode WHERE cr.FileID IN (SELECT FileID FROM Suffer WHERE SchoolID = givenID) GROUP BY WeaponUsed, CrimeDescription;
    DECLARE cur2 CURSOR FOR SELECT AVG(Rating), SchoolName FROM (SELECT * FROM Ratings r NATURAL JOIN Schools s WHERE s.SchoolID = givenID) AS CurrSchool GROUP BY SchoolID;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done=1;
    SET safety = 0;
	OPEN cur;
	REPEAT
		FETCH cur INTO count, weapon, crime;
        SET crimeWeight = CASE WHEN crime LIKE '%RAPE%' OR crime LIKE '%BOMB%' OR crime LIKE '%CHILD%' OR crime LIKE '%SEX%' OR crime LIKE '%ING%' OR crime LIKE '%TER%'OR crime LIKE '%AS%'OR crime LIKE '%TER%' OR crime = 'CRIMINAL HOMICIDE' THEN 1 ELSE 0.7 END;
        SET weaponWeight = CASE WHEN weapon LIKE '%RIFLE%' OR weapon = 'EXPLOXIVE DEVICE' OR weapon = 'CAUSTIC CHEMICAL/POISON' OR weapon = 'ASSAULT WEAPON/UZI/AK47/ETC' THEN 1 ELSE 0.7 END;
        SET safety = safety + (crimeWeight * weaponWeight * count);
	UNTIL done
	END REPEAT;
	CLOSE cur;
    SET done = 0;
    OPEN cur2;
    REPEAT
        FETCH cur2 INTO getaveragerating, tempname;
    UNTIL done
    END REPEAT;
    CLOSE cur2;

    SET safety = safety / 4249;

	SELECT safety, getaveragerating;
END;
'''
    conn = db.connect()
    conn.execute(sqlalchemy.text(prod))
    conn.close()
    return 'success'

def createTrigger():
    trigger = '''
CREATE TRIGGER ratingsfavoritesrelation
    AFTER INSERT ON Ratings
    FOR EACH ROW
    BEGIN
        SET @check = (SELECT SchoolID FROM Favorites f WHERE f.Username = new.Username AND f.SchoolID = new.SchoolID);
        IF @check IS NULL THEN INSERT INTO Favorites (Username, SchoolID) VALUES (new.Username, new.SchoolID);
        END IF;
    END;
'''
    conn = db.connect()
    conn.execute(sqlalchemy.text(trigger))
    conn.close()
    return 'success'