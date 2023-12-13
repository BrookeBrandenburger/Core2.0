#!/bin/bash

# Start Server
echo "Starting Xpilots Server"
# switchBase 1 = 100% probability to swap bases on death, + teams disables teams
gnome-terminal -- ./xpilots -map simple.xp -noquit -switchBase 1.0 +teams -maxRoundTime 20 -roundsToPlay 0 -resetOnHuman 5 +limitedLives -maxClientsPerIP 10    
sleep 3
# Set the number of instances you want to run
num_instances=3

# Loop to run multiple instances
for ((i=1; i<=$num_instances; i++)); do
    echo "Running instance $i"
    gnome-terminal -- python3 core_controller.py "$i" &
    sleep 1  # Optional: Add a small delay between instances if needed
done

# Wait for all instances to finish
wait

echo "All $num_instances instances have been started."
