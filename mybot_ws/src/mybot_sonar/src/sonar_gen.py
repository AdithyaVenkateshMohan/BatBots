#!/usr/bin/env python


# topic that need to be subcribed is a point cloud /mybot/laser/pointcloud2
# point cloud2 will have the x,y,z which have to be converted into polar co-ordinates
# then given to the sonar signal simlator to get the signal
# this block of code is meant to be written in python 2.7
# 


# importing below required libaries
import rospy 
import pcl 
from sensor_msgs.msg import PointCloud 
from geometry_msgs.msg import Point 

import sensor_msgs.point_cloud2 as pc2


#callback on reciving the pointcloud data
def callback(data):
    
    #pc = pc2.read_points(data, skip_nans = True)
    
    pc_list = []
    #for p in pc :
    #    pc_list.append([p[0], p[1], p[2] , p[4]])
    
    pc_list = data.points
    intensity_list = data.channels
    rospy.loginfo(rospy.get_caller_id()+"points are " + "data")
    rospy.loginfo(pc_list)
    rospy.loginfo(intensity_list)





def listener3d():
    #creates  a node called peeker to process the 
    rospy.init_node("peeker", anonymous = True)
    #subscribing to the pointcloud data which is published  
    rospy.Subscriber("/mybot/laser/pointcloud2", PointCloud, callback)
    rospy.spin() #keeps the python from exciting until the node stopped



if __name__ == "__main__":
    try:
        listener3d()
    except rospy.ROSInterruptException:
        pass

