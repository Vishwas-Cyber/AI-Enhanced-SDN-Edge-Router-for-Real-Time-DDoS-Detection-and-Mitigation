from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, DEAD_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types
from ryu.lib import hub

import time
import os
import csv
from pathlib import Path

import joblib
import pandas as pd
import json

FEATURES = [
    'packet_count',
    'byte_count',
    'duration',
    'packet_count_per_second',
    'byte_count_per_second'
]


class Monitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    POLL_INTERVAL = 2
    MIN_PACKETS_BEFORE_DECISION = 20
    MIN_DURATION_BEFORE_DECISION = 1.0

    BLOCK_IDLE_TIMEOUT = 60
    BLOCK_HARD_TIMEOUT = 180

    RULE_PPS_THRESHOLD = 1000
    RULE_BPS_THRESHOLD = 1000000
    RULE_TOTAL_PACKETS_THRESHOLD = 5000

    MODEL_PROB_THRESHOLD = 0.60
    MODEL_PPS_FLOOR = 100

    STALE_FLOW_SECONDS = 20

    def __init__(self, *args, **kwargs):
        super(Monitor, self).__init__(*args, **kwargs)

        self.mac_to_port = {}
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)

        self.model = None
        self.model_enabled = False

        self.flow_state = {}
        self.blocked = set()

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.event_path = os.path.join(base_dir, 'results', 'events.jsonl')
        os.makedirs(os.path.dirname(self.event_path), exist_ok=True)

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        model_path = os.path.join(base_dir, 'model.pkl')

        self.results_dir = Path(base_dir) / 'results'
        self.results_dir.mkdir(exist_ok=True)
        self.attack_log_path = self.results_dir / 'attack_events.csv'
        self._ensure_attack_log()

        try:
            self.model = joblib.load(model_path)
            self.model_enabled = True
            self.logger.info('AI DDoS Monitor started, model loaded from %s', model_path)
            print(f'AI DDoS Monitor started, model loaded from {model_path}')
        except Exception as e:
            self.logger.warning('Model not loaded from %s, using rule-based detection only: %s', model_path, e)
            print(f'Model not loaded from {model_path}, using rule-based detection only: {e}')

    def _ensure_attack_log(self):
        if not self.attack_log_path.exists():
            with open(self.attack_log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'event_time', 'datapath_id', 'in_port', 'src_mac', 'dst_mac',
                    'packet_count', 'byte_count', 'duration',
                    'pps', 'bps', 'model_prob',
                    'rule_attack', 'model_attack',
                    'first_seen_time', 'detection_latency_sec'
                ])

    def _append_attack_log(self, row):
        with open(self.attack_log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        self.logger.info('Table-miss flow installed on datapath %s', datapath.id)
        print(f'Table-miss flow installed on datapath {datapath.id}')

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def state_change_handler(self, ev):
        datapath = ev.datapath

        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.datapaths[datapath.id] = datapath
                self.mac_to_port.setdefault(datapath.id, {})
                self.logger.info('Registered datapath %016x', datapath.id)
                print(f'Registered datapath {datapath.id:016x}')

        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                del self.datapaths[datapath.id]
                self.mac_to_port.pop(datapath.id, None)
                self.logger.info('Unregistered datapath %016x', datapath.id)
                print(f'Unregistered datapath {datapath.id:016x}')

    def _monitor(self):
        while True:
            for dp in list(self.datapaths.values()):
                self._request_flow_stats(dp)
            hub.sleep(self.POLL_INTERVAL)

    def _request_flow_stats(self, datapath):
        parser = datapath.ofproto_parser
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    def add_flow(self, datapath, priority, match, actions, idle_timeout=0, hard_timeout=0, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        kwargs = dict(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst,
            idle_timeout=idle_timeout,
            hard_timeout=hard_timeout
        )
        if buffer_id is not None:
            kwargs['buffer_id'] = buffer_id

        mod = parser.OFPFlowMod(**kwargs)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth is None or eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src
        dpid = datapath.id

        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        if src in self.blocked:
            return

        out_port = self.mac_to_port[dpid].get(dst, ofproto.OFPP_FLOOD)
        actions = [parser.OFPActionOutput(out_port)]

        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_src=src, eth_dst=dst)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, buffer_id=msg.buffer_id)
                return
            self.add_flow(datapath, 1, match, actions)

        data = None if msg.buffer_id != ofproto.OFP_NO_BUFFER else msg.data
        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data
        )
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        datapath = ev.msg.datapath
        body = ev.msg.body
        now = time.time()

        for stat in body:
            try:
                if stat.priority != 1:
                    continue

                in_port = stat.match.get('in_port')
                src = stat.match.get('eth_src')
                dst = stat.match.get('eth_dst')

                if src is None or dst is None or in_port is None:
                    continue

                key = (datapath.id, in_port, src, dst)

                packet_count = int(stat.packet_count)
                byte_count = int(stat.byte_count)
                duration = float(stat.duration_sec) + float(stat.duration_nsec) / 1e9

                if duration <= 0:
                    continue

                if key not in self.flow_state:
                    self.flow_state[key] = {
                        'last_packet_count': packet_count,
                        'last_byte_count': byte_count,
                        'last_duration': duration,
                        'last_seen_time': now,
                        'first_seen_time': now
                    }
                    continue

                prev = self.flow_state[key]

                delta_packets = packet_count - prev['last_packet_count']
                delta_bytes = byte_count - prev['last_byte_count']
                delta_duration = duration - prev['last_duration']

                self.flow_state[key].update({
                    'last_packet_count': packet_count,
                    'last_byte_count': byte_count,
                    'last_duration': duration,
                    'last_seen_time': now
                })

                if delta_packets < 0 or delta_bytes < 0 or delta_duration <= 0:
                    continue

                pps = delta_packets / delta_duration
                bps = delta_bytes / delta_duration

                print(
                    f'dp={datapath.id} in_port={in_port} src={src} dst={dst} '
                    f'total_pkts={packet_count} total_bytes={byte_count} dur={duration:.2f} '
                    f'delta_pkts={delta_packets} delta_bytes={delta_bytes} '
                    f'd_dur={delta_duration:.2f} pps={pps:.2f} bps={bps:.2f}'
                )

                if src in self.blocked:
                    continue

                if packet_count < self.MIN_PACKETS_BEFORE_DECISION or duration < self.MIN_DURATION_BEFORE_DECISION:
                    continue

                model_prob = None
                if self.model_enabled:
                    try:
                        features = pd.DataFrame([{
                            'packet_count': packet_count,
                            'byte_count': byte_count,
                            'duration': duration,
                            'packet_count_per_second': pps,
                            'byte_count_per_second': bps
                        }])[FEATURES]

                        if hasattr(self.model, 'predict_proba'):
                            model_prob = float(self.model.predict_proba(features)[0][1])
                        else:
                            pred = int(self.model.predict(features)[0])
                            model_prob = 1.0 if pred == 1 else 0.0
                    except Exception as e:
                        self.logger.warning('Model inference failed for %s -> %s: %s', src, dst, e)
                        print(f'Model inference failed for {src} -> {dst}: {e}')

                rule_attack = (
                    pps >= self.RULE_PPS_THRESHOLD or
                    bps >= self.RULE_BPS_THRESHOLD or
                    packet_count >= self.RULE_TOTAL_PACKETS_THRESHOLD
                )

                model_attack = (
                    model_prob is not None and
                    model_prob >= self.MODEL_PROB_THRESHOLD and
                    pps >= self.MODEL_PPS_FLOOR
                )

                if rule_attack or model_attack:
                    first_seen_time = self.flow_state[key]['first_seen_time']
                    detection_latency = now - first_seen_time
                    self._block_source(
                        datapath=datapath,
                        in_port=in_port,
                        src=src,
                        dst=dst,
                        packet_count=packet_count,
                        byte_count=byte_count,
                        duration=duration,
                        pps=pps,
                        bps=bps,
                        model_prob=model_prob,
                        rule_attack=rule_attack,
                        model_attack=model_attack,
                        first_seen_time=first_seen_time,
                        detection_latency=detection_latency
                    )

            except Exception as e:
                self.logger.exception('Error processing flow stat: %s', e)
                print(f'Error processing flow stat: {e}')

        stale_keys = []
        for key, val in self.flow_state.items():
            if key[0] == datapath.id and now - val['last_seen_time'] > self.STALE_FLOW_SECONDS:
                stale_keys.append(key)

        for key in stale_keys:
            del self.flow_state[key]

    def _write_event(self, event):
        try:
            with open(self.event_path, 'a', encoding='utf-8') as handle:
                handle.write(json.dumps(event, sort_keys=True) + '\n')
        except Exception as exc:
            self.logger.warning('Could not write event telemetry: %s', exc)

    def _block_source(self, datapath, in_port, src, dst, packet_count, byte_count, duration,
                      pps, bps, model_prob, rule_attack, model_attack,
                      first_seen_time, detection_latency):
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(eth_src=src)

        self.add_flow(
            datapath=datapath,
            priority=500,
            match=match,
            actions=[],
            idle_timeout=self.BLOCK_IDLE_TIMEOUT,
            hard_timeout=self.BLOCK_HARD_TIMEOUT
        )

        self.blocked.add(src)

        self._write_event({
            'event': 'ddos_detected',
            'datapath_id': int(datapath.id),
            'source_mac': str(src),
            'packets': int(packet_count),
            'bytes': int(byte_count),
            'duration_sec': float(duration),
            'pps': float(pps),
            'bps': float(bps),
            'model_probability': (
                None if model_prob is None else float(model_prob)
            ),
            'rule_priority': 500,
            'idle_timeout': self.BLOCK_IDLE_TIMEOUT,
            'hard_timeout': self.BLOCK_HARD_TIMEOUT
        })
        prob_text = f'{model_prob:.4f}' if model_prob is not None else 'N/A'

        print('\n' + '=' * 70)
        print('DDOS DETECTED')
        print(f'SRC MAC            : {src}')
        print(f'DST MAC            : {dst}')
        print(f'PACKETS            : {packet_count}')
        print(f'BYTES              : {byte_count}')
        print(f'DURATION           : {duration:.2f} sec')
        print(f'PPS                : {pps:.2f}')
        print(f'BPS                : {bps:.2f}')
        print(f'MODEL PROB         : {prob_text}')
        print(f'RULE ATTACK        : {rule_attack}')
        print(f'MODEL ATTACK       : {model_attack}')
        print(f'DETECTION LATENCY  : {detection_latency:.2f} sec')
        print('BLOCKING')
        print(f'DROP RULE INSTALLED FOR {src}')
        print('=' * 70 + '\n')

        self._append_attack_log([
            time.strftime('%Y-%m-%d %H:%M:%S'),
            datapath.id,
            in_port,
            src,
            dst,
            packet_count,
            byte_count,
            f'{duration:.4f}',
            f'{pps:.4f}',
            f'{bps:.4f}',
            prob_text,
            int(rule_attack),
            int(model_attack),
            f'{first_seen_time:.4f}',
            f'{detection_latency:.4f}'
        ])

        self.logger.warning('DDOS DETECTED src=%s dst=%s pps=%.2f bps=%.2f prob=%s latency=%.2f',
                            src, dst, pps, bps, prob_text, detection_latency)
