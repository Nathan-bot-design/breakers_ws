#ifndef DIFFDRIVE_ARDUINO_H
#define DIFFDRIVE_ARDUINO_H

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

  // =========================
  // IMU state variables
  // =========================
  double imu_orientation_x_;
  double imu_orientation_y_;
  double imu_orientation_z_;
  double imu_orientation_w_;

  double imu_angular_vel_x_;
  double imu_angular_vel_y_;
  double imu_angular_vel_z_;

  double imu_linear_acc_x_;
  double imu_linear_acc_y_;
  double imu_linear_acc_z_;
};

} // namespace diffdrive_arduino

#endif // DIFFDRIVE_ARDUINO_H
