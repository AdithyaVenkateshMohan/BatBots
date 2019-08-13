#!/usr/bin/env python


# topic that need to be subcribed is a point cloud /mybot/laser/pointcloud2
# point cloud2 will have the x,y,z which have to be converted into polar co-ordinates
# then given to the sonar signal simlator to get the signal
# this block of code is meant to be written in python 3
#
# 


# importing below required libaries
import rospy 
import pcl 
from sensor_msgs.msg import PointCloud 
from geometry_msgs.msg import Point 

import sensor_msgs.point_cloud2 as pc2


import numpy
from matplotlib import pyplot
from scipy.interpolate import interp1d
import library




#callback on reciving the pointcloud data
def callback(data):
    
    #pc = pc2.read_points(data, skip_nans = True)
    
    pc_list = []
    #for p in pc :
    #    pc_list.append([p[0], p[1], p[2] , p[4]])
    
    pc_list = data.points
    intensity_list = data.channels

    echo_sequence , impulse_time = echo_genration(pc_list)

    pyplot.figure(1)
    pyplot.plot(impulse_time, echo_sequence)
    pyplot.draw()
    pyplot.pause(0.00000002)
    pyplot.clf()
    pyplot.cla()

def echo_genration(pc_list):
    #param for the echo generation
    sample_frequency = 250000
    emission_level = 100
    emission_duration = 0.0025
    emission_frequency = 40000
    emitter_radius = 0.005
    absorption_coefficient = 1.318  # http://www.sengpielaudio.com/calculator-air.htm
    reflection_strength = -40
    speed_of_sound = 340

    ##### this is where i can give the input 
    azimuths = numpy.array([])
    elevations = numpy.array([])
    distances = numpy.array([])
    print("single point", pc_list[0])
    for p in pc_list:
        #print(p)
        distances = numpy.append(distances, p.x)
        azimuths = numpy.append(azimuths, p.y)
        elevations = numpy.append(elevations, p.z)

    # if not we didn't recive any points    
    assert(distances.size > 0)


    emission_samples = int(sample_frequency * emission_duration)
    emission_time = numpy.linspace(0, emission_duration, emission_samples)
    emission = numpy.sin(2 * numpy.pi * emission_frequency * emission_time)
    window = library.signal_ramp(emission_samples, 10)
    emission = emission * window

    # pyplot.figure()
    # pyplot.plot(emission)

    # %%
    # Make piston model (model of emitter directionality)

    piston, degrees = library.pistonmodel(emission_frequency, radius=emitter_radius)
    piston = 10 * numpy.log10(piston)
    piston_function = interp1d(degrees, piston)

    # pyplot.figure()
    # pyplot.plot(degrees, piston)

    # %%
    # Get excentricities and echo delays

    excentricities = library.gca(azimuths, elevations, 0, 0)
    # @causing errors is this too  long for 
    delays = 2 * distances / speed_of_sound

    # %%
    # Calculate path losses

    loss_directionality = piston_function(excentricities)
    loss_attenuation = - 2 * distances * absorption_coefficient
    loss_spreading = -40 * numpy.log10(distances)

    echoes = emission_level + reflection_strength + loss_directionality + loss_attenuation + loss_spreading
    echoes_pa = library.db2pa(echoes)
    echoes_pa[echoes < 0] = 0

    # %%
    # Make impulse response

    impulse_time, impulse_response = library.make_impulse_response(delays, echoes_pa, emission_duration, sample_frequency)

    # pyplot.figure()
    # pyplot.plot(impulse_time, impulse_response)

    # %%
    # Make echo sequence

    echo_sequence = numpy.convolve(emission, impulse_response, mode='same')
    return echo_sequence , impulse_time
    





def listener3d():
    #creates  a node called peeker to process the 
    
    pyplot.show()
    pyplot.ion()
    rospy.init_node("peeker", anonymous = True)
    #subscribing to the pointcloud data which is published  
    rospy.Subscriber("/mybot/laser/polorcloud", PointCloud, callback)
    rospy.spin() #keeps the python from exciting until the node stopped



if __name__ == "__main__":
    try:
        listener3d()
    except rospy.ROSInterruptException:
        pass



    
    