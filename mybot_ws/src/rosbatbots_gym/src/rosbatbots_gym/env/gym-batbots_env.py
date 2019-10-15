#/usr/bin/python

import rospy
import gym
import time
import copy 
from gym import utils , spaces
import tf
import numpy as np
from std_msgs.msg import Empty , String 
from geometry_msgs.msg import Pose , Twist
from sensor_msgs.msg import PointCloud

from gym.envs import registration as register
from gym.utils import seeding

#from src.rosbatbots_gym.gazeboconnection import GazeboConnection
from mybot_sonar import sonar_gen 

from rosbatbots_gym.gazeboconnection import GazeboConnection




reg = register.register(
    id = 'gymbatbotsEnv-V0',
    entry_point = 'rosbatbots_gym.env.gym-batbots_env:BatBotsEnv', 
)


class BatBotsEnv(gym.Env):
    def __init__(self):
        # action velocity that needs to published for sending the velocity info to the sim
        self.action_topic = "/cmd_vel"
        # action velocity pub
        self.vel_pub = rospy.Publisher(self.action_topic, Twist, queue_size=10)

        # defining the default velocity here it is the zero velocity
        # at rest or bring the robot to rest this velocity will be published  
        self.default_velocity = Twist()

        self.default_velocity.linear.x =0
        self.default_velocity.linear.y =0
        self.default_velocity.linear.z =0
        self.default_velocity.angular.x =0
        self.default_velocity.angular.y =0
        self.default_velocity.angular.z =0
        # actions timestep which the time for which the action selected is excuted
        self.action_timeStep = 0.5
        # actions velocity is the velocity at which selected action is excuted
        self.action_velocity = 0.05

        #common timeout constant that we wait for the data 
        self.timeout = 5
        
        #encoded actions
        self.straight = 0
        self.back = 1
        self.right = 2
        self.left = 3
        #param for calulating rewards
        # so it's good for the robot to stay from 4 to 6 units away from the wall
        # for the wall following behav not more not less 
        self.distance_fromWall = 5
        self.deltaDistance = 1
        # defining the the reward range
        self.reward_range = (-np.Inf , np.Inf)
        # defining the action_space
        self.action_space = spaces.Discrete(4)
        # storing the function pointer for the echo_genration
        self.echoes_genration = sonar_gen.echo_generation 
        # observation space is defined here
        self.observation_space = spaces.Box(low = -np.Inf , high = np.Inf , shape = (1,28000))

        # gazebo connection is established
        self.gazebo_pipe = GazeboConnection() 

        #storing the topic for the observation and reward signals
        # which is to be subscribed and read for getting the data from the sim
        self.observation_topic = '/mybot/polorcloud'
        self.rewardsignal_topic = 'mybot/closestdistance'
        self.collision_topic = 'mybot/collision'
        
        self.seed = self._seed()



    def _seed(self , seed = None):
        self.np_random , seed = seeding.np_random(seed) 
        return [seed]       

    def _step(self , action):

        # unpause the sim 
        self.gazebo_pipe.unpause()
        # velocity to be is selected according to the action variable
        self.velocity_toBe = copy.deepcopy(self.default_velocity)
        if (action == self.straight):
            self.velocity_toBe.linear.x = self.action_velocity
        else:
            if(action == self.back):
                self.velocity_toBe.linear.x = -self.action_velocity
            else:
                if(action == self.right):
                    self.velocity_toBe.angular.z = -self.action_velocity
                else:
                    if(action == self.left):
                        self.velocity_toBe.angular.z = self.action_velocity
        # publishing the selected velocity
        self.vel_pub.publish(self.velocity_toBe)
        # sleep for action time step
        rospy.sleep(self.action_timeStep)
        self.vel_pub.publish(self.default_velocity)
        
        echo , time  = get_observationEnv()

        reward = get_reward()
        # pause the sim 
        self.gazebo_pipe.pause()

        return echo , reward

    def get_observationEnv(self):
        Cloudobservation = None
        while Cloudobservation is None:
            try:
                Cloudobservation  = rospy.wait_for_message(self.observation_topic , PointCloud , timeout= self.timeout)
            except:
                rospy.loginfo("exception raised at getting observation of the polar cloud")
        
        echo_pulse,echo_time,_ = self.echoes_genration(Cloudobservation)

        return echo_pulse, echo_time

    def get_reward(self):
        pass

    
    def _reset(self):
        
        #resets the simulator to the default starting case
        self.gazebo_pipe.resetSim()
        #unpause the sim 
        self.gazebo_pipe.unpauseSim()
        #checks all the connections of the pub
        self.checkalltopics_pubConnections()
        #resetting velocities just in case
        self.reset_velocities()
        # getting the first observation
        observation = self.get_observationEnv()
        # the gazebo engine is paused 
        self.gazebo_pipe.pauseSim()
        
        return observation

    def reset_velocities(self):
        self.vel_pub.publish(self.default_velocity)
        rospy.sleep(self.action_timeStep)


    def checkalltopics_pubConnections(self):
        rate = rospy.Rate(10)
        
        while self.vel_pub.get_num_connections() == 0:
            rospy.loginfo("the vel_pub has zero connections so wait")
            rate.sleep(10)
        
        rospy.loginfo("velocity vel_pub connection with the gazebo sim is connected succesfully")
