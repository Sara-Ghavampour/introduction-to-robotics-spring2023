#!/usr/bin/env python3

import random
import time
from functools import partial

import rclpy
from rclpy.node import Node
from std_msgs.msg import String,Int32
from turtlesim.srv import Spawn, Kill
from turtlesim.msg import Pose
from .util import *
class Spawner(Node):
    
    def __init__(self):
        super().__init__("spawner")

        self.killpublisher = self.create_publisher(Int32,'killtopic',10)
        self.deathnote_publisher_ = self.create_publisher(String,'death_note',10)
        self.death_notebook = []
        self.death_road= ' '
        self.turtle_num = 6
        self.name_prefix = "spawned_"
        self.turtle_map = dict()
        self.spawn_turtle()
        
        
        self.chaser_position_subscriber_ = self.create_subscription(Pose, "turtle1/pose", self.callback_chased, 10)
        
    def callback_chased(self, chaser_position):
        for name, pos in self.turtle_map.items():
            if name not in self.death_notebook and abs(chaser_position.x - pos[0]) < 0.5 and abs(chaser_position.y - pos[1]) < 0.5:
                self.kill_turtle(name)
                time.sleep(0.1)
                
                #todo: publish name of turtle and order of killing
                self.death_notebook.append(name)
                self.death_road+=" -> "+name+" "
                death_road_msg = String()
                death_name = String()
                death_name.data = name+" just got killed"
                death_road_msg.data = self.death_road
                self.deathnote_publisher_.publish(death_name)
                self.deathnote_publisher_.publish(death_road_msg)
                
        
    
    def kill_turtle(self, name):
         
            
            turtle_killer = self.create_client(Kill, "kill")
            
            turtle_to_kill = Kill.Request()
            turtle_to_kill.name = name
            
            future = turtle_killer.call_async(turtle_to_kill)
            future.add_done_callback(self.callback_killed_turtle)
            msg = Int32()
            msg.data=10
            self.killpublisher.publish(msg) # kill
            
        
    def callback_killed_turtle(self, future):
        try:
            self.get_logger().info("Chased the turtle!")
        except Exception as e:
            self.get_logger().error(e)
    
    def spawn_turtle(self):
        vertices = generate_polygon(center=(6, 6),
                            avg_radius=3,
                            irregularity=0,
                            spikiness=0,
                            num_vertices=6)

        for i in range(len(vertices)):
            
            spawner = self.create_client(Spawn, "spawn")
            while not spawner.wait_for_service(1.0):
                self.get_logger().warn("Waiting for the chaser to spawn..")
                
            turtle_to_spawn = Spawn.Request()
            turtle_to_spawn.x = vertices[i][0]
            turtle_to_spawn.y = vertices[i][1]
            turtle_to_spawn.theta = random.uniform(-3, 3)
            turtle_to_spawn.name = self.name_prefix + str(i)
            
            self.turtle_map[turtle_to_spawn.name] = vertices[i]
            
            future = spawner.call_async(turtle_to_spawn)
            future.add_done_callback(partial(self.future_callback, spawned_x=turtle_to_spawn.x, spawned_y=turtle_to_spawn.y))
        
    def future_callback(self, future, spawned_x, spawned_y):
        try:
            response = future.result()
            self.get_logger().info(f"Spawned {response.name} ==> x: {spawned_x}, y: {spawned_y}")
        except Exception as e:
            self.get_logger().error(e);               

def main(args=None):
    rclpy.init(args=args)
    spawner_node = Spawner()
    rclpy.spin(spawner_node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()



