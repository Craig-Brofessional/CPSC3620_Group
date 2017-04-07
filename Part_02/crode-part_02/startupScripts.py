import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.igext as IG

NUM_COMPUTE_CORES = 3
NUM_FILE_SYSTEM_CORES = 3
NUM_TOTAL_CORES = NUM_COMPUTE_CORES + NUM_FILE_SYSTEM_CORES + 1
BASE_IP = "192.172.1."

pc = portal.Context()
request = rspec.Request()

params = pc.bindParameters()

tourDescription = "This profile provides a small HPC system similar to the EXSEDE " \
 + "- Gordon system. As I was working alone, this only replicates the file system " \
 + "(NFS) and the scheduler (Torque)."

#
# Setup the Tour info with the above description
#  
tour = IG.Tour()
tour.Description(IG.Tour.TEXT,tourDescription)
request.addTour(tour)

# Create a link with type LAN
link = request.LAN("lan")

# Generate the nodes
for i in range(NUM_TOTAL_CORES):
    node = request.RawPC("node" + str(i))
    node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU14-64-STD"
    
    iface = node.addInterface("if" + str(i))
    iface.component_id = "eth1"
    iface.addAddress(rspec.IPv4Address(BASE_IP + str(i + 1), "255.255.255.0"))
    link.addInterface(iface)
    
    # Command 0
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo apt-get update"))
    
    if i == 0:
        # Command 1 (Setup NFS Server)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo apt-get -y -f install nfs-kernel-server "))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="echo '/home *(rw,sync,no_root_squash)' | sudo tee -a /etc/exports"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo service nfs-kernel-server restart"))
        # Command 4 (Install libraries for code execution)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo apt-get -y -f install python python-dev python-pip python-numpy"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo apt-get -y -f install openmpi-bin libopenmpi-dev"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo pip install mpi4py"))
        
        # Command 7 (Setup torque)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo apt-get -y -f install torque-server torque-client torque-mom torque-pam"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo /etc/init.d/torque-mom stop"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo /etc/init.d/torque-scheduler stop"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo /etc/init.d/torque-server stop"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo pbs_server -t create -f"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo killall pbs_server"))

        # Command 13 (Edit config)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo sh -c 'echo 'node0-lan' > /etc/torque/server_name'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo sh -c 'echo 'node0-lan' > /var/spool/torque/server_priv/acl_svr/acl_hosts'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo sh -c 'echo 'root@node0-lan' > /var/spool/torque/server_priv/acl_svr/operators'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo sh -c 'echo 'root@node0-lan' > /var/spool/torque/server_priv/acl_svr/managers'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo sh -c 'echo 'node0-lan' > /var/spool/torque/server_priv/nodes'"))
        for computeNodeNum in range(NUM_TOTAL_CORES - NUM_COMPUTE_CORES, NUM_TOTAL_CORES):
            node.addService(rspec.Execute(shell="/bin/sh",
                                          command="sudo sh -c 'echo 'node" + str(computeNodeNum) + "-lan' >> /var/spool/torque/server_priv/nodes'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo sh -c 'echo 'node0-lan' > /var/spool/torque/mom_priv/config'"))
        
        # Command 22 (Restart all processes again)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sleep 10"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo /etc/init.d/torque-server start"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo /etc/init.d/torque-scheduler start"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo /etc/init.d/torque-mom start"))
        
        # Command 26 (Set scheduling properties)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo qmgr -c 'set server scheduling = true'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo qmgr -c 'set server keep_completed = 300'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo qmgr -c 'set server mom_job_sync = true'"))
        
        # Command 29 (Create default queue)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo qmgr -c 'create queue batch'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo qmgr -c 'set queue batch queue_type = execution'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo qmgr -c 'set queue batch started = true'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo qmgr -c 'set queue batch enabled = true'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo qmgr -c 'set queue batch resources_default.walltime = 1:00:00'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo qmgr -c 'set queue batch resources_default.nodes = 1'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo qmgr -c 'set server default_queue = batch'"))
        
        # Command 36 (Configure submission pool)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo qmgr -c 'set server submit_hosts = SERVER'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo qmgr -c 'set server allow_node_submit = true'"))
        
        # Command 38 (Setup/Install Environment Modules Required by Asg4)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo apt-get install -y -f environment-modules"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo git clone https://github.com/Craig-Brofessional/CPSC_3620.git /usr/share/modules/modulefiles/tmp"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo mv /usr/share/modules/modulefiles/tmp/modulefiles/* /usr/share/modules/modulefiles"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo rm -r /usr/share/modules/modulefiles/tmp"))
        
    elif i > 0 and i < NUM_FILE_SYSTEM_CORES + 1:
        
        # Command 1 (Setup NFS Client)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo apt-get -y -f install nfs-common"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo mkdir -p /nfs/home"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="until ping -c1 "  + BASE_IP + "1 &>/dev/null; do sleep 1:; done"))
        
        # Command 4 (Ensure that server is ready to mount)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sleep 120"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="echo 'Trying to mount @' `date +'%T.%6N'`"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo mount -o bg " + BASE_IP + "1:/home /nfs/home"))
        
    elif i >= NUM_TOTAL_CORES - NUM_COMPUTE_CORES and i < NUM_TOTAL_CORES:
        # Command 1 (Install necessary programs)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo apt-get -y -f install python python-dev python-pip python-numpy"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo apt-get -y -f install openmpi-bin libopenmpi-dev"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo pip install mpi4py"))
        
        # Command 4 (Setup/Install Environment Modules Required by Asg4)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo apt-get install -y -f environment-modules"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo git clone https://github.com/Craig-Brofessional/CPSC_3620.git /usr/share/modules/modulefiles/tmp"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo mv /usr/share/modules/modulefiles/tmp/modulefiles/* /usr/share/modules/modulefiles"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo rm -r /usr/share/modules/modulefiles/tmp"))
        
        # Command 8 (Setup Torque Client)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo apt-get install -y -f torque-client torque-mom"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo /etc/init.d/torque-mom stop"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo sh -c 'echo 'node0-lan' > /etc/torque/server_name'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo sh -c 'echo 'node0-lan' > /var/spool/torque/mom_priv/config'"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo qmgr -c 'set server submit_hosts += CLIENT'"))
        
        # Command 13 (Wait for Torque Server, Connect)
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="until ping -c1 "  + BASE_IP + "1 &>/dev/null; do sleep 1:; done"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sleep 120"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo pbs_mom"))

        
        
# Print the RSpec to the enclosing page.
portal.context.printRequestRSpec(request)
