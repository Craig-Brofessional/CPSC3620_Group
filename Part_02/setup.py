import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.igext as IG

NUM_COMPUTE_CORES = 3
NUM_FILE_SYSTEM_CORES = 3
NUM_WORKER_CORES = NUM_COMPUTE_CORES + NUM_FILE_SYSTEM_CORES

pc = portal.Context()
request = rspec.Request()

#pc.defineParameter("workerCount",
#                   "Number of HPCC thorslaves (multiple of 4)",
#                   portal.ParameterType.INTEGER, 4)

#pc.defineParameter("controllerHost", "Name of controller node",
#                   portal.ParameterType.STRING, "node0", advanced=True,
#                   longDescription="The short name of the controller node.  You shold leave this alone unless you really want the hostname to change.")

params = pc.bindParameters()

tourDescription = "This profile provides a small HPC system similar to the EXSEDE - Gordon system that our group was assigned"

#tourInstructions = \
#  """
#### Basic Instructions
#Once your experiment nodes have booted, and this profile's configuration scripts have finished deploying HPCCSystems inside your experiment, you'll be able to visit [the ECLWatch interface](http://{host-%s}:8010) (approx. 5-15 minutes).  
#""" % (params.controllerHost)

#
# Setup the Tour info with the above description and instructions.
#  
tour = IG.Tour()
tour.Description(IG.Tour.TEXT,tourDescription)
#tour.Instructions(IG.Tour.MARKDOWN,tourInstructions)
request.addTour(tour)

# Create a link with type LAN
link = request.LAN("lan")

# Generate the nodes
for i in range(NUM_WORKER_CORES + 1):
    node = request.RawPC("node" + str(i))
    node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU14-64-STD"
    
    # Create interfaces for each node.
    iface = node.addInterface("if" + str(i))
    link.addInterface(iface)
    
    #iface.component_id = "eth1"
    #iface.addAddress(rspec.IPv4Address("192.168.1." + str(i + 1), "255.255.255.0"))
    #link.addInterface(iface)
    
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo adduser --ingroup admin --disabled-password gordonAdmin"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo adduser gordonAdmin sudo"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo apt-get update"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                    command="sudo apt-get -y -f install python"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                    command="sudo apt-get -y -f install openmpi-bin libopenmpi-dev"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                    command="pip install mpi4py"))
    
    if i == 0:
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sleep 60"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo service hpcc-init start"))        
        
# Print the RSpec to the enclosing page.
portal.context.printRequestRSpec(request)


    