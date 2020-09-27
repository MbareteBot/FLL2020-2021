#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Stop, Direction, Button
from pybricks.tools import wait, DataLog

from pybricks.iodevices import Ev3devSensor

from control import PIDSystem

import csv
import math


ev3 = EV3Brick()


#ReadSensorData = open('SensorData.txt', 'r')

SensorValues = [] 

class Robot:

    def __init__(self):
        
        
        self.left_steeringMotor = 0
        self.right_steeringMotor = 0
        self.letf_mainMotor = 0
        self.right_mainMotor = 0

        self.gyro_direction = 1
        self.motor_direction = Direction.CLOCKWISE

        self.left_motor_degrees = 0
        self.last_right_motor_degrees =  0
        
        self.gyroSensor = 0
        self.left_colorSensor = 0
        self.right_colorSensor = 0
        self.top_colorSensor = 0

        self.error_log = []
        self.MotorsAverageDegrees = 0
        
        self.kp_value = 0
        self.ki_value = 0
        self.kd_value = 0
        self.integral_value = 0
        self.derivative_value = 0
        self.error_value = 0
        self.last_error_value = 0
        self.pid_output = 0

        self.speedMotorA = 0
        self.speedMotorD = 0
        self.MotorsAverageSpeed = 0


        self.global_x_pos = 0
        self.global_y_pos = 0

        self.target_x_pos = []
        self.target_y_pos = []

        self.robot_moves = 0
        

    def setSteeringMotors(self, left_motor_port, right_motor_port, set_inverse_direction = False):

        if set_inverse_direction:
            self.motor_direction = Direction.COUNTERCLOCKWISE

        self.left_steeringMotor = Motor(left_motor_port, Direction.COUNTERCLOCKWISE)
        self.right_steeringMotor = Motor(right_motor_port, Direction.COUNTERCLOCKWISE)

    def setGyroSensor(self, port, inverse_direction = False):
        
        if inverse_direction:
            self.gyro_direction = -1
        
        self.gyroSensor = Ev3devSensor(port)


    def setColorSensor(self, port_left, port_right, port_top):

        self.left_colorSensor = ColorSensor(port_left)
        self.right_colorSensor = ColorSensor(port_right)
        self.top_colorSensor = ColorSensor(port_top)


    def LineSquaring(self):
        NotSkip = True
        SpeedMotorA = 300
        SpeedMotorD = 300

        Fase2Degrees = -150
        Running = True

        light_data = open("SensorData.txt","r")
        sensor_register = light_data.readlines()
        White = int(sensor_register[0])
        print("Color>",White)
        Fase = 0

        while Running:

            Checking = True
            NotSkip = True
            self.left_steeringMotor.run(SpeedMotorA)
            self.right_steeringMotor.run(SpeedMotorD)

            if self.left_colorSensor.reflection() >= White and NotSkip:
                self.left_steeringMotor.hold()
                while Checking:
                    self.right_steeringMotor.run(SpeedMotorD)
                    if self.right_colorSensor.reflection() > White:
                        self.right_steeringMotor.hold()

                        Fase += 1

                        if Fase == 2:
                            Running = False
                        else:
                            self.left_steeringMotor.run_angle(Fase2Degrees, 100, wait = False)
                            self.right_steeringMotor.run_angle(Fase2Degrees, 100)
                            ev3.speaker.beep()                        
                            ev3.speaker.beep()

                        NotSkip = False
                        Checking = False

                        SpeedMotorA = 300
                        SpeedMotorD = 300
                            

            elif self.right_colorSensor.reflection() >= White and NotSkip:
                self.right_steeringMotor.hold()

                while Checking:
                    self.left_steeringMotor.run(SpeedMotorA)
                    if self.left_colorSensor.reflection() > White:
                        self.left_steeringMotor.hold()

                        Fase += 1

                        if Fase == 2:
                            Running = False
                        else:
                            self.left_steeringMotor.run_angle(Fase2Degrees, 100, wait = False)
                            self.right_steeringMotor.run_angle(Fase2Degrees, 100)
                            ev3.speaker.beep()
                        
                        NotSkip = False
    
                        Checking = False
                        SpeedMotorA = 300
                        SpeedMotorD = 300

        self.left_steeringMotor.hold()
        self.right_steeringMotor.hold()

        wait(300)



    def Turn(self, target_angle):

        self.left_steeringMotor.reset_angle(0)
        self.right_steeringMotor.reset_angle(0)
        self.gyroSensor.read("GYRO-CAL")

        target_angle_encoders = target_angle * 1.95
        acc_rate = round(target_angle_encoders / (ev3.battery.voltage() * 0.01)) * 1
        print(acc_rate)

        
        self.left_motor_degrees = (self.left_steeringMotor.angle() * (6.24 * math.pi)) / 360
        self.last_right_motor_degrees = (self.right_steeringMotor.angle() * (6.24 * math.pi)) / 360

        max_integral_value = 100
        Turning = True


        Control = PIDSystem()


        Control.reset()

        while Turning:

            error_value = target_angle - int(self.gyroSensor.read("GYRO-ANG")[0]) * self.gyro_direction

            Control.setPID(error_value, 0.15, 0.8, 0.1)

            self.left_steeringMotor.dc(Control.pid_output)
            self.right_steeringMotor.dc(Control.pid_output * -1)


            if  Control.error_value > -0.1 and Control.error_value < 0.1:
                Turning = False
                self.speedMotorA = 0
                self.speedMotorD = 0
            

        self.right_steeringMotor.hold()
        self.left_steeringMotor.hold()
        wait(100)
        #self.updatePos()
        print("\n---Turn---")
        print("\nTarget:",target_angle)
        print("Gyro:", self.gyroSensor.read("GYRO-ANG")[0])



    def Move(self, target_distance_user, target_orientation, target_duty_limit, use_gyro=False):

        self.left_steeringMotor.reset_angle(0)
        self.right_steeringMotor.reset_angle(0)
        
        target_distance_cm = target_distance_user
        target_distance = round((target_distance_user / (6.24 * math.pi)) * 360)
        print("Target:",target_distance)
        
        self.MotorsAverageDegrees = (self.left_steeringMotor.angle() + self.right_steeringMotor.angle()) / 2

        MotorOffset = 10
        
        Running = True
        
        speed_kp = round(target_distance/ev3.battery.voltage()*0.1,3)
        print("KP:",speed_kp)
        speed_ki = 0.1
        speed_kd = 0.2
        speed_error = 0
        speed_integral = 0
        speed_derivative = 0
        speed_last_error = 0
        speed_output = 0
        max_integral_value = 120

        self.left_steeringMotor.reset_angle(0)
        self.right_steeringMotor.reset_angle(0)

        MovedEnough = False
        StopDiagnostic = "Reached Distance Target"
        print(target_distance,ev3.battery.voltage())

        Correction_target_distance = 100

        self.left_motor_degrees = (self.left_steeringMotor.angle() * (6.24 * math.pi)) / 360
        self.last_right_motor_degrees = (self.right_steeringMotor.angle() * (6.24 * math.pi)) / 360

        while Running:


            self.MotorsAverageSpeed = (self.left_steeringMotor.speed() + self.right_steeringMotor.speed()) / 2
            self.MotorsAverageDegrees = (abs(self.left_steeringMotor.angle()) + abs(self.right_steeringMotor.angle())) / 2
            
            
            
            
            if use_gyro:

                error_value = target_orientation - self.gyroSensor.angle()
                kp_value = 4
                ki_value = 0.001
                kd_value = 0.1
        
            else:

                error_value = self.right_steeringMotor.speed() - self.left_steeringMotor.speed()
                kp_value = 0.2
                ki_value = 0.001
                kd_value = 0.01


            Control.setPID(error_value, kp_value, ki_value, kd_value)


            if target_distance > 0:

                speed_error = target_distance - self.right_steeringMotor.angle()

                if speed_output < 8:
                    speed_output = 8 


            else:

                speed_error = target_distance - (target_distance - (self.right_steeringMotor.angle()))

                if speed_output > -8:
                    speed_output = -8



            if speed_integral > max_integral_value:
                speed_integral = max_integral_value

            elif speed_integral < -max_integral_value:
                speed_integral = -max_integral_value


            speed_integral += speed_error
            speed_derivative = speed_error - speed_last_error
            speed_output = (speed_error * speed_kp) + (speed_integral * speed_ki) + (speed_derivative * speed_kd)      

            if target_orientation > 0:
                self.left_steeringMotor.dc(speed_output + target_orientation)
                self.right_steeringMotor.dc(speed_output)

            elif target_orientation < 0:
                self.left_steeringMotor.dc(speed_output)
                self.right_steeringMotor.dc(speed_output + abs(target_orientation))

            else:
                self.left_steeringMotor.dc(speed_output + self.pid_output)
                self.right_steeringMotor.dc(speed_output)


                                                         


            # if target_distance < 0:

            #     if self.right_steeringMotor.angle() > target_distance/2:
            #         speed_error = target_distance - (target_distance - (self.right_steeringMotor.angle()))
            #     else:
            #         speed_error = target_distance - (self.right_steeringMotor.angle())

            #     if speed_integral < -120:
            #         speed_integral = -120


            #     if -self.MotorsAverageDegrees <= (target_distance * Correction_target_distance)/ 100:
            #         Running = False


            #     if self.MotorsAverageSpeed < -100 and MovedEnough == False:
            #         MovedEnough = True

            #     if self.MotorsAverageSpeed > -abs(target_duty_limit) and MovedEnough:
            #         Running = False
            #         StopDiagnostic = "Got Stalled" 

            #     if speed_output > -8:
            #         speed_output = -10               

                
            # else:

            #     if self.right_steeringMotor.angle() < target_distance/2:
            #         speed_error = target_distance - (target_distance - (self.right_steeringMotor.angle()))
            #     else:
            #         speed_error = target_distance - (self.right_steeringMotor.angle())

            #     if speed_integral > 120:
            #         speed_integral = 120


            #     if self.MotorsAverageDegrees >= (target_distance * Correction_target_distance)/ 100:
            #         Running = False


            #     if self.MotorsAverageSpeed > 100 and MovedEnough == False:
            #         MovedEnough = True

            #     if self.MotorsAverageSpeed < target_duty_limit and MovedEnough:
            #         Running = False
            #         StopDiagnostic = "Got Stalled" 

            #     if speed_output < 8:
            #         speed_output = 10




        self.left_steeringMotor.hold()
        self.right_steeringMotor.hold()
        wait(250)
       
        print("\n---Move Straight---")
        print("\nTarget:", target_distance)
        print("Motor Degrees:", round(abs(self.left_steeringMotor.angle() + self.right_steeringMotor.angle())/2))
        print("Diagnostic:", StopDiagnostic)
        print("Motor Precision:", round(abs(((self.MotorsAverageDegrees * 100)/target_distance)), 1), "%")
        print("self.gyroSensor:", self.gyroSensor.angle())
        print("\n---Move Straight---")




    def RegularMove(target_distance_cm, target_speed, target_duty_limit):

        target_distance_cm = round((target_distance_cm / (6.24 * math.pi)) * 360)
        target_speed = abs(target_speed)
        target_duty_limit = abs((target_duty_limit * 800) / 100)
        self.left_steeringMotor.reset_angle(0)
        self.right_steeringMotor.reset_angle(0)

        if target_distance_cm < 0:
            target_speed *= -1
            target_duty_limit *= -1

        
        StopDiagnostic = "Reached Distance Target"

        MotorOffset = 10
        Running = True
        MovedEnough = False
        target_orientation = 0

        while Running:

            self.MotorsAverageDegrees = (self.left_steeringMotor.angle() + self.right_steeringMotor.angle()) / 2
            self.MotorsAverageSpeed = (self.left_steeringMotor.speed() + self.right_steeringMotor.speed()) / 2

            Error = (self.left_steeringMotor.angle() - self.right_steeringMotor.angle()) * 0.5

            if target_distance_cm < 0:
                Error *= -1


            target_orientation = 0


            Robot.drive(target_speed, target_orientation)

            print("Error:", Error)
            print("Speed self.left_steeringMotor:", self.left_steeringMotor.speed())
            print("Speed self.right_steeringMotor:", self.right_steeringMotor.speed())

            if target_distance_cm > 0:

                if self.MotorsAverageDegrees >= target_distance_cm - MotorOffset:
                    Running = False

                if self.MotorsAverageSpeed > 250:
                    MovedEnough = True

                elif self.MotorsAverageSpeed < target_duty_limit and MovedEnough:
                    Running = False
                    StopDiagnostic = "Got Stalled"         
    
            else:

                if self.MotorsAverageDegrees <= target_distance_cm + MotorOffset:
                    Running = False

                if self.MotorsAverageSpeed < -250:
                    MovedEnough = True

                if self.MotorsAverageSpeed > target_duty_limit  and MovedEnough:
                    Running = False
                    StopDiagnostic = "Got Stalled"



        Robot.stop()

        print("\n--MoveToStall--\n")
        print("Target:", target_distance_cm)
        print("Motor Degrees:", self.left_steeringMotor.angle())
        print("Diagnostic:", StopDiagnostic)
        print("self.gyroSensor:", self.gyroSensor.angle())
        print("\n--MoveToStall--")


    def LightSensorCalibration(self):

        WhiteColorValue = 70
        BlackColorValue = 15
        Speed = 200
        Running = True
        ev3.speaker.beep()
        while Running:
        
            if any(ev3.buttons.pressed()):

                while Running:

                    self.left_steeringMotor.run(Speed)
                    self.right_steeringMotor.run(Speed)

                    if self.left_colorSensor.reflection() > WhiteColorValue:
                        self.left_steeringMotor.hold()
                        while Running:
                            self.right_steeringMotor.run(Speed)
                            if self.right_colorSensor.reflection() > WhiteColorValue:
                                self.right_steeringMotor.hold()
                                WhiteColorValue = round(self.left_colorSensor.reflection())
                                wait(200)

                                while Running:
                                    self.left_steeringMotor.run(Speed)
                                    self.right_steeringMotor.run(Speed)
                                    if self.left_colorSensor.reflection() < BlackColorValue:
                                        self.left_steeringMotor.hold()
                                        while Running:
                                            self.right_steeringMotor.run(Speed)
                                            if self.right_colorSensor.reflection() < BlackColorValue:
                                                self.right_steeringMotor.hold()
                                                BlackColorValue = round(self.left_colorSensor.reflection())
                                                wait(200)
                                                Running = False


                ev3.screen.print(WhiteColorValue, BlackColorValue)
                SensorData = DataLog(name = 'SensorData', timestamp = False, extension = 'txt')
                SensorData.log(WhiteColorValue)
                SensorData.log(BlackColorValue)


    def LineFollower(WhiteColorValue, BlackColorValue):
        LineTarget = (WhiteColorValue) / 2
        self.gyroSensor.reset_angle(0)
        Running = True

        Heading = 0
        Error = 0
        Speed = 50


        while Running:

            Robot.drive(Speed, Heading)

            Error = (LineTarget - self.left_colorSensor.reflection()) * 0.05

            Heading = (Error - self.gyroSensor.angle()) * 0.5

        for line in ReadSensorData:
                                
            reading_check = line[:-1]

            SensorValues.append(reading_check)

        TargetDegrees = 80
        #AdvancedMove(30,0,20,False)
        #Turn(90, False)


        Register = DataLog("Target", "Motor", "FinalOrientation")                                                                                                                                                                                                                                                                                                                                                                                                                                


    def CheckDevices(self):


        self.motors_devices = [self.left_steeringMotor,self.right_steeringMotor,
                                self.letf_mainMotor,self.right_mainMotor]


        self.sensor_devices = [self.gyroSensor, self.left_colorSensor, 
                                self.right_colorSensor, self.top_colorSensor]



        for motors in range(0,len(self.motors_devices)):

            if self.motors_devices[motor] != 0:

                try:
                    self.motors_devices[motor].reset_angle(0)
                    print("Motor", self.motors_devices[motor], " = OK")

                except IOError:
                    print("Motor",  self.motors_devices[motor], " = ERROR")



        for sensor in range(0, len(self.sensor_devices)):

            if self.sensor_devices[sensor] != 0:

                try:
                    #self.sensor_devices[sensor].read("")
                    print("Motor", self.motors_devices[motor], " = OK")

                except IOError:
                    print("Motor",  self.motors_devices[motor], " = ERROR")



        
                
                


    def pathRun(self):
        RobotValues_txt = []

        with open("RobotValues.txt") as f:

            for line in f:
                                
                RobotValues_txt_Check = line[:-2]

                RobotValues_txt.append(RobotValues_txt_Check)

        print("\n---Robot Data---\n")    
        print(RobotValues_txt)
        print("Total Moves:", len(RobotValues_txt))
        print("\n---Robot Data---")    

        Index = 0
        Counter = 0
        for i in range(len(RobotValues_txt)):

            self.Move((float(RobotValues_txt[Index]) * 100)/100 , 0, 20)
            Counter += 1
            Index += 1

            if Counter < len(RobotValues_txt) - 1:
                self.Turn(float(RobotValues_txt[Index])*-1)

            else:
                break

            Counter += 1
            Index += 1

        ev3.speaker.beep()  