# mn --controller remote --mac --custom topo.py --topo ...

from mininet.topo import Topo


class HostsTopo(Topo):
    def build(self, hosts=1):
        s = self.addSwitch('s1')
        for i in range(1, hosts + 1):
            h = self.addHost('h%d' % i)
            self.addLink(s, h)


topos = {'hoststopo': HostsTopo}
