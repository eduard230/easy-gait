All data derived from the IMU system follow detail below;

- All lower limb segment orientation in x, y, z and w (Pelvic, Thigh (left/Right), Shank (left/Right), foot (left/Right), body.
- All lower limb segment access sensor in x, y, z (m/s^2) (Pelvic, Thigh (left/Right), Shank (left/Right), foot (left/Right).
- All lower limb segment acceleration in x, y, z (m/s^2) (Pelvic, Thigh (left/Right), Shank (left/Right), foot (left/Right).
- All lower limb segment shows the degree (deg) of course, pitch, roll, tilt, obliquity (in pelvic only), rotation (Pelvic, Thigh (left/Right), Shank (left/Right), foot (left/Right).
- All lower limb joint angle (Pelvic, Hip, Knee and Ankle) processing data from IMU are described in detail in CSV files available in the dataset.
A description of joint attitude in clinical use can be reported in three planes, i.e., the sagittal, coronal, and transverse anatomical planes of the body (Papi, 2012).  

- Each.csv file contains each walking trials.

For example, [OMC]01_walking1.csv is the file containing patient number 1's lower limb joint ankle for walking trial 1.

Below is a description of each file's contents:

Raw 1 denotes all parameters derived from IMU including 140 parameters.

Column A represents the number of measurement frames that were captured at a frequency of 200 Hz.

Column B and subsequent columns illustrate all parameter as indicated  in Raw 1.


lower limb segment acceleration direction

X axis
			up			down
Pelvis			+			-
Left Thigh		+			-
Left Shank		+			-
Right Thigh		+			-
Right Shank		+			-
			forward			backward
Left Foot		+			-
Right Foot		+			-


Y axis
			left			right
Pelvis			+			-
			forward			backward
Left Thigh		+			-
Left Shank		+			-
Right Thigh		-			+
Right Shank		-			+
			lateral 		medial
Left Foot		+			-
Right Foot		-			+

Z axis
			forward			backward			
Pelvis			-			+
			lateral 		medial
Left Thigh		+			-
Left Shank		+			-
Right Thigh		+			-
Right Shank 		+			-
			up			down
Left Foot		+			-
Right Foot 		+			-

				clockwise		counterclockwise
Pelvis course (deg) 		+			-			:related with vertical axis (x axis)
Pelvis pitch (deg)		+			-			:related with lateral axis (y axis)
Pelvis roll (deg)		+			-			:related with transverse axis (Z axis)
Left thigh course (deg)		+			-			:related with vertical axis (x axis)
Left thigh pitch (deg)		+			-			:related with lateral axis (y axis)
Left thigh roll (deg)		+			-			:related with transverse axis (Z axis)
Left shank course (deg)		+			-			:related with vertical axis (x axis)
Left shank pitch (deg)		+			-			:related with lateral axis (y axis)
Left shank roll (deg)		+			-			:related with transverse axis (Z axis)
Left foot course (deg)		+			-			:related with vertical axis (x axis)
Left foot pitch (deg)		+			-			:related with lateral axis (y axis)
Left foot roll (deg)		+			-			:related with transverse axis (Z axis)
Right thigh course (deg)	+			-			:related with vertical axis (x axis)
Right thigh pitch (deg)		+			-			:related with lateral axis (y axis)
Right thigh roll (deg)		+			-			:related with transverse axis (Z axis)
Right shank course (deg)	+			-			:related with vertical axis (x axis)
Right shank pitch (deg)		+			-			:related with lateral axis (y axis)
Right shank roll (deg)		+			-			:related with transverse axis (Z axis)
Right foot course (deg)		+			-			:related with vertical axis (x axis)
Right foot pitch (deg)		+			-			:related with lateral axis (y axis)
Right foot roll (deg)		+			-			:related with transverse axis (Z axis)

				left 			right
Pelvic Obliquity LT (deg)	+			-
Pelvic Rotation LT (deg)	+			-
Pelvic Obliquity RT (deg)	-			+
Pelvic Rotation RT (deg)	-			+

									hip extension 		hip flexion
Noraxon MyoMotion-Segments-Thigh LT-Tilt Fwd (deg)			+			-
Noraxon MyoMotion-Segments-Thigh RT-Tilt Fwd (deg)			+			-
									hip abduction 		hip adduction
Noraxon MyoMotion-Segments-Thigh LT-Tilt Med (deg)			+			-
Noraxon MyoMotion-Segments-Thigh RT-Tilt Med (deg)			+			-
									hip external rot. 	hip internal rot.
Noraxon MyoMotion-Segments-Thigh LT-Rotation Ext (deg) 			+			-
Noraxon MyoMotion-Segments-Thigh RT-Rotation Ext (deg)			+			-

									knee extension 		knee flexion
Noraxon MyoMotion-Segments-Shank LT-Tilt Fwd (deg)			-			+
Noraxon MyoMotion-Segments-Shank RT-Tilt Fwd (deg)			-			+
									knee abduction 		knee adduction
Noraxon MyoMotion-Segments-Shank LT-Tilt Med (deg)			+			-
Noraxon MyoMotion-Segments-Shank RT-Tilt Med (deg)			+			-
									knee external rot. 	knee internal rot.
Noraxon MyoMotion-Segments-Shank LT-Rotation Ext (deg)			+			-
Noraxon MyoMotion-Segments-Shank RT-Rotation Ext (deg)			+			-

									ankle dorsiflexion 	ankle plantarflexion
Foot Pitch Down LT (deg)						-			+ 		:related with lateral axis (y axis)
Foot Pitch Down RT (deg)						-			+ 		:related with lateral axis (y axis)
									ankle eversion 		ankle inversion
Foot Roll Med LT (deg)							+			- 		:related with vertical axis (x axis)
Foot Roll Med RT (deg)							+			- 		:related with vertical axis (x axis)
									ankle abduction 	ankle adduction
Foot Rotation Ext LT (deg)						+			- 		:related with transverse axis (Z axis)
Foot Rotation Ext RT (deg)						+			- 		:related with transverse axis (Z axis)


Joint angle direction

	Right	                                                   Left
	Flex	Ext	Abd	Add	Int Rot	 Ext Rot	   Flex	   Ext	   Abd	   Add	   Int Rot	Ext Rot
HIP	 +	 -	 -	 +	  +	    -	            +	    -	    +	    -	      -	           +
KNEE	 -	 +	 -	 +	  +	    -	            -	    +	    +	    -	      -	           +


	Dorsi-	  Plantar-	Inv	Eve	Int Rot	  Ext Rot  Dorsi-  Plantar-	   Inv	     Eve	Int Rot	   Ext Rot
ANKLE	  +	     -	         +	 -	   +	     -	     +	     -	            -	      +	           -	      +
   


