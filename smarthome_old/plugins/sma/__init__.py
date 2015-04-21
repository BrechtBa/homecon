#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2013 Robert Budde                       robert@projekt131.de
#########################################################################
#  This software is based on Stuart Pittaway's "NANODE SMA PV MONITOR"
#  https://github.com/stuartpittaway/nanodesmapvmonitor
#
#  This software is based on SBF's "SMAspot"
#  https://code.google.com/p/sma-spot/
#
#  SMA-Plugin for SmartHome.py.   http://mknx.github.com/smarthome/
#
#	License: Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)
#	http://creativecommons.org/licenses/by-nc-sa/3.0/
#
#	You are free:
#		to Share — to copy, distribute and transmit the work
#		to Remix — to adapt the work
#	Under the following conditions:
#	Attribution:
#		You must attribute the work in the manner specified by the author or licensor
#		(but not in any way that suggests that they endorse you or your use of the work).
#	Noncommercial:
#		You may not use this work for commercial purposes.
#	Share Alike:
#		If you alter, transform, or build upon this work, you may distribute the resulting work
#		only under the same or similar license to this one.
#
# DISCLAIMER:
#	A user of this plugin acknowledges that he or she is receiving this
#	software on an "as is" basis and the user is not relying on the accuracy
#	or functionality of the software for any purpose. The user further
#	acknowledges that any use of this software will be at his own risk
#	and the copyright owner accepts no responsibility whatsoever arising from
#	the use or application of the software.
#########################################################################

import logging
import time
import socket
import sys
from datetime import datetime
from dateutil import tz

BCAST_ADDR = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
ZERO_ADDR = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

SMANET2_HDR = bytes([0x7E, 0xFF, 0x03, 0x60, 0x65])

FCSTAB = [
    0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf,
    0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
    0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
    0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
    0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd,
    0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
    0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c,
    0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
    0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
    0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
    0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a,
    0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
    0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9,
    0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
    0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
    0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
    0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7,
    0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
    0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036,
    0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
    0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5,
    0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
    0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134,
    0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
    0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3,
    0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb,
    0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232,
    0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a,
    0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
    0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
    0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330,
    0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78,
]

# Start-Address, End-Address, ?
STATUS_READ = (0x00214800, 0x002148FF, [0x00, 0x02, 0x80, 0x58])
#STATUS_READ = (0x00214800, 0x002148FF, [0x00, 0x02, 0x80, 0x51])
DCx_P_READ = (0x00251E00, 0x00251EFF, [0x00, 0x02, 0x80, 0x53])
E_STAT_READ = (0x00260100, 0x002622FF, [0x00, 0x02, 0x00, 0x54])
AC_P_READ = (0x00263F00, 0x00263FFF, [0x00, 0x02, 0x00, 0x51])
ACx_PM_READ = (0x00411E00, 0x004120FF, [0x00, 0x02, 0x00, 0x51])
RELAY_READ = (0x00416400, 0x004164FF, [0x00, 0x02, 0x80, 0x58])
#RELAY_READ  = (0x00416400, 0x004164FF, [0x00, 0x02, 0x80, 0x51])
OTIME_READ = (0x00462E00, 0x00462FFF, [0x00, 0x02, 0x00, 0x54])
DCx_UI_READ = (0x00451F00, 0x004521FF, [0x00, 0x02, 0x80, 0x53])
ACx_P_READ = (0x00464000, 0x004642FF, [0x00, 0x02, 0x00, 0x51])
ACx_UI_READ = (0x00464800, 0x004652FF, [0x00, 0x02, 0x00, 0x51])
ACx_I2_READ = (0x00465300, 0x004655FF, [0x00, 0x02, 0x00, 0x51])
FREQ_READ = (0x00465700, 0x004657FF, [0x00, 0x02, 0x00, 0x51])

AC_MAX2 = (0x00832A00, 0x00832AFF, [0x00, 0x02, 0x00, 0x51])

TYPE_LABEL = (0x00821E00, 0x008220FF, [0x00, 0x02, 0x00, 0x58])
SW_VERSION = (0x00823400, 0x008234FF, [0x00, 0x02, 0x00, 0x58])

fields = {'STATUS': [0x00214801, 1, STATUS_READ],

          'DC_STRING1_P': [0x251e01, 1, DCx_P_READ],
          'DC_STRING2_P': [0x251e02, 1, DCx_P_READ],

          'E_TOTAL': [0x260101, 1, E_STAT_READ],
          'E_DAY': [0x262201, 1, E_STAT_READ],

          'AC_P_TOTAL': [0x263f01, 1, AC_P_READ],

          'AC_PHASE1_P_MAX': [0x00411E01, 1, ACx_PM_READ],
          'AC_PHASE2_P_MAX': [0x00411F01, 1, ACx_PM_READ],
          'AC_PHASE3_P_MAX': [0x00412001, 1, ACx_PM_READ],

          'GRID_RELAY': [0x00416401, 1, RELAY_READ],

          'OPERATING_TIME': [0x00462E01, 1, OTIME_READ],
          'FEEDING_TIME': [0x00462F01, 1, OTIME_READ],

          'DC_STRING1_U': [0x451f01, 100.0, DCx_UI_READ],
          'DC_STRING2_U': [0x451f02, 100.0, DCx_UI_READ],
          'DC_STRING1_I': [0x452101, 1000.0, DCx_UI_READ],
          'DC_STRING2_I': [0x452102, 1000.0, DCx_UI_READ],

          'AC_PHASE1_P': [0x00464001, 1, ACx_P_READ],
          'AC_PHASE2_P': [0x00464101, 1, ACx_P_READ],
          'AC_PHASE3_P': [0x00464201, 1, ACx_P_READ],

          'AC_PHASE1_U': [0x00464801, 100.0, ACx_UI_READ],
          'AC_PHASE2_U': [0x00464901, 100.0, ACx_UI_READ],
          'AC_PHASE3_U': [0x00464A01, 100.0, ACx_UI_READ],
          'AC_PHASE1_I': [0x00465001, 1000.0, ACx_UI_READ],
          'AC_PHASE2_I': [0x00465101, 1000.0, ACx_UI_READ],
          'AC_PHASE3_I': [0x00465201, 1000.0, ACx_UI_READ],

          'AC_PHASE1_I2': [0x00465301, 1000.0, ACx_I2_READ],
          'AC_PHASE2_I2': [0x00465401, 1000.0, ACx_I2_READ],
          'AC_PHASE3_I2': [0x00465501, 1000.0, ACx_I2_READ],

          'GRID_FREQUENCY': [0x00465701, 100.0, FREQ_READ],
          }

logger = logging.getLogger('SMA')


class SMA():

    def __init__(self, smarthome, bt_addr, password="0000", update_cycle="60"):
        self._sh = smarthome
        self._update_cycle = int(update_cycle)
        self._fields = {}
        self._read_ops = []
        self._inv_bt_addr = bt_addr
        self._inv_password = password
        self._inv_last_read_timestamp_utc = 0
        self._inv_serial = 0
        self._own_bt_addr_le = bytearray(BCAST_ADDR)
        self._inv_bt_addr_le = bytearray.fromhex(
            self._inv_bt_addr.replace(':', ' '))
        self._inv_bt_addr_le.reverse()
        self._btsocket = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

    def _update_values(self):
        #logger.warning("sma: signal strength = {}%%".format(self._inv_get_bt_signal_strength()))
        timestamp_utc = 0
        for read_op in self._read_ops:
            data = self._inv_get_value(read_op)
            if (data != []):
                for field in data:
                    field_addr = field[0]
                    if field_addr in self._fields:
                        for item in self._fields[field_addr]['items']:
                            item(field[2] / self._fields[field_addr]
                                 ['eval'], 'SMA', self._inv_bt_addr)
                    timestamp_utc = field[1]
        # update time
        if (timestamp_utc > self._inv_last_read_timestamp_utc):
            self._inv_last_read_timestamp_utc = timestamp_utc
            self._inv_last_read_datetime = datetime.fromtimestamp(
                self._inv_last_read_timestamp_utc, tz.tzlocal())
            self._inv_last_read_str = self._inv_last_read_datetime.strftime(
                "%d.%m.%Y %H:%M:%S")
            logger.debug(
                "sma: last successful update = {}".format(self._inv_last_read_str))
            if 'LAST_UPDATE' in self._fields:
                for item in self._fields['LAST_UPDATE']['items']:
                    item(self._inv_last_read_str, 'SMA', self._inv_bt_addr)

    def run(self):
        self.alive = True
        self._send_count = 0
        try:
            self._btsocket.connect((self._inv_bt_addr, 1))
            logger.info(
                "sma: via bluetooth connected to {}".format(self._inv_bt_addr))
            self._inv_connect()
            self._inv_login()
            if 'OWN_ADDRESS' in self._fields:
                for item in self._fields['OWN_ADDRESS']['items']:
                    item(self._own_bt_addr, 'SMA', self._inv_bt_addr)
            if 'INV_ADDRESS' in self._fields:
                for item in self._fields['INV_ADDRESS']['items']:
                    item(self._inv_bt_addr, 'SMA', self._inv_bt_addr)
            if 'INV_SERIAL' in self._fields:
                for item in self._fields['INV_SERIAL']['items']:
                    item(self._inv_serial, 'SMA', self._inv_bt_addr)
        except:
            logger.error(
                "sma: establishing connection to inverter failed - {}".format(sys.exc_info()))
        self._sh.scheduler.add('SMA', self._update_values,
                               prio=5, cycle=self._update_cycle)

    def stop(self):
        self.alive = False
        try:
            self._sh.scheduler.remove('SMA')
        except:
            logger.error(
                "sma: removing sma.update from scheduler failed - {}".format(sys.exc_info()))
        try:
            self._btsocket.close()
            #self._btsocket = False
        except:
            logger.error(
                "sma: closing connection to inverter failed - {}".format(sys.exc_info()))

    def parse_item(self, item):
        if 'sma' in item.conf:
            field_name = item.conf['sma']
            if field_name in fields:
                field_addr = fields[field_name][0]
                field_eval = fields[field_name][1]
                logger.debug("sma: {0} connected to field {1} ({2:#06x})".format(
                    item, field_name, field_addr))
                if not field_addr in self._fields:
                    self._fields[field_addr] = {
                        'items': [item], 'logics': [], 'eval': field_eval}
                else:
                    self._fields[field_addr]['items'].append(item)
                field_read_op = fields[field_name][2]
                if not field_read_op in self._read_ops:
                    self._read_ops.append(field_read_op)
            else:
                field_addr = field_name
                logger.debug("sma: {0} connected to field {1})".format(
                    item, field_name))
                if not field_addr in self._fields:
                    self._fields[field_addr] = {'items': [item], 'logics': []}
                else:
                    if not item in self._fields[field_addr]['items']:
                        self._fields[field_addr]['items'].append(item)
        # return None to indicate "read-only"
        return None

    # receive function for SMANET1 messages
    def _recv_smanet1_msg(self, timeout=1.0):
        try:
            # wait for sfd
            msg = bytearray()
            self._btsocket.settimeout(timeout)
            while (len(msg) < 4):
                msg += self._btsocket.recv(4)
                while (msg[0] != 0x7E):
                    msg.pop(0)
            # get level 1 length and validate
            if ((msg[1] ^ msg[2] ^ msg[3]) != 0x7E):
                logger.warning("sma: rx: length fields invalid")
                return []
            length = int.from_bytes(msg[1:3], byteorder='little')
            if (length < 18):
                logger.warning("sma: rx: length to small: {}".format(length))
                return []

            # get remaining bytes
            while (len(msg) < length):
                # receive at most only precisely the number of bytes that are
                # missing for this msg (allow follow-up msgs))
                msg += self._btsocket.recv(length - len(msg))

            # check src and dst addr and check
            if (msg[4:10] != self._inv_bt_addr_le):
                logger.warning("sma: rx: unknown src addr")
                return []
            if (msg[10:16] != self._own_bt_addr_le) and (msg[10:16] != ZERO_ADDR) and (msg[10:16] != BCAST_ADDR):
                logger.warning("sma: rx: wrong dst addr")
                return []

            #logger.debug("rx: SMANET1 msg: len={} / data=[{}]".format(len(msg), ' '.join(['0x%02x' % b for b in msg])))
        except socket.timeout:
            logger.warning(
                "sma: rx: timeout exception - could not receive msg within {}s".format(timeout))
            msg = []
        except:
            logger.warning("sma: rx: exception - {}".format(sys.exc_info()))
            msg = []
        return msg

    def _recv_smanet2_msg(self, cmdcodes_expected=[0x0001]):
        # allow receiving SMANET2 msgs which consist of multiple SMANET1
        # msgs!!!
        retries = 10
        smanet2_msg = bytearray()
        while self.alive:
            retries -= 1
            if (retries == 0):
                logger.warning("sma: recv smanet2 msg - retries used up!")
                return []
            smanet1_msg = self._recv_smanet1_msg()
            if (smanet1_msg == []):
                break

            # get cmdcode - check for last message code (0x0001)
            smanet2_msg += smanet1_msg[18::]
            cmdcode_recv = int.from_bytes(
                smanet1_msg[16:18], byteorder='little')
            if (cmdcode_recv in cmdcodes_expected):
                break

        if (smanet2_msg[0:5] != SMANET2_HDR):
            logger.warning("sma: no SMANET2 msg")
            logger.warning(
                "sma: recv: len={} / data=[{}]".format(len(smanet2_msg), ' '.join(['0x%02x' % b for b in smanet2_msg])))
            return []

        # remove escape characters
        i = 0
        while True:
            if (smanet2_msg[i] == 0x7d):
                smanet2_msg[i + 1] ^= 0x20
                del(smanet2_msg[i])
            i += 1
            if (i == len(smanet2_msg)):
                break

        crc = self._calc_crc16(smanet2_msg[1:-3])
        if (crc != int.from_bytes(smanet2_msg[-3:-1], byteorder='little')):
            logger.warning("sma: crc: crc16 error - {:04x}".format(crc))
            logger.warning(
                "sma: crc: len={} / data=[{}]".format(len(smanet2_msg), ' '.join(['0x%02x' % b for b in smanet2_msg])))
            return []
        return smanet2_msg

    def _recv_smanet1_msg_with_cmdcode(self, cmdcodes_expected=[0x0001]):
        retries = 3
        while self.alive:
            retries -= 1
            if (retries == 0):
                logger.warning("sma: recv msg with cmdcode - retries used up!")
                return []
            msg = self._recv_smanet1_msg()
            # get cmdcode
            if (msg != []) and (int.from_bytes(msg[16:18], byteorder='little') in cmdcodes_expected):
                break
        return msg

    def _send_msg(self, msg):
        if (len(msg) >= 0x3a):
            # calculate crc starting with byte 19 and append with LE byte-oder
            msg += self._calc_crc16(msg[19::]).to_bytes(2, byteorder='little')
            # add escape sequences starting with byte 19
            i = 19
            while True:
                if (msg[i] in [0x7d, 0x7e, 0x11, 0x12, 0x13]):
                    msg[i] ^= 0x20
                    msg.insert(i, 0x7d)
                i += 1
                if (i == len(msg)):
                    break
            # add msg delimiter
            msg += bytes([0x7e])
        # set length fields
        msg[1:3] = len(msg).to_bytes(2, byteorder='little')
        msg[3] = msg[1] ^ msg[2] ^ 0x7e
        #print("tx: len={} / data=[{}]".format(len(msg), ' '.join(['0x%02x' % b for b in msg])))
        self._btsocket.send(msg)

    def _calc_crc16(self, msg):
        crc = 0xFFFF
        for i in msg:
            crc = (crc >> 8) ^ FCSTAB[(crc ^ i) & 0xFF]
        crc ^= 0xFFFF
        #print("crc16 = {:x}".format(crc))
        return crc

    def _inv_connect(self):
        # receive broadcast-msg from inverter
        msg = self._recv_smanet1_msg_with_cmdcode([0x0002])

        # extract net-id from the 0x0002 msg
        self._net_id = msg[22]

        # reply with wildcard src addr
        msg[4:10] = ZERO_ADDR
        msg[10:16] = self._inv_bt_addr_le
        self._send_msg(msg)

        # receive msg from inverter
        msg = self._recv_smanet1_msg_with_cmdcode([0x000a])
        # receive msg from inverter
        msg = self._recv_smanet1_msg_with_cmdcode([0x0005, 0x000c])
        # receive msg from inverter
        msg = self._recv_smanet1_msg_with_cmdcode([0x0005])

        if (msg == []):
            raise

        # extract own bluetooth addr
        self._own_bt_addr_le = msg[26:32]
        logger.info("sma: own bluetooth address: {}".format(
            ':'.join(['%02x' % b for b in self._own_bt_addr_le[::-1]])))

        # first SMA net2 msg
        retries = 10
        while (retries > 0) and self.alive:
            retries -= 1
            # level1
            cmdcode = 0x0001
            msg = bytearray([0x7E, 0, 0, 0])
            msg += self._own_bt_addr_le + self._inv_bt_addr_le + \
                cmdcode.to_bytes(2, byteorder='little')
            # sma-net2 level
            ctrl = 0xA009
            self._send_count = (self._send_count + 1) & 0x7FFF
            msg += SMANET2_HDR + ctrl.to_bytes(2, byteorder='little') + BCAST_ADDR + bytes([0x00, 0x00]) + self._inv_bt_addr_le + \
                bytes([0x00] + [0x00] + [0, 0, 0, 0]) + \
                (self._send_count | 0x8000).to_bytes(
                    2, byteorder='little')
            msg += bytes([0x00, 0x02, 0x00] + [0x00] +
                         [0x00, 0x00, 0x00, 0x00] + [0x00, 0x00, 0x00, 0x00])
            # send msg to inverter
            self._send_msg(msg)
            # receive msg from inverter
            msg = self._recv_smanet2_msg()
            if (msg != []):
                break

        if (retries == 0):
            logger.warning("sma: connect - retries used up!")
            return

        # second SMA net2 msg
        cmdcode = 0x0001
        msg = bytearray([0x7E, 0, 0, 0])
        msg += self._own_bt_addr_le + self._inv_bt_addr_le + \
            cmdcode.to_bytes(2, byteorder='little')
        # sma-net2 level
        ctrl = 0xA008
        self._send_count = (self._send_count + 1) & 0x7FFF
        msg += SMANET2_HDR + ctrl.to_bytes(2, byteorder='little') + BCAST_ADDR + bytes([0x00, 0x03]) + self._inv_bt_addr_le + \
            bytes([0x00] + [0x03] + [0, 0, 0, 0]) + \
            (self._send_count | 0x8000).to_bytes(
                2, byteorder='little')
        msg += bytes([0x0E, 0x01, 0xFD, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # send msg
        self._send_msg(msg)

    def _inv_login(self):
        timestamp_utc = int(time.time())
        password_pattern = [0x88, 0x88, 0x88, 0x88, 0x88,
                            0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88]
        password_pattern[0:len(self._inv_password)] = [((0x88 + ord(char)) & 0xff)
                                                       for char in self._inv_password]

        retries = 5
        while (retries > 0) and self.alive:
            retries -= 1
            # level1
            cmdcode = 0x0001
            msg = bytearray([0x7E, 0, 0, 0])
            msg += self._own_bt_addr_le + self._inv_bt_addr_le + \
                cmdcode.to_bytes(2, byteorder='little')
            # sma-net2 level
            ctrl = 0xA00E
            self._send_count = (self._send_count + 1) & 0x7FFF
            msg += SMANET2_HDR + ctrl.to_bytes(2, byteorder='little') + BCAST_ADDR + bytes([0x00, 0x01]) + self._inv_bt_addr_le + \
                bytes([0x00] + [0x01] + [0, 0, 0, 0]) + \
                (self._send_count | 0x8000).to_bytes(
                    2, byteorder='little')
            msg += bytes([0x0C, 0x04, 0xFD, 0xFF, 0x07, 0x00,
                         0x00, 0x00, 0x84, 0x03, 0x00, 0x00])
            msg += timestamp_utc.to_bytes(4, byteorder='little')
            msg += bytes([0x00, 0x00, 0x00, 0x00] + password_pattern)
            # send msg to inverter
            self._send_msg(msg)
            # send msg to inverter
            self._send_msg(msg)
            # receive msg from inverter
            msg = self._recv_smanet2_msg()
            if (msg != []):
                break

        if (retries == 0):
            logger.warning("sma: login - retries used up!")
            return

        # extract serial
        self._inv_serial = int.from_bytes(msg[17:21], byteorder='little')
        logger.info("sma: inverter serial = {}".format(self._inv_serial))

    def _inv_get_bt_signal_strength(self):
        cmdcode = 0x0003
        msg = bytearray([0x7E, 0, 0, 0])
        msg += self._own_bt_addr_le + self._inv_bt_addr_le + \
            cmdcode.to_bytes(2, byteorder='little')
        msg += bytes([0x05, 0x00])
        self._send_msg(msg)
        msg = self._recv_smanet1_msg_with_cmdcode([0x0004])
        # extract signal strength
        return ((msg[22] * 100.0) / 0xff)

    def _inv_get_value(self, value_set):
        # send request
        # level1
        cmdcode = 0x0001
        msg = bytearray([0x7E, 0, 0, 0])
        msg += self._own_bt_addr_le + self._inv_bt_addr_le + \
            cmdcode.to_bytes(2, byteorder='little')
        # sma-net2 level
        self._send_count = (self._send_count + 1) & 0x7FFF
        msg += SMANET2_HDR + bytes([0x09, 0xA0]) + BCAST_ADDR + bytes([0x00, 0x00]) + self._inv_bt_addr_le + \
            bytes([0x00] + [0x00] + [0, 0, 0, 0]) + \
            (self._send_count | 0x8000).to_bytes(
                2, byteorder='little')
        msg += bytes(value_set[2]) + value_set[0].to_bytes(4, byteorder='little') + \
            value_set[1].to_bytes(4, byteorder='little')
        # send msg to inverter
        self._send_msg(msg)

        # receive response from inverter
        data = []
        while (data == []) and self.alive:
            response = self._recv_smanet2_msg()
            if (response == []):
                logger.warning("sma: no response to request (timeout)!")
                return data
            if (len(response) >= 60):
                i = 41
                try:
                    while (i < (len(response) - 11)):
                        value_code = int.from_bytes(
                            response[i:i + 4], byteorder='little') & 0x00FFFFFF
                        timestamp_utc = int.from_bytes(
                            response[i + 4:i + 8], byteorder='little')
                        # this only works for nums - fix it!
                        value = int.from_bytes(
                            response[i + 8:i + 12], byteorder='little')
                        if (value == 0x80000000) or (value == 0xFFFFFFFF):
                            value = 0
                        logger.debug(
                            "sma: value_code={:#08x} / value={:5d}".format(value_code, value))
                        data += [[value_code, timestamp_utc, value]]

                        if (response[32] == 0x54):
                            i += 16
                        elif (response[32] in [0x51, 0x53]):
                            i += 28
                        elif (response[32] == 0x58):
                            i += 40
                        # elif ((response[i + 3] == 0x00) or (response[i + 3] == 0x40)):
                        #    i += 28
                        # elif ((response[i + 3] == 0x08) or (response[i + 3] == 0x10)):
                        #    i += 40
                        else:
                            logger.error(
                                "sma: rx - can not decode field width from identifier={:#02x}".format(value_set[2][3]))
                            for entry in data:
                                logger.debug(
                                    "sma: value_code={:#08x} / timestamp={} / value={:5d}".format(entry[0], entry[1], entry[2]))
                            data = []
                            break
                except:
                    data = []
                    pass

            if (data == []):
                logger.warning("sma: rx - unknown/malformed response!")
                logger.warning(
                    "sma: rx - len={} data=[{}]\n".format(len(response), ' '.join(['0x%02x' % b for b in response])))

        return data
