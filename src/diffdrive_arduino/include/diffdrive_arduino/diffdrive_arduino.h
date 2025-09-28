#ifndef DIFFDRIVE_ARDUINO_REAL_ROBOT_H
#define DIFFDRIVE_ARDUINO_REAL_ROBOT_H

#include <cstring>
#include "rclcpp/rclcpp.hpp"

#include <hardware_interface/handle.hpp>
#include <hardware_interface/hardware_info.hpp>
#include <hardware_interface/system_interface.hpp>
#include <rclcpp_lifecycle/state.hpp>
#include <hardware_interface/types/hardware_interface_return_values.hpp>

#include "config.h"
#include "wheel.h"
#include "arduino_comms.h"


using hardware_interface::CallbackReturn;
using hardware_interface::return_type;

namespace diffdrive_arduino
{

class DiffDriveArduino : public hardware_interface::SystemInterface
{


public:
  DiffDriveArduino();

  CallbackReturn on_init(const hardware_interface::HardwareInfo & info) override;

  std::vector<hardware_interface::StateInterface> export_state_interfaces() override;

  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

  CallbackReturn on_activate(const rclcpp_lifecycle::State & previous_state) override;

  CallbackReturn on_deactivate(const rclcpp_lifecycle::State & previous_state) override;

  return_type read(const rclcpp::Time & time, const rclcpp::Duration & period) override;

  return_type write(const rclcpp::Time & time, const rclcpp::Duration & period) override;
  



private:

  Config cfg_;
  ArduinoComms arduino_;

  Wheel l_wheel_;
  Wheel r_wheel_;

  rclcpp::Logger logger_;

  std::chrono::time_point<std::chrono::system_clock> time_;
  // double imu_ax_{0.0}, imu_ay_{0.0}, imu_az_{0.0};   // linear accel (m/s²)
  // double imu_gx_{0.0}, imu_gy_{0.0}, imu_gz_{0.0};   // angular vel (rad/s)
 double imu_orientation_[4] = {0.0, 0.0, 0.0, 1.0};  // simple identity quaternion
double imu_ax_, imu_ay_, imu_az_;
double imu_gx_, imu_gy_, imu_gz_;

  
};
} // namespace diffdrive_arduino

#endif // DIFFDRIVE_ARDUINO_REAL_ROBOT_H