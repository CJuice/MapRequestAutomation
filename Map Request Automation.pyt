import os, arcpy, re, sys, string
'''This Python toolbox was setup and usable on 6/8/16 by CJuice on GitHub.'''
'''It took the two map request automation steps (step1 and step2) and pulled them from the old toolbox style and revised the code to work in the new Python Toolbox style'''

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Step1, Step2, Floorplan]


class Step1(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 1 of 2 - Map Request Process"
        self.description = "Step 1 of the Map Request Process. Use this model to create the project folders, geodatabase, and to copy the template map document. It should be run at the beginning of each project rather than creating new folders and geodatabases one item at a time. A template mxd and gdb are stored for copying. Revise the root path with a change in Fiscal Year."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(displayName="CRF Number",
                                 name="CustomerRequestFormNumber",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input",)
        param1 = arcpy.Parameter(displayName="Map Requesters Name (No Spaces Between Names)",
                                 name="RequestersFirstAndLastNames",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")
        param2 = arcpy.Parameter(displayName="Fiscal Year (FY20XX) Folder",
                                 name="RootFYFolderPath",
                                 datatype="DEFolder",
                                 parameterType="Required",
                                 direction="Input")
        param2.value = "\\\\tceq4apmgisdata\\giswrk\\IRGIS\\Mapping\\AGProjects\\FY2017"
        params = [param0, param1, param2]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        '''Logging functionality for troubleshooting'''
        doLogging = False;
        if(doLogging):
            arcpy.AddWarning("Logging ENABLED")

        ''' Store the parameters as strings'''
        strCRFNumber = parameters[0].valueAsText
        strRequestersNameNoSpaces = parameters[1].valueAsText
        strFYYearFolder = parameters[2].valueAsText
        
        ''' Create variables holding the folder name and full path for the project'''
        strProjectFolderName = strCRFNumber + "_" + strRequestersNameNoSpaces
        strFullProjectPath = os.path.join(strFYYearFolder,strProjectFolderName)
        if strFYYearFolder == '#' or not strFYYearFolder:
            strFYYearFolder = "\\\\tceq4apmgisdata\\giswrk\\IRGIS\\Mapping\\AGProjects\\FY2017" # provide a default value if unspecified
        if(doLogging):
            arcpy.AddWarning("CRFNumber=" + strCRFNumber + "; Requesters Name= " + strRequestersNameNoSpaces + "; FY Year Folder= " + strFYYearFolder)
            arcpy.AddWarning(strProjectFolderName)
            
        ''' Store location of template mxd and gdb, and prep the names that the templates will become once they are moved to the project folder'''
        strTemplate_mxd = "\\\\tceq4apmgisdata\\giswrk\\IRGIS\\Mapping\\AGprojects\\Project_FolderStructure_Model\\PreModelSetupFiles\\Template.mxd"
        strProjectMXDName = strCRFNumber + ".mxd"
        strCopiedMXD = os.path.join(strFullProjectPath,strProjectMXDName)
        strTemplateGDB = "\\\\tceq4apmgisdata\\giswrk\\IRGIS\\Mapping\\AGProjects\\Project_FolderStructure_Model\\PreModelSetupFiles\\Template.gdb"
        strProjectGDBName = strCRFNumber + ".gdb"
        strProjectGDB = os.path.join(strFullProjectPath,strProjectGDBName)
        if(doLogging):
            arcpy.AddWarning("template mxd: " + strTemplate_mxd)
            arcpy.AddWarning("copied mxd: " + strCopiedMXD)
            arcpy.AddWarning("template gdb: " + strTemplateGDB)
            arcpy.AddWarning("Project gdb: " + strProjectGDB)

        ''' Process: Check for Spaces in Requester Name'''
        try:
            if " " in strRequestersNameNoSpaces:
                exit()               
            else:
                pass
        except:
            arcpy.AddError("The requesters name contains spaces. Please reenter the name.")
            sys.exit()
            

        '''Check if a Folder Exists; Imported the next section from a script for checking the existence of the folder'''
        # The following message will display the entire path, so that you(cartographer) can check result
        arcpy.AddWarning("\nThe project path is " + strFullProjectPath + "\n")

        ''' Statement to check the existence of the folder'''
        try:
            if arcpy.Exists(strFullProjectPath):
                exit()
            else:
                arcpy.AddWarning("\nThe project folder has been created.\n")
        except:
            arcpy.AddError("\nThe folder appears to exist already. Check the CRF# and Requester Name that you entered, and check to see if the folder has been created already. The folder could have been created by a teammate.\n")
            sys.exit()

        '''Create project folder with all of the standard content: mxd, gdb, Docs folder'''
        arcpy.CreateFolder_management(strFYYearFolder, strProjectFolderName)
        arcpy.CreateFolder_management(strFullProjectPath, "Docs")
        arcpy.Copy_management(strTemplate_mxd, strCopiedMXD, "MapDocument")
        try:
            arcpy.Copy_management(strTemplateGDB, strProjectGDB, "Workspace")
        except:
            arcpy.AddWarning("The .gdb copy process failed, but it isn't your fault. It's ESRI. All is good. Go forth and map.")
            sys.exit()

        return

class Step2(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 2 of 2 - Map Request Process"
        self.description = "Step 2 of the Map Request Process. This step requires the user to provide the CRF ticket number (6-digit) and the requesters name <b>without</b> spaces (eg JohnDoe)."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(displayName="Project Folder (CRFNumber_RequesterName)",
                                 name="projectFolder",
                                 datatype="DEFolder",
                                 parameterType="Required",
                                 direction="Input")
        param1 = arcpy.Parameter(displayName="Did you save the formatted request email to the project Docs folder as a text file?",
                                 name="emailSaved",
                                 datatype="GPBoolean",
                                 parameterType="Required",
                                 direction="Input")
        params = [param0, param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):

        ###################################
        # Script:  GISRequest_AutomationTest.py
        # Author:  CJuice on GitHub
        # Date Created:  09/11/2015
        # Python 2.7, ArcGIS 10.3
        # Purpose:  Grab items from the GIS Request emails and stick them into the map template to save time. This script
        # is an expansion of the original Step 2 script. This script expands to deal with the emails generated by the new customer
        # request form web pages (Legal, Basic, Reprint).
        #Inputs:
        '''
            0 - Workspace (Required), data type = workspace
        '''
        # Outputs:  Outputs an altered mxd
        # Modifications:  7/30/15: cleaned up old comments, relabeled variables to indicate type (str, lst), filled out the delete statements \
        #           at the end. CJS
        #       7/31/15: Changed script so that different email text file names are acceptable as long as "GIS Request" is in the file name. \
        #           Deleted old code from when the script was designed to be run as a script, rather than a tool in ArcGIS. Added code to grab \
        #           all lines of the "Description" in the email, instead of just the first line. CJS
        #       8/3/15: General cleanup/streamlining. Hardcoded a list of Texas county names so that the user entry can be checked. I learned \
        #           through an ESRI GeoNet forum discussion (that I initiated) that I would have to program in ArcObjects to set the default
        #           geodatabase for each map document. It isn't currently possible through arcpy. CJS
        #       9/9/15: The title and another element were being clipped by one character, at the end of the string. I revised the code
        #           from [X:-Z] to [X:]. It should work the same since it is paired with .split()
        #       9/17/15 - 9/30/15: Revisions to handle data from the new web form.
        #       10/6/15: When the Basic Map Request does not focus on a single county a definition query cannot be built. Added if statement checking length \
        #           of the strCounty variable. When empty operations are skipped so they do not hang. Also added more doLogging checks for troubleshooting.
        #       01/28/16: Revised to have a user defined point (based on Lat/Long in web form) added to map to help locate the facility when the map is initially opened. \
        #           Also added a few notes and cleaned up a few items.
        #       02/05/16: Removed the TX outline and Counties from the list of layers to be added to the mxd. They are already in the template mxd's in a symbolized format \
        #           and don't need to be added again. They are default layers. If the user unchecks them in the default layers list nothing will change. Revised file path to \
        #           reference root rather than drive letter
        #       06/08/2016: Successfully moved and revised step 1 and step 2 from freestanding script tools to become "tools" in the new Python toolbox style. These will now be buttons in arcmap
        ###################################
        print "*"*30 + "\n"

        import os, arcpy, re, sys, string
        # from arcpy import env

        # Turn ON (True) or OFF (False) when needing to troubleshoot
        doLogging = False

        # The folder and mxd and gdb must exist. The project setup tool (the Step 1 model) does this. The map request email must be saved 
        # as a text file and it takes the default name "FW GIS Request.txt" (since it's forwarded to Conrad from Paul. 10/2/15 comes into GISMail now.). You have to manually \
        # save it each time.
        # We need the CRF number and the map requesters name so we can build the path to the folder. We need the county name for queries and zooming.
        # Define the root path that the mxd and all other project files will share
        strRootPath = parameters[0].valueAsText               # In the tool, the cartographer needs to pick the workspace folder
        lstSep = strRootPath.split("\\")                        # Split the path apart so it stores in a list
        if(doLogging):
            arcpy.AddError(lstSep)
        lstSep2 = lstSep[-1].split("_")                         # Grab the last item in the list (which is the file name) and split it at the underscore so that the CRF number and requesters name are separated
        if(doLogging):
            arcpy.AddError(lstSep2)
        strCRF_num = lstSep2[0]                                 # Store the CRF number
        strRequester = lstSep2[1]                               # Store the requesters name

        # A hard coded list of Texas County names taken from the TxDOT Counties layer. To provide a way to check the user email input value for County accuracy.
        lstTexasCounties = [u'Anderson', u'Andrews', u'Angelina', u'Aransas', u'Archer', u'Armstrong', u'Atascosa', u'Austin', u'Bailey', \
                            u'Bandera', u'Bastrop', u'Baylor', u'Bee', u'Bell', u'Bexar', u'Blanco', u'Borden', u'Bosque', u'Bowie', u'Brazoria',\
                            u'Brazos', u'Brewster', u'Briscoe', u'Brooks', u'Brown', u'Burleson', u'Burnet', u'Caldwell', u'Calhoun', u'Callahan',\
                            u'Cameron', u'Camp', u'Carson', u'Cass', u'Castro', u'Chambers', u'Cherokee', u'Childress', u'Clay', u'Cochran', u'Coke',\
                            u'Coleman', u'Collin', u'Collingsworth', u'Colorado', u'Comal', u'Comanche', u'Concho', u'Cooke', u'Coryell', u'Cottle',\
                            u'Crane', u'Crockett', u'Crosby', u'Culberson', u'Dallam', u'Dallas', u'Dawson', u'DeWitt', u'Deaf Smith', u'Delta',\
                            u'Denton', u'Dickens', u'Dimmit', u'Donley', u'Duval', u'Eastland', u'Ector', u'Edwards', u'El Paso', u'Ellis', u'Erath',\
                            u'Falls', u'Fannin', u'Fayette', u'Fisher', u'Floyd', u'Foard', u'Fort Bend', u'Franklin', u'Freestone', u'Frio',\
                            u'Gaines', u'Galveston', u'Garza', u'Gillespie', u'Glasscock', u'Goliad', u'Gonzales', u'Gray', u'Grayson', u'Gregg',\
                            u'Grimes', u'Guadalupe', u'Hale', u'Hall', u'Hamilton', u'Hansford', u'Hardeman', u'Hardin', u'Harris', u'Harrison',\
                            u'Hartley', u'Haskell', u'Hays', u'Hemphill', u'Henderson', u'Hidalgo', u'Hill', u'Hockley', u'Hood', u'Hopkins',\
                            u'Houston', u'Howard', u'Hudspeth', u'Hunt', u'Hutchinson', u'Irion', u'Jack', u'Jackson', u'Jasper', u'Jeff Davis',\
                            u'Jefferson', u'Jim Hogg', u'Jim Wells', u'Johnson', u'Jones', u'Karnes', u'Kaufman', u'Kendall', u'Kenedy', u'Kent',\
                            u'Kerr', u'Kimble', u'King', u'Kinney', u'Kleberg', u'Knox', u'La Salle', u'Lamar', u'Lamb', u'Lampasas', u'Lavaca',\
                            u'Lee', u'Leon', u'Liberty', u'Limestone', u'Lipscomb', u'Live Oak', u'Llano', u'Loving', u'Lubbock', u'Lynn',\
                            u'Madison', u'Marion', u'Martin', u'Mason', u'Matagorda', u'Maverick', u'McCulloch', u'McLennan', u'McMullen',\
                            u'Medina', u'Menard', u'Midland', u'Milam', u'Mills', u'Mitchell', u'Montague', u'Montgomery', u'Moore', u'Morris',\
                            u'Motley', u'Nacogdoches', u'Navarro', u'Newton', u'Nolan', u'Nueces', u'Ochiltree', u'Oldham', u'Orange',\
                            u'Palo Pinto', u'Panola', u'Parker', u'Parmer', u'Pecos', u'Polk', u'Potter', u'Presidio', u'Rains', u'Randall',\
                            u'Reagan', u'Real', u'Red River', u'Reeves', u'Refugio', u'Roberts', u'Robertson', u'Rockwall', u'Runnels',\
                            u'Rusk', u'Sabine', u'San Augustine', u'San Jacinto', u'San Patricio', u'San Saba', u'Schleicher', u'Scurry',\
                            u'Shackelford', u'Shelby', u'Sherman', u'Smith', u'Somervell', u'Starr', u'Stephens', u'Sterling', u'Stonewall',\
                            u'Sutton', u'Swisher', u'Tarrant', u'Taylor', u'Terrell', u'Terry', u'Throckmorton', u'Titus', u'Tom Green',\
                            u'Travis', u'Trinity', u'Tyler', u'Upshur', u'Upton', u'Uvalde', u'Val Verde', u'Van Zandt', u'Victoria', u'Walker',\
                            u'Waller', u'Ward', u'Washington', u'Webb', u'Wharton', u'Wheeler', u'Wichita', u'Wilbarger', u'Willacy', u'Williamson',\
                            u'Wilson', u'Winkler', u'Wise', u'Wood', u'Yoakum', u'Young', u'Zapata', u'Zavala']

        # When the email is saved as a .txt file in the Docs folder it will take a different form based on \
        # who is saving it. (old)Since Conrad gets the email bounced from Paul the filename is FW GIS Request.txt . \
        # When Paul saves it is just GIS Request.txt . This next piece gets around the variations in the file name.\
        # Emails are now sent to GISMail (10/2/15). code still applicable
        try:
            strTestingEmailPath = strRootPath + "\\" + "Docs"
            for (dirname, dirs, files) in os.walk(strTestingEmailPath):
        ##        print dirname, dirs, files
                for filename in files:
                    if (filename.endswith(".txt")) and ("GIS Request" in filename):
                        filename = os.path.join(dirname, filename)
                        strEmailPath = filename
        except:
            arcpy.AddWarning("The email .txt file doesn't exist or does not contain the string \"GIS Request\" . Process terminated.")
            sys.exit()

        # Grab items from the map request email. Store them so we can put them in the mxd later on.
        try:
            femail = open(strEmailPath)
            arcpy.AddMessage("The email file has opened and is currently being examined.")
        except:
            arcpy.AddWarning("The email file did not open successfully. Process terminated.")
            sys.exit()

        # Establish the variables that I'll use to store information
        strRequestType = ""                                     # for Legal, Other, or Reprint
        strMapRequester = ""                                    # Store the map requesters name
        strPhone = ""                                           # store the phone number
        strTitle = "Empty Title"                                # There could be a case where the requester didn't put a title
        strSubtitle = ""                                        # common to see a request with no subtitle
        strDescription = ""                                     # preps a variable to store the Description text
        strMapSize = ""                                         # Determines the size of the map template to use, for those sizes in the list on the form page. Alternate sizes are dealt with by hand
        strAltMapSize = ""                                      # store the alternate map size
        strCounty = ""                                          # to store the county name

                # Layer variables, either OFF:False or ON:True

        strAirports = "off"
        strAirSites = "off"
        strBrownfields = "off"
        strCCNsewer = "off"
        strCCNwater = "off"
        strCities = "off"
        strDryCleaners = "off"
        strEdwardsAquiferRegulatoryArea = "off"
        strFaults = "off"
        strGroundwaterConservationDistricts = "off"
        strIHWfacilities = "off"
        strInjectionWells = "off"
        strMajorAquifer = "off"
        strMinorAquifer = "off"
        strMSDpoints = "off"
        strMSDpolygons = "off"
        strMSWlandfills = "off"
        strPSTpoints = "off"
        ##strPublicWaterSupply = "off"              # Multiple layer options within PWS. Address later on if people start requesting this data.
        strRailRoads = "off"
        strRiverBasins = "off"
        strRoads = "off"
        strRockUnits = "off"
        strSatelliteImagery = "off"
        strSoils = "off"
        strSuperfundSites = "off"
        ##strSurfaceWater = "off"                   # Multiple layer options with SW. Address later on if people start requesting this data.
        strTCEQregionalAreas = "off"
        strTCEQregions = "off"
        strTEAschools = "off"
        strTexasCounties = "off"
        strTexasOutline = "off"
        strTLCDistrictsCongress = "off"
        strTLCDistrictsHouse = "off"
        strTLCDistrictsSenate = "off"
        strWasteWaterOutfalls = "off"
        strWaterbody = "off"
        strWatercourse = "off"
        strWaterDistricts = "off"
        strWatershedsHUC8 = "off"
        strWatershedsHUC10 = "off"
        strWatershedsHUC12 = "off"

        floLatitude = 0.000000
        floLongitude = -0.000000

        strLinearDistance = ""
        strLinearDistanceFeature = ""
        floLinearDistanceValue = 0.0
        strLinearUnits = ""

        strRadialBuffer = ""
        strRadialDistanceFeature = ""
        floRadialDistanceValue = 0.0
        strRadialUnits = ""

        # Below are variables of interest (usable for manipulation) that store all of the email line intro's. For example "Name:" and "Map Title:" and "Roads:"
        str_Subject = "Subject:"

            # Contact Information
        str_Name = "Name:"
        str_Phone = "Phone:"
        str_Email = "Email:"

            # Map Details
        str_MapTitle = "Map Title:"
        str_Subtitle = "Map Subtitle:"
        str_MapSize = "Map Size:"
        str_AltMapSize = "Alternate Map Size:"  # Will probably use this to store the alternate size so that I send a flag to alert me to a special request
        str_County = "County:"
        str_Latitude = "Latitude:"
        str_Longitude = "Longitude:"
        str_CircDistNeed = "Circular Distance Needed:"
        str_CircDist = "Circular Distance:"
        str_CircDistUnits = "Circular Distance Units:"
        str_CircDistFeature = "Circular Distance Feature:"
        str_LinDistNeed = "Linear Distance Needed:"
        str_LinDist = "Linear Distance:"
        str_LinDistUnits = "Linear Distance Units:"
        str_LinDistFeature = "Linear Distance Feature:"
        str_SatImgBgrnd = "Satellite Image Background:"
        str_TXCounties = "Texas Counties:"
        str_Roads = "Roads:"
        str_Watercourses = "Watercourses:"
        str_Waterbodies = "Waterbodies:"
        str_WWOutfalls = "WW Outfalls:"
        str_Cities = "Cities:"
        str_TXOutline = "Texas Outline:"
        str_TCEQRegions = "TCEQ Regions:"
        str_TCEQRegionalAreas = "TCEQ Regional Areas:"
        str_AirSites = "Air Sites:"
        str_Brownfields = "Brownfields:"
        str_DryCleaners = "Dry Cleaners:"
        str_IHWFacilities = "IHW Facilities:"
        str_InjectionWells = "Injection Wells:"
        str_MSDPoints = "MSD Points:"
        str_MSDPolygons = "MSD Polygons:"
        str_MSWLandfills = "MSW Landfills:"
        str_PSTPoints = "PST Points:"
        str_SuperfundSites = "Superfund Sites:"
        str_CCNSewer = "CCN Sewer:"
        str_CCNWater = "CCN Water:"
        str_EdwardsAquiferRegulatoryArea = "Edwards Aquifer Regulatory Area:"
        str_GCDs = "GCDs:"
        ##str_PWSData = "PWS Data:"
        ##str_SWData = "SW Data:"
        str_WaterDistricts = "Water Districts:"
        str_MajorAquifers = "Major Aquifers:"
        str_MinorAquifers = "Minor Aquifers:"
        str_RiverBasins = "River Basins:"
        str_WatershedsHUC8 = "Watersheds (HUC 8):"
        str_WatershedsHUC10 = "Watersheds (HUC 10):"
        str_WatershedsHUC12 = "Watersheds (HUC 12):"
        str_Soils = "Soils:"
        str_Faults = "Faults:"
        str_RockUnits = "Rock Units:"
        str_Airports = "Airports:"
        str_RailRoads = "Railroads:"
        str_TEASchools = "TEA Schools:"
        str_TLCDistrictsCongress = "TLC Congressional Districts:"
        str_TLCDistrictsHouse = "TLC House Districts:"
        str_TLCDistrictsSenate = "TLC Senate Districts:"

            # Description
        str_Description = "Description:"

        # added for the part of the script that grabs all of the Description lines
        count = 0
        lstIndex = []

        # FUTURE: defining function to accept each line of the email, identify which variable will be manipulated based on the line content, grab the value of the variable from the line, and assign it to the variable
        ##def lineCheck(input, input2):
        ##    if input.startswith(input) and len(line[len(input):]) > 0:
        ##        input2 = line[len(input):].strip()

        # Read the lines in the email, grab values, assign to variable
        for line in femail:
            line = line.strip()
            
            if len(line) > 0:
                if doLogging:
                    arcpy.AddMessage("(log) " + line)
                lstIndex.append((count, line))                  # builds a list of tuples. The tuple is: (line index, line text as a string). Did this because I need the location of the description and all lines of it/after it starts.

                # Subject Line
                if line.startswith(str_Subject):                # Storing the request type in a variable.
                    if "Legal" in line:
                        strRequestType = "Legal"
                    elif "Other" in line:
                        strRequestType = "Other"
                    elif "Reprint" in line:
                        strRequestType = "Reprint"
                    else:
                        strRequestType = "Unknown Request Type"

                # TODO: create and use a function to perform the below repetitive code. Needs to handle extra steps for Lat/Long
                # Contact Information
                elif line.startswith(str_Name) and len(line[len(str_Name):]) > 0: # skips if name is not given
                    strMapRequester = line[len(str_Name):].strip()
                elif line.startswith(str_Phone) and len(line[len(str_Phone):]) > 0: # skips if phone is not given
                    strPhone = line[len(str_Phone):].strip()
                    
                # Map Details                  
                elif line.startswith(str_MapTitle) and len(line[len(str_MapTitle):]) > 0: # checks for an empty title, which happens sometimes
                    strTitle = line[len(str_MapTitle):].strip()
                elif line.startswith(str_Subtitle) and len(line[len(str_Subtitle):]) > 0: # checks for an empty subtitle, which is common
                    strSubtitle = line[len(str_Subtitle):].strip()
                elif line.startswith(str_MapSize) and len(line[len(str_MapSize):]) > 0: # checks map size. Will use to grab the needed template.
                    strMapSize = line[len(str_MapSize):].strip()
                elif line.startswith(str_AltMapSize) and len(line[len(str_AltMapSize):]) > 0: # checks alternate map size. Will use to notify me that an alternate size was requested.
                    strAltMapSize = line[len(str_AltMapSize):].strip()
                elif line.startswith(str_County) and len(line[len(str_County):]) > 0: # checks and grabs County.
                    strCounty = line[len(str_County):].strip()                                            
                elif line.startswith(str_Latitude) and len(line[len(str_Latitude):]) > 0: # checks Latitude. Will grab, convert to type float.  
                    strLatitude = line[len(str_Latitude):].strip()
                    floLatitude = float(strLatitude)
                elif line.startswith(str_Longitude) and len(line[len(str_Longitude):]) > 0: # checks Longitude. Will grab, convert to type float.  
                    strLongitude = line[len(str_Longitude):].strip()
                    floLongitude = float(strLongitude)

                elif line.startswith(str_CircDistNeed) and len(line[len(str_CircDistNeed):]) > 0: # checks if radial distance is needed
                    strRadialBuffer = line[len(str_CircDistNeed):].strip()
                elif line.startswith(str_CircDist) and len(line[len(str_CircDist):]) > 0: # radial distance value needed
                    floRadialDistanceValue = line[len(str_CircDist):].strip()
                elif line.startswith(str_CircDistUnits) and len(line[len(str_CircDistUnits):]) > 0: # the units of the radial distance needed
                    strRadialUnits = line[len(str_CircDistUnits):].strip()
                elif line.startswith(str_CircDistFeature) and len(line[len(str_CircDistFeature):]) > 0: # the feature from which to measure
                    strRadialDistanceFeature = line[len(str_CircDistFeature):].strip()

                elif line.startswith(str_LinDistNeed) and len(line[len(str_LinDistNeed):]) > 0: # checks if linear distance is needed
                    strLinearDistance = line[len(str_LinDistNeed):].strip()
                elif line.startswith(str_CircDist) and len(line[len(str_CircDist):]) > 0: # linear distance value needed
                    floRadialDistanceValue = line[len(str_CircDist):].strip()
                elif line.startswith(str_CircDistUnits) and len(line[len(str_CircDistUnits):]) > 0: # the units of the linear distance needed
                    strRadialUnits = line[len(str_CircDistUnits):].strip()
                elif line.startswith(str_CircDistFeature) and len(line[len(str_CircDistFeature):]) > 0: # the feature from which to measure
                    strRadialDistanceFeature = line[len(str_CircDistFeature):].strip()

                # Map Layers
            ##    elif line.startswith(str_SatImgBgrnd) and len(line[len(str_SatImgBgrnd):]) > 0: # # commented out because google imagery was causing script to fail
            ##         strSatelliteImagery = line[len(str_SatImgBgrnd):].strip()
                elif line.startswith(str_TXCounties) and len(line[len(str_TXCounties):]) > 0: # 
                    strTexasCounties = line[len(str_TXCounties):].strip()
                elif line.startswith(str_Roads) and len(line[len(str_Roads):]) > 0: # 
                    strRoads = line[len(str_Roads):].strip()
                elif line.startswith(str_Watercourses) and len(line[len(str_Watercourses):]) > 0: # 
                    strWatercourse = line[len(str_Watercourses):].strip()
                elif line.startswith(str_Waterbodies) and len(line[len(str_Waterbodies):]) > 0: # 
                    strWaterbody = line[len(str_Waterbodies):].strip()
                elif line.startswith(str_WWOutfalls) and len(line[len(str_WWOutfalls):]) > 0: # 
                    strWasteWaterOutfalls = line[len(str_WWOutfalls):].strip()
                elif line.startswith(str_Cities) and len(line[len(str_Cities):]) > 0: # 
                    strCities = line[len(str_Cities):].strip()
                elif line.startswith(str_TXOutline) and len(line[len(str_TXOutline):]) > 0: # 
                    strTexasOutline = line[len(str_TXOutline):].strip()
                elif line.startswith(str_TCEQRegions) and len(line[len(str_TCEQRegions):]) > 0: # 
                    strTCEQregions = line[len(str_TCEQRegions):].strip()
                elif line.startswith(str_TCEQRegionalAreas) and len(line[len(str_TCEQRegionalAreas):]) > 0: # 
                    strTCEQregionalAreas = line[len(str_TCEQRegionalAreas):].strip()
                elif line.startswith(str_AirSites) and len(line[len(str_AirSites):]) > 0: # 
                    strAirSites = line[len(str_AirSites):].strip()
                elif line.startswith(str_Brownfields) and len(line[len(str_Brownfields):]) > 0: # 
                    strBrownfields = line[len(str_Brownfields):].strip()
                elif line.startswith(str_DryCleaners) and len(line[len(str_DryCleaners):]) > 0: # 
                    strDryCleaners = line[len(str_DryCleaners):].strip()
                elif line.startswith(str_IHWFacilities) and len(line[len(str_IHWFacilities):]) > 0: # 
                    strIHWfacilities = line[len(str_IHWFacilities):].strip()
                elif line.startswith(str_InjectionWells) and len(line[len(str_InjectionWells):]) > 0: # 
                    strInjectionWells = line[len(str_InjectionWells):].strip()
                elif line.startswith(str_MSDPoints) and len(line[len(str_MSDPoints):]) > 0: # 
                    strMSDpoints = line[len(str_MSDPoints):].strip()
                elif line.startswith(str_MSDPolygons) and len(line[len(str_MSDPolygons):]) > 0: # 
                    strMSDpolygons = line[len(str_MSDPolygons):].strip()
                elif line.startswith(str_MSWLandfills) and len(line[len(str_MSWLandfills):]) > 0: # 
                    strMSWlandfills = line[len(str_MSWLandfills):].strip()
                elif line.startswith(str_PSTPoints) and len(line[len(str_PSTPoints):]) > 0: # 
                    strPSTpoints = line[len(str_PSTPoints):].strip()
                elif line.startswith(str_SuperfundSites) and len(line[len(str_SuperfundSites):]) > 0: # 
                    strSuperfundSites = line[len(str_SuperfundSites):].strip()
                elif line.startswith(str_CCNSewer) and len(line[len(str_CCNSewer):]) > 0: # 
                    strCCNsewer = line[len(str_CCNSewer):].strip()
                elif line.startswith(str_CCNWater) and len(line[len(str_CCNWater):]) > 0: # 
                    strCCNwater = line[len(str_CCNWater):].strip()
                elif line.startswith(str_EdwardsAquiferRegulatoryArea) and len(line[len(str_EdwardsAquiferRegulatoryArea):]) > 0: # 
                    strEdwardsAquiferRegulatoryArea = line[len(str_EdwardsAquiferRegulatoryArea):].strip()
                elif line.startswith(str_GCDs) and len(line[len(str_GCDs):]) > 0: # 
                    strGroundwaterConservationDistricts = line[len(str_GCDs):].strip()
            ##    elif line.startswith(str_PWSData) and len(line[len(str_PWSData):] > 0: # 
            ##         strPublicWaterSupply = line[len(str_PWSData):].strip()
            ##    elif line.startswith(str_SWData) and len(line[len(str_SWData):] > 0: # 
            ##         strSurfaceWater = line[len(str_SWData):].strip()
                elif line.startswith(str_WaterDistricts) and len(line[len(str_WaterDistricts):]) > 0: # 
                    strWaterDistricts = line[len(str_WaterDistricts):].strip()
                elif line.startswith(str_MajorAquifers) and len(line[len(str_MajorAquifers):]) > 0: # 
                    strMajorAquifers = line[len(str_MajorAquifers):].strip()
                elif line.startswith(str_MinorAquifers) and len(line[len(str_MinorAquifers):]) > 0: # 
                    strMinorAquifers = line[len(str_MinorAquifers):].strip()
                elif line.startswith(str_RiverBasins) and len(line[len(str_RiverBasins):]) > 0: # 
                    strRiverBasins = line[len(str_RiverBasins):].strip()
                elif line.startswith(str_WatershedsHUC8) and len(line[len(str_WatershedsHUC8):]) > 0: # 
                    strWatershedsHUC8 = line[len(str_WatershedsHUC8):].strip()
                elif line.startswith(str_WatershedsHUC10) and len(line[len(str_WatershedsHUC10):]) > 0: # 
                    strWatershedsHUC10 = line[len(str_WatershedsHUC10):].strip()
                elif line.startswith(str_WatershedsHUC12) and len(line[len(str_WatershedsHUC12):]) > 0: # 
                    strWatershedsHUC12 = line[len(str_WatershedsHUC12):].strip()
                elif line.startswith(str_Soils) and len(line[len(str_Soils):]) > 0: # 
                    strSoils = line[len(str_Soils):].strip()
                elif line.startswith(str_Faults) and len(line[len(str_Faults):]) > 0: # 
                    strFaults = line[len(str_Faults):].strip()
                elif line.startswith(str_RockUnits) and len(line[len(str_RockUnits):]) > 0: # 
                    strRockUnits = line[len(str_RockUnits):].strip()
                elif line.startswith(str_Airports) and len(line[len(str_Airports):]) > 0: # 
                    strAirports = line[len(str_Airports):].strip()
                elif line.startswith(str_RailRoads) and len(line[len(str_RailRoads):]) > 0: # 
                    strRailRoads = line[len(str_RailRoads):].strip()
                elif line.startswith(str_TEASchools) and len(line[len(str_TEASchools):]) > 0: # 
                    strTEAschools = line[len(str_TEASchools):].strip()
                elif line.startswith(str_TLCDistrictsCongress) and len(line[len(str_TLCDistrictsCongress):]) > 0: # 
                    strTLCdistrictsCongress = line[len(str_TLCDistrictsCongress):].strip()
                elif line.startswith(str_TLCDistrictsHouse) and len(line[len(str_TLCDistrictsHouse):]) > 0: # 
                    strTLCdistrictsHouse = line[len(str_TLCDistrictsHouse):].strip()
                elif line.startswith(str_TLCDistrictsSenate) and len(line[len(str_TLCDistrictsSenate):]) > 0: # 
                    strTLCdistrictsSenate = line[len(str_TLCDistrictsSenate):].strip() 

                # Description        
            ##    elif line.startswith(str_DescriptionHEADER):
                elif line.startswith(str_Description) and len(line[len(str_Description):]) > 0: # skips if the description isn't given, which happens sometimes.
                    intDescPos = count
                # Increment the count to store the line index.       
                count += 1


        lstIndex.sort()                                         # This sorts the tuples in the list by line index number
        # The section below is code to grab the entire Description text submitted by the map requester as stored in the email txt file.
        # There are some necessary set-up pieces above here. It strips out the <br />.
        for item in lstIndex:
            if item[0] == intDescPos:
                text = item[1]
                text = re.findall('\s.*', text)
                text = string.replace(text[0], "<br />", "")
                strDescription = text.strip()
            elif item[0] > intDescPos:
                text = item[1]
        ##        text = string.replace(text, "<br />", "")
                text = text.strip()
                strDescription = strDescription + " " + text
            else:
                continue
        # END of the section

        femail.close()                                          # we are finished with the email text-file so close it out.
        arcpy.AddMessage("The email file has been closed. The map is being created based on the request details.")

        # Dictionary of Layer Paths in GeoData and their ON/OFF status based on the email information. THIS HAS TO COME AFTER THE EMAIL INFORMATION HAS BEEN READ AND THE VARIABLES HAVE BEEN UPDATED FROM THEIR ORIGINAL ASSIGNMENT TO WHAT THE EMAIL INDICATES.
        # May be better form to create variables for the layer paths and then put the variables in the dictionary? (is more code! but...)
        dictLayers = {r"\\tceq4apmgisdata\gisdat\Geodata\Administrative\MNET_CITY_PLACE.lyr": strCities,r"\\tceq4apmgisdata\gisdat\Geodata\Administrative\TCEQ_CCN_SEWER.lyr": strCCNsewer,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Administrative\TCEQ_CCN_WATER.lyr": strCCNwater,r"\\tceq4apmgisdata\gisdat\Geodata\Administrative\TCEQ_EDWARDS_REGULATORY.lyr": strEdwardsAquiferRegulatoryArea,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Administrative\TCEQ_REGIONAL_AREAS.lyr": strTCEQregionalAreas,r"\\tceq4apmgisdata\gisdat\Geodata\Administrative\TCEQ_REGIONS.lyr": strTCEQregions,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Administrative\TEA_SCHOOLS.lyr": strTEAschools,r"\\tceq4apmgisdata\gisdat\Geodata\Administrative\TLC_CONGRESSIONAL_DISTRICTS.lyr": strTLCDistrictsCongress,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Administrative\TLC_HOUSE_DISTRICTS.lyr": strTLCDistrictsHouse,r"\\tceq4apmgisdata\gisdat\Geodata\Administrative\TLC_SENATE_DISTRICTS.lyr": strTLCDistrictsSenate,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Air\AIR_SITES.lyr": strAirSites,r"\\tceq4apmgisdata\gisdat\Geodata\Facility\TCEQ_BROWNFIELDS.lyr": strBrownfields,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Facility\TCEQ_DRYCLEANERS.lyr": strDryCleaners,r"\\tceq4apmgisdata\gisdat\Geodata\Facility\TCEQ_IHW_FACILITIES.lyr": strIHWfacilities,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Facility\TCEQ_INJECTION_WELLS.lyr": strInjectionWells,r"\\tceq4apmgisdata\gisdat\Geodata\Facility\TCEQ_MSD_POINTS.lyr": strMSDpoints,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Facility\TCEQ_MSD_POLY.lyr": strMSDpolygons,r"\\tceq4apmgisdata\gisdat\Geodata\Facility\TCEQ_MSW_LANDFILL_POLY.lyr": strMSWlandfills,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Facility\TCEQ_PST.lyr": strPSTpoints,r"\\tceq4apmgisdata\gisdat\Geodata\Facility\TCEQ_SUPERFUND_SITES.lyr": strSuperfundSites,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Geology\NRCS_STATSGO_SOILS.lyr": strSoils,r"\\tceq4apmgisdata\gisdat\Geodata\Geology\USGS_DGAT_FAULT_250K.lyr": strFaults,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Geology\USGS_DGAT_ROCKUNIT_250K.lyr": strRockUnits,r"\\tceq4apmgisdata\gisdat\Geodata\Imagery\Google_Imagery.lyr": strSatelliteImagery,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Transportation\MNET_AIRPORT.lyr": strAirports,r"\\tceq4apmgisdata\gisdat\Geodata\Transportation\MNET_RAILROAD.lyr": strRailRoads,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Water\MNET_WATER.lyr": strWatercourse,r"\\tceq4apmgisdata\gisdat\Geodata\Transportation\MNET_TRANSPORTATION.lyr": strRoads,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Water\MNET_WATER_POLYGON.lyr": strWaterbody,r"\\tceq4apmgisdata\gisdat\Geodata\Water\TCEQ_CCN_SEWER.lyr": strCCNsewer,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Water\TCEQ_CCN_WATER.lyr": strCCNwater,r"\\tceq4apmgisdata\gisdat\Geodata\Water\TCEQ_GCD.lyr": strGroundwaterConservationDistricts,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Water\TCEQ_OUTFALLS_WASTEWATER.lyr": strWasteWaterOutfalls,r"\\tceq4apmgisdata\gisdat\Geodata\Water\TCEQ_WATER_DISTRICTS.lyr": strWaterDistricts,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Water\TWDB_MAJOR_AQUIFERS.lyr": strMajorAquifer,r"\\tceq4apmgisdata\gisdat\Geodata\Water\TWDB_MINOR_AQUIFERS.lyr": strMinorAquifer,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Water\TWDB_RIVER_BASINS.lyr": strRiverBasins,r"\\tceq4apmgisdata\gisdat\Geodata\Water\USGS_HUC_08_WATERSHEDS.lyr": strWatershedsHUC8,\
                      r"\\tceq4apmgisdata\gisdat\Geodata\Water\USGS_HUC_10_WATERSHEDS.lyr": strWatershedsHUC10,r"\\tceq4apmgisdata\gisdat\Geodata\Water\USGS_HUC_12_WATERSHEDS.lyr": strWatershedsHUC12}
                # Satelitte Imagery and Transportation (roads) are group layers with sublayers inside. They will not add to the map via the script at the bottom. They are in the above \
                # dictionary but the code down below filters out layers with "Google" and "Transportation" in their path
                # On 20160205 removed r"\\tceq4apmgisdata\gisdat\Geodata\Administrative\TXDOT_STATE_OUTLINE.lyr": strTexasOutline,r"\\tceq4apmgisdata\gisdat\Geodata\Administrative\_TXDOT_COUNTIES.lyr": strTexasCounties,\
                # from the above dictionary. The layers are default layers, in the template mxd, and dont need to be added again. If the user unclicks them in the form they are going to be in the map anyway. 
                # Doing this because they were being added to the map a second time and lacked symbology. This was the easiest way for now.

        # Determine which mxd template to grab and copy and rename
        if "8.5 x 11" in strMapSize:
            strMapSize = "Template85_11"
        elif "ANSI C" in strMapSize:
            strMapSize = "Template17_22"
        elif "ANSI D" in strMapSize:
            strMapSize = "Template22_34"
        elif "ANSI E" in strMapSize:
            strMapSize = "Template34_44"
        elif "35 x 35" in strMapSize:
            strMapSize = "Template35_35"
        else:                               # To handle the Alternate map size situation. Defaults to a 22x34 map. Down below the AlternateMapSize text element is relocated to the center of the map to alert the cartographer.
            strMapSize = "Template22_34"
            
        if doLogging:
            arcpy.AddMessage("(log) Map Size: " + strMapSize)
            
        # store the full template mxd filename in a variable
        strTemplateMXDFileName = strMapSize + ".mxd"

        # Define the path for the project mxd
        pathMXD = os.path.join(strRootPath, strCRF_num + ".mxd")

        # copy the necessary template to the project folder and rename it using the CRF number 
        pathMXDtemplatesStorageLocation = r"\\tceq4apmgisdata\giswrk\IRGIS\Mapping\AGprojects\Project_FolderStructure_Model\PreModelSetupFiles"
        strTemplatePath = os.path.join(pathMXDtemplatesStorageLocation, strTemplateMXDFileName)
        arcpy.Copy_management(strTemplatePath, pathMXD)

        # create a map document object for the newly created file
        mapDoc = arcpy.mapping.MapDocument(pathMXD)

        if doLogging:
            arcpy.AddMessage(mapDoc)
            
        # prepare the inset paragraph for use
        strParagraph = "The facility is located in " + strCounty + " County.  The circle (green) in \n the left inset map represents the approximate location of the facility. \n The inset map on the right represents the location of " + strCounty + "\n County (red) in the state of Texas."
        strSummary = "Map for " + strMapRequester + "  " + strPhone # storing the summary text for later use

        if doLogging:
            arcpy.AddMessage("(log) " + strParagraph)
        if doLogging:
            arcpy.AddMessage("(log) " + strSummary)
            
        # Change the title, subtitle if one is provided, inset paragraph, county name
        for elm in arcpy.mapping.ListLayoutElements(mapDoc):
            if doLogging:
                arcpy.AddMessage(elm.name)
            if len(strSubtitle) != 0 and elm.name == "Sub_Title":
                elm.text = strSubtitle
            elif elm.name == "County_Name":
                elm.text = strCounty + " County"
            elif elm.name == "Inset_Paragraph":
                elm.text = strParagraph                         # store the formatted paragraph, with county name concatenation, in a variable
                if strMapSize == "Template85_11":
                    elm.elementPositionX =  0.3402                   # so that the text box element doesn't relocate
                    elm.elementPositionY =  0.3192                   # so that the text box element doesn't relocate
                elif strMapSize == "Template17_22":
                    elm.elementPositionX =  19.3269
                    elm.elementPositionY =  0.4225
                elif strMapSize == "Template22_34":
                    elm.elementPositionX =  31.2269  
                    elm.elementPositionY =  0.5225
                elif strMapSize == "Template34_44":
                    elm.elementPositionX =  41.2368    
                    elm.elementPositionY =  0.5225
                elif strMapSize == "Template35_35":
                    elm.elementPositionX =  32.2269
                    elm.elementPositionY =  0.5225
            elif elm.name == "AlternateMapSize" and len(strAltMapSize) > 0 and strMapSize == "Template22_34":
                elm.elementPositionX = 16
                elm.elementPositionY = 12
            else:
                pass
                

        # Fill out the Map Document Properties with proper documentation. 
        mapDoc.title = strTitle                                 # The title on the layout is a dynamic text element that references the Map Document Properties
        mapDoc.summary = strSummary                             # just storing the requesters name and phone extension in the Map Document Properties
        mapDoc.description = strDescription                     # storing all lines of the description text.

        # Set the default geodatabase (workspace environment ?) to the project (CRF#) geodatabase. Started a thread on ESRI GeoNet on 7/31/15. Answer: Is not possible using ArcPy! Would have to use ArcObjects to create.
        ##gdbPath = rootpath + "\\" + crf_num + ".gdb"
        ##arcpy.env.workspace = gdbPath

        # Define the County based definition queries for the data frames. If this is a basic map request a county may not be specified. It will skip if so.
        strQuery = "Name = " + "'"+strCounty+"'" 
        for df in arcpy.mapping.ListDataFrames(mapDoc, "Main Data Frame"):
            if doLogging:
                arcpy.AddMessage(df.name)
            for lyr in arcpy.mapping.ListLayers(df, "County Boundary"):
                if doLogging:
                    arcpy.AddMessage("(log) County in query: " + strCounty)
                if doLogging:
                    arcpy.AddWarning("A specific county was not given. Definition querying skipped.")
                if len(strCounty) > 0:
                    arcpy.MakeFeatureLayer_management (lyr)                                     # making a feature layer to query
                    arcpy.SelectLayerByAttribute_management (lyr, "NEW_SELECTION", strQuery)    # select the layer by the query
                    df.zoomToSelectedFeatures()                                                 # zoom to the feature in memory
                    arcpy.SelectLayerByAttribute_management (lyr, "CLEAR_SELECTION")
                    arcpy.RefreshActiveView()                                                   # refresh the map so that the extent change shows up
                    if doLogging:
                        arcpy.AddMessage(lyr.name)

        for df in arcpy.mapping.ListDataFrames(mapDoc, "County Inset"):
            if doLogging:
                arcpy.AddMessage(df.name)
            for lyr in arcpy.mapping.ListLayers(df, "Counties"):
                if len(strCounty) > 0:
                    lyr.definitionQuery = strQuery                  # run the definition query
                    df.zoomToSelectedFeatures()                     # zoom to the feature in memory
                    arcpy.RefreshActiveView()                       # refresh the map so that the extent change shows up
                        
        for df in arcpy.mapping.ListDataFrames(mapDoc, "State Inset"):
            if doLogging:
                arcpy.AddMessage(df.name)
            for lyr in arcpy.mapping.ListLayers(df, "County of Interest"):
                if len(strCounty) > 0:
                    lyr.definitionQuery = strQuery                  # run the definition query
                    arcpy.RefreshActiveView()                       # refresh the map so that the extent change shows up

        # Add the Points, Lines, and Polygons feature classes in the CRF geodatabase to the Main Data Frame
        FCUserDefinedPointPath = strRootPath + "\\" + strCRF_num + ".gdb" + "\\" + "UserDefinedPoint"
        for df in arcpy.mapping.ListDataFrames(mapDoc):
            if doLogging:
                arcpy.AddMessage(df.name)
            if df.name == "Main Data Frame":
                FCpoints = strRootPath + "\\" + strCRF_num + ".gdb" + "\\" + "Project\Points"  
                arcpy.MakeFeatureLayer_management(FCpoints, "POINTS")           # A layer file must be created for a feature class. Feature classes cannot be added straight to a map using arcpy.
                lyrPoints = arcpy.mapping.Layer("POINTS")
                arcpy.mapping.AddLayer(df, lyrPoints)
                
                FClines = strRootPath + "\\" + strCRF_num + ".gdb" + "\\" + "Project\Lines"  
                arcpy.MakeFeatureLayer_management(FClines, "LINES")
                lyrLines = arcpy.mapping.Layer("LINES")
                arcpy.mapping.AddLayer(df, lyrLines)
                
                FCpolygons = strRootPath + "\\" + strCRF_num + ".gdb" + "\\" + "Project\POLYGONS"  
                arcpy.MakeFeatureLayer_management(FCpolygons, "POLYGONS")
                lyrPolygons = arcpy.mapping.Layer("POLYGONS")
                arcpy.mapping.AddLayer(df, lyrPolygons)
                
                # Creating a point from the Lat/Long provided by the user in the web form. Also, styling the point to be a green circle with black dot in center.
                
                arcpy.AddWarning("Latitude: " + str(floLatitude) + " , Longitude: " + str(floLongitude))
                cursor = arcpy.da.InsertCursor(FCUserDefinedPointPath, ["SHAPE@XY"]) #JBoss showing this as having an error, not recognizing InsertCursor but it does work and is valid
                xy = (floLongitude, floLatitude)
                cursor.insertRow([xy])
                arcpy.MakeFeatureLayer_management(FCUserDefinedPointPath, "User Defined Point")          
                lyrUserPoint = arcpy.mapping.Layer("User Defined Point")
                strLayerSymbologyPath = r"\\tceq4apmgisdata\giswrk\IRGIS\Mapping\AGprojects\Project_FolderStructure_Model\PreModelSetupFiles\User Defined Point.lyr"
                arcpy.ApplySymbologyFromLayer_management(lyrUserPoint, strLayerSymbologyPath)
                arcpy.mapping.AddLayer(df, lyrUserPoint)
                
                # Add layers from GeoData to the map based on the requesters choices
                # for items in dictLayers are "on", that layer needs to be added to main data frame.
                arcpy.AddMessage("Adding the requested layers to the map.")
                for layerPath in dictLayers.keys():
                    if doLogging:
                        arcpy.AddMessage(layerPath)
                    if dictLayers[layerPath] == "on" and "Google" not in layerPath and "Transportation" not in layerPath:
                        ##arcpy.AddMessage(layerPath)
                        # break up the layer path to grab the file name.
                        strBaseName = os.path.basename(layerPath)
                        lstBaseNameParts = os.path.splitext(strBaseName)
                        strFileName = lstBaseNameParts[0]
                        # feed the file name (sans extension) into arcpy to create and add a layer to the Table of Contents
                        arcpy.MakeFeatureLayer_management(layerPath, strFileName)
                        lyrRequestedLayer = arcpy.mapping.Layer(strFileName)          
                        arcpy.mapping.AddLayer(df, lyrRequestedLayer)
                        arcpy.AddMessage(strFileName + " has been added.")
            elif df.name == "County Inset":
                arcpy.MakeFeatureLayer_management(FCUserDefinedPointPath, "User Defined Point")          
                lyrUserPoint = arcpy.mapping.Layer("User Defined Point")
                strLayerSymbologyPath = r"\\tceq4apmgisdata\giswrk\IRGIS\Mapping\AGprojects\Project_FolderStructure_Model\PreModelSetupFiles\User Defined Point.lyr"
                arcpy.ApplySymbologyFromLayer_management(lyrUserPoint, strLayerSymbologyPath)
                arcpy.mapping.AddLayer(df, lyrUserPoint)

        # Save in case next step fails (use while testing).
        ## mapDoc.save()
               
        ##    else:
        ##        # break up the layer path to grab the file name.
        ##        urlGoogleWMS = r"https://txgi.tnris.org/login/path/apollo-panic-east-travel/wms?"
        ##        strBaseName = os.path.basename(layerPath)
        ##        lstBaseNameParts = os.path.splitext(strBaseName)
        ##        strFileName = lstBaseNameParts[0]
        ##        # feed the file name (sans extension) into arcpy to create and add a layer to the Table of Contents
        ##        arcpy.MakeImageServerLayer_management(urlGoogleWMS, strFileName)
        ##        lyrRequestedLayer = arcpy.mapping.Layer(strFileName)          #STOP: this is where the script is failing. DUE TO LAYER HAVING SUBLAYERS!
        ##        arcpy.mapping.AddLayer(df, lyrRequestedLayer)
        ##        arcpy.AddMessage(layerPath + " has been added to the map, per the requesters choosing.")


        # save the mxd one last time
        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()
        mapDoc.save()
        arcpy.AddMessage("The new map has been saved and is ready for use.")


        if doLogging:
            arcpy.AddMessage(dir())

        arcpy.AddWarning("\n" + "*"*30)

        # Close and delete all the files, objects, etc.
##        lstVariablesToDelete = dir()
##        for item in lstVariablesToDelete:
##            if "__" not in item:
##                del item
        ## as of 10/1/15 ['FClines', 'FCpoints', 'FCpolygons', '__builtins__', '__doc__', '__file__', '__name__', '__package__', 'arcgis', 'arcpy', 'count', 'datetime', 'df', 'dictLayers', 'dirname', 'dirs', 'doLogging', 'elm', 'env', 'femail', 'filename', 'files', 'floLatitude', 'floLinearDistanceValue', 'floLongitude', 'floRadialDistanceValue', 'intDescPos', 'item', 'layerPath', 'line', 'lstBaseNameParts', 'lstIndex', 'lstSep', 'lstSep2', 'lstTexasCounties', 'lyr', 'lyrLines', 'lyrPoints', 'lyrPolygons', 'lyrRequestedLayer', 'mapDoc', 'math', 'os', 'pathMXD', 'pathMXDtemplatesStorageLocation', 're', 'strAirSites', 'strAirports', 'strAltMapSize', 'strBaseName', 'strBrownfields', 'strCCNsewer', 'strCCNwater', 'strCRF_num', 'strCities', 'strCounty', 'strDescription', 'strDryCleaners', 'strEdwardsAquiferRegulatoryArea', 'strEmailPath', 'strFaults', 'strFileName', 'strGroundwaterConservationDistricts', 'strIHWfacilities', 'strInjectionWells', 'strLatitude', 'strLinearDistance', 'strLinearDistanceFeature', 'strLinearUnits', 'strLongitude', 'strMSDpoints', 'strMSDpolygons', 'strMSWlandfills', 'strMajorAquifer', 'strMapRequester', 'strMapSize', 'strMinorAquifer', 'strPSTpoints', 'strParagraph', 'strPhone', 'strQuery', 'strRadialBuffer', 'strRadialDistanceFeature', 'strRadialUnits', 'strRailRoads', 'strRequestType', 'strRequester', 'strRiverBasins', 'strRoads', 'strRockUnits', 'strRootPath', 'strSatelliteImagery', 'strSoils', 'strSubtitle', 'strSummary', 'strSuperfundSites', 'strTCEQregionalAreas', 'strTCEQregions', 'strTEAschools', 'strTLCDistrictsCongress', 'strTLCDistrictsHouse', 'strTLCDistrictsSenate', 'strTemplateMXDFileName', 'strTemplatePath', 'strTestingEmailPath', 'strTexasCounties', 'strTexasOutline', 'strTitle', 'strWasteWaterOutfalls', 'strWaterDistricts', 'strWaterbody', 'strWatercourse', 'strWatershedsHUC10', 'strWatershedsHUC12', 'strWatershedsHUC8', 'str_AirSites', 'str_Airports', 'str_AltMapSize', 'str_Brownfields', 'str_CCNSewer', 'str_CCNWater', 'str_CircDist', 'str_CircDistFeature', 'str_CircDistNeed', 'str_CircDistUnits', 'str_Cities', 'str_County', 'str_Description', 'str_DryCleaners', 'str_EdwardsAquiferRegulatoryArea', 'str_Email', 'str_Faults', 'str_GCDs', 'str_IHWFacilities', 'str_InjectionWells', 'str_Latitude', 'str_LinDist', 'str_LinDistFeature', 'str_LinDistNeed', 'str_LinDistUnits', 'str_Longitude', 'str_MSDPoints', 'str_MSDPolygons', 'str_MSWLandfills', 'str_MajorAquifers', 'str_MapSize', 'str_MapTitle', 'str_MinorAquifers', 'str_Name', 'str_PSTPoints', 'str_Phone', 'str_RailRoads', 'str_RiverBasins', 'str_Roads', 'str_RockUnits', 'str_SatImgBgrnd', 'str_Soils', 'str_Subject', 'str_Subtitle', 'str_SuperfundSites', 'str_TCEQRegionalAreas', 'str_TCEQRegions', 'str_TEASchools', 'str_TLCDistrictsCongress', 'str_TLCDistrictsHouse', 'str_TLCDistrictsSenate', 'str_TXCounties', 'str_TXOutline', 'str_WWOutfalls', 'str_WaterDistricts', 'str_Waterbodies', 'str_Watercourses', 'str_WatershedsHUC10', 'str_WatershedsHUC12', 'str_WatershedsHUC8', 'string', 'sys', 'text', 'time']


        return

class Floorplan(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Floorplan Update - Map Request Process"
        self.description = "When Patty Love, executive assistant, requests and updated Building A, Floor 2, IRD Floorplan map you run this model to automate the export of a pdf of a preconfigured mxd. The mxd is connected to an excel file that Patty edits from her station. You must first create the CRF project folder so that you can choose it in this model."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(displayName="CRF Folder",
                                 name="CustomerRequestFormFolder",
                                 datatype="DEFolder",
                                 parameterType="Required",
                                 direction="Input")

        params = [param0]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        ###################################
        # Script:  ExportFloorPlanMap_Script.py
        # Author:  CJuice on GitHub
        # Date Created:  06/23/2015
        # Purpose:  Automate the print out of floorplan maps for Patty.
        # Inputs:  No Inputs
        # Outputs:  A Map that is to be emailed to Patty
        # Modifications:  20160621 moved to new Python Toolbox from freestanding script
        ###################################
        #
        # Start Scripting Below

        # Define the map document that will be opened and worked with, store as a variable
        mxdPath = r"\\tceq4apmgisdata\giswrk\IRGIS\Mapping\AGprojects\Project_FolderStructure_Model\PreModelSetupFiles\FloorplanMap.mxd"
        mxd = arcpy.mapping.MapDocument(mxdPath)

        # To put todays date in the file name, import datetime and then the date method(?) to access the today() feature.
        # Make sure the date is string so that it can be used in the file name

        import datetime
        from datetime import date

        # Store the filename
        documentname = str(date.today()) + "FloorplanMap"

        # Build the full path for the output pdf
        pdfpath = parameters[0].valueAsText + "\\" + documentname + ".pdf"

        # Export the pdf
        try:
            arcpy.mapping.ExportToPDF(mxd, pdfpath)
            arcpy.AddWarning("PDF exported successfully")
        except:
            arcpy.AddError("PDF did not export properly")
        
        # Delete the object references
        del mxd

        return
