
#include <ignition/math/Pose3.hh>
#include <ignition/math/Rand.hh>
#include <gazebo/physics/physics.hh>

#include <geometry_msgs/Point.h>
#include <geometry_msgs/Quaternion.h>

// include files for ros
#include <ros/ros.h>
#include "geometry_msgs/Pose.h"
#include "gazebo_rosPosePublisher/PosePublisher.hh"

using namespace gazebo;

GZ_REGISTER_MODEL_PLUGIN(PosePub)

PosePub::PosePub()
{

    ROS_INFO("Pose publisher  is  about to be switched on");

}


PosePub::~PosePub()
{
  this->pose_queue_.clear();
  this->pose_queue_.disable();
  this->rosnode->shutdown();
  this->callback_pose_queue_thread_.join();
  delete this->rosnode;
}


void PosePub::Load(physics::ModelPtr _model , sdf::ElementPtr _sdf)
{
    this-> model = _model;
    this->sdf = _sdf;

    if (!_sdf->HasElement("frameName"))
  {
    ROS_INFO_NAMED("block_laser", "Block laser plugin missing <frameName>, defaults to /world");
    this->frame_name_ = "/world";
  }
  else
    this->frame_name_ = _sdf->GetElement("frameName")->Get<std::string>();

  if (!_sdf->HasElement("topicName"))
  {
    ROS_INFO_NAMED("block_laser", "Block laser plugin missing <topicName>, defaults to /world");
    this->topic_name_ = "/world";
  }
  else
    this->topic_name_ = _sdf->GetElement("topicName")->Get<std::string>();

 this->connections.push_back(event::Events::ConnectWorldUpdateBegin(std::bind(&PosePub::onUpdate, this)));

 

    //// ros side of the functions

    this->rosnode = new ros::NodeHandle("posePub");
    ros::AdvertiseOptions ao = ros::AdvertiseOptions::create<geometry_msgs::Pose>(
                                this->topic_name_ ,100 ,boost::bind(&PosePub::PoseConnect, this),boost::bind(&PosePub::PoseDisconnect, this),ros::VoidPtr(), &this->pose_queue_ );
  
    this->pub_ = this->rosnode->advertise(ao);

    this->callback_pose_queue_thread_ = boost::thread( boost::bind( &PosePub::PoseQueueThread,this ) );
}

void PosePub::onUpdate()
{
    ignition::math::Pose3d pose = this->model->GetWorldPose().Ign();

    // geometry_msgs::Point p_ = new geometry_msgs::Point((float) pose.Pos().X(),
    //                             (float) pose.Pos().Y(),
    //                             (float) pose.Pos().Z());

    // geometry_msgs::Quaternion q_ = new geometry_msgs::Quaternion(pose.Rot().X(),
    //                             pose.Rot().Y(),
    //                             pose.Rot().Z(),
    //                             pose.Rot().W()) ;



    // pose_ = new geometry_msgs::Pose( p_ , q_);

    pose_.position.x = pose.Pos().X();
    pose_.position.y = pose.Pos().Y();
    pose_.position.z = pose.Pos().Z();

    pose_.orientation.x = pose.Rot().X();
    pose_.orientation.y = pose.Rot().Y();
    pose_.orientation.z = pose.Rot().Z();
    pose_.orientation.w = pose.Rot().W();

    this->pub_. publish(pose_);

}

void PosePub::PoseConnect()
{
  ROS_INFO("pose publisher under topic name " );

}


void PosePub::PoseDisconnect()
{
    ROS_INFO("pose publisher stopped" );
}

void PosePub::PoseQueueThread()
{
  static const double timeout = 0.01;

  while (this->rosnode->ok())
  {
    this->pose_queue_.callAvailable(ros::WallDuration(timeout));
  }
}