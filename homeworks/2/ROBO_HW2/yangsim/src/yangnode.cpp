#include <chrono>
#include <memory>
#include <sstream>
#include <future>
#include <string>
#include <functional>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "rclcpp_components/register_node_macro.hpp"

#include "yinyang_interfaces/srv/datasrv.hpp"
#include "yinyang_interfaces/action/goodbye.hpp"
#include "std_msgs/msg/string.hpp"




using namespace std::chrono_literals;
using namespace std::placeholders;

using Bye = yinyang_interfaces::action::Goodbye;
using GoalHandle = rclcpp_action::ClientGoalHandle<Bye>;

    char* conv[] = {
      "Hi Yin, I am Yang the opposite of you.",
      "Yes, Yin; we ourselves, do not mean anything since we are only employed to express a relation",
      "Precisely, Yin; we are used to describe how things function in relation to each other and to the universe.",
      "For what is and what is not beget each other.",
      "High and low place each other.",
      "Before and behind follow each other.",
      "And you fade into the darkness."
    };


class YangNode : public rclcpp::Node
{
public:

    YangNode() : Node("yangnode")
    {
        

        this->declare_parameter("shout", false);

        
        yang_service = this->create_service<yinyang_interfaces::srv::Datasrv>(
          "yang_service",
          std::bind(&YangNode::yang_service_callback, this, _1, _2, _3)
        );

        

        yang_client = this->create_client<yinyang_interfaces::srv::Datasrv>("yin_service");
        
        
        timer = this->create_wall_timer(1s, std::bind(&YangNode::timer_callback, this));
        publisher_ = this->create_publisher<std_msgs::msg::String>("conversation", 10);                   
        action_client_yang_ = rclcpp_action::create_client<Bye>(this,"goodbye");
        
    }

private:

    int counter = 0;
    bool yin_cli_send_flag = false;
    
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;

   
    rclcpp::Client<yinyang_interfaces::srv::Datasrv>::SharedPtr yang_client;
    rclcpp::TimerBase::SharedPtr timer;
    rclcpp::Service<yinyang_interfaces::srv::Datasrv>::SharedPtr yang_service;

    rclcpp_action::Client<Bye>::SharedPtr action_client_yang_;


    void yang_service_callback(
            const std::shared_ptr<rmw_request_id_t> request_header,
            const std::shared_ptr<yinyang_interfaces::srv::Datasrv::Request> request,
            const std::shared_ptr<yinyang_interfaces::srv::Datasrv::Response> response)
    {
        
        std::stringstream pub_sent;
        pub_sent << "";
        pub_sent << request->a;
        RCLCPP_INFO(this->get_logger(), pub_sent.str().c_str()); // given conv from yin at first for every req
        
        int checksum = 0;
        for (int i = 0; i < (int)request->len; i++) {
          checksum += request->a[i];
        }
        response->checksum = checksum;
        auto message = std_msgs::msg::String();
        message.data = "Yin client masage: " + request->a + ", " + std::to_string(request->len) + ", " + std::to_string(checksum);

        publisher_->publish(message);
        this->yin_cli_send_flag = true;
    }

    void goal_response_callback(const GoalHandle::SharedPtr & goal_handle) {
      if (!goal_handle) {
        RCLCPP_ERROR(this->get_logger(), "Goal was rejected");
      } else {
        RCLCPP_INFO(this->get_logger(), "Goal accepted ");
      }
    }

    void feedback_callback(GoalHandle::SharedPtr, const std::shared_ptr<const Bye::Feedback> feedback) {
      
      std::stringstream ss;
      auto number = feedback->opacity;
      ss << number << " ";
      RCLCPP_INFO(this->get_logger(), ss.str().c_str());
    }

    void result_callback(const GoalHandle::WrappedResult & result) {
      switch (result.code) {
        case rclcpp_action::ResultCode::SUCCEEDED:
          break;
        case rclcpp_action::ResultCode::ABORTED:
          RCLCPP_ERROR(this->get_logger(), "Goal was aborted");
          return;
        case rclcpp_action::ResultCode::CANCELED:
          RCLCPP_ERROR(this->get_logger(), "Goal was canceled");
          return;
        default:
          RCLCPP_ERROR(this->get_logger(), "Unknown result code");
          return;
      }
      std::stringstream ss;
      ss << "Result received: ";
      ss << result.result->b;
      RCLCPP_INFO(this->get_logger(), ss.str().c_str());
      rclcpp::shutdown();
    }

    void timer_callback()
    {
      

      if (this->yin_cli_send_flag && this->counter != 7) {
        bool isshout = this->get_parameter("shout").get_parameter_value().get<bool>();
        auto req = std::make_shared<yinyang_interfaces::srv::Datasrv::Request>();
        

        
        std::string  yang_sent =conv[this->counter];
        
        req->a = yang_sent;
        req->len = std::strlen(conv[this->counter]);

        if (isshout) {
          req->a = "**" + yang_sent + "**";
          req->len = std::strlen(conv[this->counter]) + 4;
        } 

        this->counter = this->counter + 1;
        auto result_future = yang_client->async_send_request(req);
        this->yin_cli_send_flag = false;
        RCLCPP_INFO(this->get_logger(), "request sent");
      }

      if (this->counter == 7 ) {
        auto goal_msg = Bye::Goal();
        goal_msg.a = "Good bye";

        //RCLCPP_INFO(this->get_logger(), "Sending goal");

        auto send_goal_options = rclcpp_action::Client<Bye>::SendGoalOptions();

        send_goal_options.goal_response_callback =
          std::bind(&YangNode::goal_response_callback, this, _1);
        send_goal_options.feedback_callback =
          std::bind(&YangNode::feedback_callback, this, _1, _2);
        send_goal_options.result_callback =
          std::bind(&YangNode::result_callback, this, _1);
        this->action_client_yang_->async_send_goal(goal_msg, send_goal_options);

        
      
      }

    }
};  


int main(int argc, char* argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<YangNode>());
    
    rclcpp::shutdown();
    return 0;
}


