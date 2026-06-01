This README file was generated on [2025-11-25] by [Dr Matthew Wassall].

-------------------
GENERAL INFORMATION
-------------------
// Title of Dataset: IMU dataset of lower limb prosthetic users traversing real-world terrain with and without a walking aid
// DOI: doi:10.18710/U8RGDL
// Contact Information
     // Name: Dr Matthew Wassall
     // Institution: NTNU – Norwegian University of Science and Technology
     // Email: matthelw@ntnu.no
     // ORCID: 0000-0001-7288-1669


// Contributors: See metadata field Contributor.
// Data Type: See metadata field Data Type.
// Date of Collection: See metadata field Date of Collection.
// Funding sources: See metadata section Funding Information.

// Description of dataset: 
This dataset contains inertial measurement unit (IMU) data from twenty lower limb prosthetic users (mean ± SD age: 64.6 ± 11.8 years, 2 female, 18 male; 11 transtibial, 8 transfemoral, 1 bilateral amputee transtibial right leg transfemoral left leg) traversing real-world terrain (flat ground, stairs, slopes, grass, uneven terrain, unstable terrain) with and without a walking aid. Data from four body worn IMUs (prosthetic shank, prosthetic thigh, trunk, other shank) was collected for this dataset. 

--------------------------
METHODOLOGICAL INFORMATION
--------------------------

The data was recorded at 100Hz, using Xsens Awinda IMUs (Movella Inc, California, USA) and the data in the dataset is the raw IMU data and the signals have not been filtered. Datafiles have been synchronized, using a synchronization movement that was then identified using peak detection in Matlab. Individual strides have been identified in the datafiles and the terrain label for each stride as well as identifying turn steps are also included. Strides were identified using peaks of the rate of turn along the medio-lateral direction of the prosthetic shank (IMU variable Gyroscope Y). The data has been trimmed to remove recordings before the frist stride and after the last stride.  

This dataset contains IMU data for 20 lower limb prosthetic users (11 transtibial, 8 transfemoral and one bilateral transtibial right leg transfemoral left leg) traversing a variety of real-world terrain. Participant number and prosthetic type are listed below:

Participant number	Type of prosthetic
P1			Left Transtibial
P2			Left Transtibial
P3			Right Transfemoral
P4			Right Transfemoral
P5			Right Transtibial
P6			Right Transtibial
P7			Bilateral (TT - right transtibial, TF - left transfemoral)
P8			Left Transtibial
P9			Left Transfemoral
P10			Left Transfemoral
P11			Right Transtibial
P12			Left Transfemoral
P13			Right Transtibial
P14			Right Transfemoral
P15			Left Transtibial
P16			Left Transfemoral
P17			Left Transtibial
P18			Left Transtibial
P19			Right Transfemoral
P20			Right Transtibial

The terrain that was used in the data collection is detailed below. Not all participants collected data on all terrain types.

Terrain		Naming convention	Label
Flat		FL			1
Grass		GR			2
Stair ascent 	ST			4
Stair descent	ST			5
Slope ascent	SL			6
Slope descent	SL			7
Gravel		GV			8
Uneven terrain	UN			9

For most trials the participant started on flat ground and transitions to the stated terrain, however this was not possible for all trials.

Data was collected on the terrains with the participants with (wi) and without (wo) a walking aid. Not all participants felt comfortable walking with or without a walking aid so not all participants completed both conditions. For participant P7 the walking aid was always used in the right hand and supported the left transfemoral leg.

//Datafile variables

Each IMU datafile contains the following variables:

Feature			Units	Description
Acceleration X		m/s2	Acceleration in the vertical direction (w/gravity)
Acceleration Y 		m/s2	Acceleration in the medio-lateral direction (w/gravity)
Acceleration Z 		m/s2	Acceleration in the anterior-posterior direction (w/gravity)
Free Acceleration E 	m/s2	Acceleration in the vertical direction (w/o gravity)
Free Acceleration N 	m/s2	Acceleration in the medio-lateral direction (w/o gravity)
Free Acceleration U	m/s2	Acceleration in the anterior-posterior direction (w/o gravity)
Gyroscope X 		rad/s	Rate of turn along the vertical direction
Gyroscope Y 		rad/s	Rate of turn along the medio-lateral direction
Gyroscope Z 		rad/s	Rate of turn along the anteriorposterior direction
Magnetometer X 		a.u.	3D magnetic field in the vertical direction
Magnetometer Y 		a.u.	3D magnetic field in the medio-lateral direction
Magnetometer Z 		a.u.	3D magnetic field in the anteriorposterior direction
Velocity X 		m/s	Delta_velocity (dv) in the vertical direction
Velocity Y 		m/s	Delta_velocity (dv) in the mediolateral direction
Velocity Z 		m/s	Delta_velocity (dv) in the anteriorposterior direction
Steps			N/A	Stride number
Terrain			N/A	Terrain label
Turn			N/A	Turn (1   turning, 0   not turning)

Each row in the datafile is one timepoint, with each timepoint being 0.01s apart. 

--------------------
DATA & FILE OVERVIEW
--------------------
// File List: 

P1.zip - zip folder containing all datafiles for Participant 1. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.   
P2.zip - zip folder containing all datafiles for Participant 2. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P3.zip - zip folder containing all datafiles for Participant 3. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P4.zip - zip folder containing all datafiles for Participant 4. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P5.zip - zip folder containing all datafiles for Participant 5. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P6.zip - zip folder containing all datafiles for Participant 6. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P7_TT.zip - zip folder containing all datafiles for Participant 7 with the prosthetic IMU identified as the transtibial right leg. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P7_TF.zip - zip folder containing all datafiles for Participant 7 with the prosthetic IMU identified as the transfemoral left leg. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P8.zip - zip folder containing all datafiles for Participant 8. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P9.zip - zip folder containing all datafiles for Participant 9. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P10.zip - zip folder containing all datafiles for Participant 10. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P11.zip - zip folder containing all datafiles for Participant 11. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P12.zip - zip folder containing all datafiles for Participant 12. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P13.zip - zip folder containing all datafiles for Participant 13. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P14.zip - zip folder containing all datafiles for Participant 14. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P15.zip - zip folder containing all datafiles for Participant 15. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P16.zip - zip folder containing all datafiles for Participant 16. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P17.zip - zip folder containing all datafiles for Participant 17. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P18.zip - zip folder containing all datafiles for Participant 18. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P19.zip - zip folder containing all datafiles for Participant 19. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
P20.zip	 - zip folder containing all datafiles for Participant 20. Datafiles are saved as .csv files. Details of the datafiles in each folder is stated below.
 
// Datafiles:
 
The datafiles contain IMU data for body worn IMUs. There is data for multiple trials for each participant. The participants wore 4 IMUs in each trial. The IMUs were placed on the anterior prosthetic shank (PS), anterior prosthetic leg thigh (TH), posterior trunk (TR) (approximate location of the L4 vertebra) and anterior other shank (OS) (approximately at the midpoint of each limb segment. Prosthetic shank placement varied depending on the participants prothesis, IMU was placed on prosthesis pylon to ensure consistent orientation). For participant P7 the trunk IMU was placed on the other thigh (OH), so no trunk IMU data was recorded. For each trial the participant traversed a set terrain, details of the terrains included in the data can be found in the methodological information.   

// Datafile naming convention:

Datafiles are named with the terrain type, if a walking aid was used, trial number and finally IMU location. Example:

UNwi01PS (trial over uneven terrain, with a walking aid, trial number 1, IMU on prosthetic shank)

Datafiles that start with  Step  were trials conducted on at a location where the participant traversed stairs, slopes and flat ground all in one trial.

For most participants there is multiple triles for each terrain but this was dependant on the length of the terrain and the participants ability to conduct multiple trials. 

// Is this an updated version of a dataset published on DataverseNO? no


--------------------------
SHARING/ACCESS INFORMATION
--------------------------

Data collected has been fully anonymized and is no longer considered personal data and can be shared openly. There is no data saved that could reidentify individually that participated in the data collection.   

// Licenses/Restrictions: See Terms tab.
// Links to publications that cite or use the data: See metadata field Related Publication.
// Links/relationships to related data sets: See metadata field Related Dataset.
// Data sources: See metadata field Data Source.
// Recommended citation: See citation generated by repository.



