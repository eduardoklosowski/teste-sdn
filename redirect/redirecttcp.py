from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import (CONFIG_DISPATCHER, MAIN_DISPATCHER,
                                    set_ev_cls)
from ryu.lib.packet import ipv4, packet, tcp
from ryu.ofproto import ether, inet, ofproto_v1_3

from utils import add_flow, mark_processed


class RedirectTCP(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(
            eth_type=ether.ETH_TYPE_IP,
            ip_proto=inet.IPPROTO_TCP,
            ipv4_dst='10.0.0.2',
            tcp_dst=80,
        )
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER),
        ]
        add_flow(datapath, 2, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        tcp_pkt = pkt.get_protocol(tcp.tcp)

        if ip_pkt and ip_pkt.dst == '10.0.0.2' and tcp_pkt and tcp_pkt.dst_port == 80:
            self.logger.info('--> HTTP ip=%r port=%r', ip_pkt.src, tcp_pkt.src_port)

            match = parser.OFPMatch(
                in_port=in_port,
                eth_type=ether.ETH_TYPE_IP,
                ip_proto=inet.IPPROTO_TCP,
                ipv4_src=ip_pkt.src,
                ipv4_dst=ip_pkt.dst,
                tcp_src=tcp_pkt.src_port,
                tcp_dst=tcp_pkt.dst_port,
            )
            actions = [
                parser.OFPActionSetField(eth_dst='00:00:00:00:00:03'),
                parser.OFPActionSetField(ipv4_dst='10.0.0.3'),
                parser.OFPActionOutput(3),
            ]

            match_return = parser.OFPMatch(
                in_port=3,
                eth_type=ether.ETH_TYPE_IP,
                ip_proto=inet.IPPROTO_TCP,
                ipv4_src='10.0.0.3',
                ipv4_dst=ip_pkt.src,
                tcp_src=tcp_pkt.dst_port,
                tcp_dst=tcp_pkt.src_port,
            )
            actions_return = [
                parser.OFPActionSetField(eth_src='00:00:00:00:00:02'),
                parser.OFPActionSetField(ipv4_src='10.0.0.2'),
                parser.OFPActionOutput(in_port),
            ]

            add_flow(datapath, 3, match, actions, idle_timeout=20)
            add_flow(datapath, 3, match_return, actions_return, idle_timeout=20)

            out = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=ofproto.OFP_NO_BUFFER,
                in_port=in_port,
                actions=actions,
                data=msg.data,
            )
            datapath.send_msg(out)
            mark_processed(ev, self.__class__.__name__)
