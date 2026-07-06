from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel

def run():
    net = Mininet(controller=RemoteController, link=TCLink)

    print("*** Adding remote controller")
    c0 = net.addController('c0', ip='127.0.0.1', port=6633)

    print("*** Adding hosts")
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')

    print("*** Adding switch (OpenFlow 1.3)")
    s1 = net.addSwitch('s1', protocols='OpenFlow13')

    print("*** Creating links")
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    print("*** Starting network")
    net.start()

    print("*** Network ready. Run tests inside CLI.")
    CLI(net)

    print("*** Stopping network")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
