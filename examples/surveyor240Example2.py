# Import the Surveyor module
from brping import Surveyor240
from brping import definitions

# To create a Surveyor object:
# mySurveyor240 = Surveyor240()

# Create a Surveyor object, log to folder in same directory as script
mySurveyor240 = Surveyor240(logging=True, log_directory="logs/surveyor")

# The Surveyor typically uses a TCP connection. connect_tcp() expects a string ip and int port
# The default address and port combination for the Surveyor is 192.168.2.86:62312
ip = "192.168.2.86"
port = 62312

# Initialize TCP connection with the Surveyor
mySurveyor240.connect_tcp(ip, port)

# Initialize communication with the device
if mySurveyor240.initialize() is False:
    print("Failed to initialize Surveyor!")
    # Close socket before exiting
    try:
        mySurveyor240.iodev.close()
    except Exception as e:
        print(f"Failed to close socket: {e}")
    exit(1)

# To determine the milliseconds per ping from a ping rate
ping_rate = 10 # 10 pings per second
my_msec_per_ping = Surveyor240.calc_msec_per_ping(ping_rate)

# To set ping parameters on the Surveyor, use control_set_ping_parameters()
# https://docs.ceruleansonar.com/c/surveyor-240-16/application-programming-interface/set_ping_parameters
mySurveyor240.control_set_ping_parameters(
    end_mm=0,       # Set to 0 to let Surveyor track range dynamically
    msec_per_ping=my_msec_per_ping,
    ping_enable=1,
    enable_atof_data=1
)

# To stop logging
mySurveyor240.stop_logging()
print(f"Is logging: {mySurveyor240.logging}")

# To start logging
mySurveyor240.start_logging(new_log=True)
print(f"Is logging: {mySurveyor240.logging}")

# Keep track of the max table length for readability in the console
atof_table_max_rows = 0


# Collect data from the device, CTRL-C to exit while loop
while True:
    try:
        data = mySurveyor240.wait_message([definitions.SURVEYOR240_ATOF_POINT_DATA])
        if data:
            # Access packet fields like any other attribute
            print(f"Ping Number: {data.ping_number}")
            
            # Use the atof list function to create a list of atof_t structs
            atof_list = mySurveyor240.create_atof_list(data)
            atof_table_max_rows = max(atof_table_max_rows, len(atof_list))

            # Print the table with padding
            print(f"{'Index':<6} {'Angle (rad)':>15} {'TOF (s)':>15}")
            print("-" * 36)

            for i in range(atof_table_max_rows):
                if i < len(atof_list):
                    print(f"{i:<6} {atof_list[i].angle:>15.6f} {atof_list[i].tof:>15.6f}")
                else:
                    # Print empty row to maintain height
                    print(f"{'':<6} {'':<15} {'':<15}")


        else:
            print("Bad packet")
    except KeyboardInterrupt:
        break

# Use the atof list function to create a list of atof_t structs
atof_list = mySurveyor240.create_atof_list(data)
print(f"atof_list[0] = {atof_list[0]}")

# To stop pinging
mySurveyor240.control_set_ping_parameters(ping_enable=0)

# Close socket before exiting
try:
    mySurveyor240.iodev.close()
except Exception as e:
    print(f"Failed to close socket: {e}")
