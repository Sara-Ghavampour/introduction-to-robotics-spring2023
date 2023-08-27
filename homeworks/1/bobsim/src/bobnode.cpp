#include <chrono>
#include <functional>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/char.hpp"

using namespace std::chrono_literals;

/* This example creates a subclass of Node and uses std::bind() to register a
* member function as a callback from the timer. */

class MinimalPublisher : public rclcpp::Node
{
  public:
    MinimalPublisher()
    : Node("bobnode"),count_(0)
    {
      publisher_ = this->create_publisher<std_msgs::msg::Char>("topic", 10);
      timer_ = this->create_wall_timer(
      500ms, std::bind(&MinimalPublisher::timer_callback, this));
    }

  private:

    char encrypt(char input){
        char key [] = "9812762781";
        int key_idx = count_ % strlen(key);
        return key[key_idx]^input;
    }
    void timer_callback()
    {
      char str_array[]="SEND_HELP!#"  ;
      auto message = std_msgs::msg::Char();
      message.data = encrypt(str_array[count_]) ;
      RCLCPP_INFO(this->get_logger(), "Publishing: '%c'", message.data);
      publisher_->publish(message);
      if(str_array[count_]=='#'){count_=-1;}
      count_++;
    
    }
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<std_msgs::msg::Char>::SharedPtr publisher_;
    size_t count_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MinimalPublisher>());
  rclcpp::shutdown();
  return 0;
}