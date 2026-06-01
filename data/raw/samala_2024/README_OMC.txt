Joint's angle data derived from the OMC system

- All lower limb joint angle (Hip, Knee and Ankle) processing data from OMC are described in detail in CSV files available in the dataset.
- Each.csv file contains all five walking trials.

For example, [OMC]01.csv is the file containing patient number 1's lower limb joint ankle for all 5 walking trials.

Below is a description of each file's contents:

Raw 1 denotes the number of waking trials.

Raw 2 denotes the joint angle parameters (hip, knee, and ankle).

Raw 3 denotes the rotational motion along each joint's axis. A description of joint attitude in clinical use can be reported in three planes, i.e., the sagittal, coronal, and transverse anatomical planes of the body (Papi, 2012).  

X, Y, Z ----> The three axes of a body segment fixed the Cartesian coordinate system

X indicates that the joint is rotational along the X axis, which is the joint's flexion/extension. 
Y indicates that the joint is rotational along the Y axis, which is the joint's abduction/adduction. 
Z indicates that the joint is rotational along the Z axis, which is the joint's internal/extenal rotation. 

Raw 4 provides the joint's angle during each joint motion (degrees).

Column A represents the number of measurement frames that were captured at a frequency of 200 Hz.
Column B represents the joint's angle in each walking trial, as depicted in Raw 1.


Joint angle direction

	Right	                                                   Left
	Flex	Ext	Abd	Add	Int Rot	 Ext Rot	   Flex	   Ext	   Abd	   Add	   Int Rot	Ext Rot
HIP	 +	 -	 -	 +	  +	    -	             +	    -	    +	    -	      -	           +
KNEE	 -	 +	 -	 +	  +	    -	            -	    +	    +	    -	      -	           +


	Dorsi-	  Plantar-	Inv	Eve	Int Rot	  Ext Rot  Dorsi-  Plantar-	   Inv	     Eve	Int Rot	   Ext Rot
ANKLE	  +	     -	         +	 -	   +	     -	     +	     -	            -	      +	           -	      +
   
