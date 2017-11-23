"""
This class is a simple tool for you to send signal to SHIMADZU LABNIRS.

NOTE:
1. Common port addresses:
    LPT1 = 0x0378 or 0x03BC, LPT2 = 0x0278 or 0x0378, LPT3 = 0x0278
2. Follow the following instruction to make the config and plug the cable:
    a. Always plug the last few cables to the machine, 
      eg: do not plug the 7 to 'START', 8 to 'DI-8';
    b. Plug the first few cables to the port with the same #, 
      eg: the first cable to the DI-1 port;
    c. The keywords of config dictionary need to be ints but not a string

"""

from psychopy import parallel
import logging
import time

class TaskChangeTrigger(object):
  """
  Class for Task Change mode.
  """
  def __init__(self, port, config = {7: 'start', 8: 'stop'}, interval = 0.01, debug = False):
    """
    @para string port: the port you need to communicate with;
    @para dictionary config: how the cable pluged into the device;
    @para bool debug: if need print the debug data to the console.
    """
    self.dictionary = {}
    self.port = parallel.ParallelPort(address=port)
    self.config = config
    self.config_allowed = config.values()
    self.interval = interval
    self.debug = debug
    
    config_keys = config.keys()
    config_key_len = len(config_keys)

    if not all(isinstance(n, int) for n in config_keys):
      raise TypeError('The keywords of config dictionary need to be ints!')

    if config_keys and max(config_keys) != 8:
      raise TypeError('The last key of config dictionary must be 8, do not leave blank cable!');

    if config_key_len and sorted(config_keys) != range(min(config_keys), max(config_keys) + 1):
      raise TypeError('The keys of config dictioanry must be continuous numbers!')

    if not all(n in ['zero', 'mark', 'start', 'stop'] for n in self.config_allowed):
      raise TypeError('The value of config dictionary must be one of "zero", "mark", "start", "stop"!')

    for _key in config_keys:
      self.dictionary[config[_key]] = self.transform_signal(0b10 ** (_key - 1))
    
    self.max_data = 0b10 ** (8 - config_key_len) - 1

    for _signal in range(1, self.max_data):
      self.dictionary[_signal] = self.transform_signal((0b10 ** config_key_len - 1) * (0b10 ** (8 - config_key_len)) + _signal)

  @staticmethod
  def transform_signal(signal):
    """
    Revert the binary bit to make the signal fit the rule of SHIMADZU LABNIRS.
    @para int signal: the signal to be opreated.
    """
    return 0b11111111 - signal

  def _action_(self, action):
    """
    Ready an action, private function, do NOT use it independently!
    @para string action: the action to be emited.
    """
    if not action in self.config_allowed:
      raise Exception('Action is not defined!')
    
    self._send_(self.dictionary[action])
    time.sleep(self.interval)
    self._send_(0b11111111)

  def _send_(self, signal):
    """
    Method for sending the signal, do NOT use it independently!
    @para int signal: the signal to be sent.
    """
    signal = int(signal)
    self.port.setData(signal)

  def start(self):
    """
    Send a "Start" signal.
    """
    return self._action_('start')

  def stop(self):
    """
    Send a "Stop" signal.
    """
    return self._action_('stop')

  def zero(self):
    """
    Send a "Zero" signal.
    """
    return self._action_('zero')

  def mark(self):
    """
    Send a "Mark" signal.
    """
    return self._action_('mark')
