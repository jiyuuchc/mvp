import serial
import datatime

class Mvp:
	stx, etx, eot, enq, ack, nak = (b'\x02',b'\x03',b'\x04',b'\x05',b'\x06',b'\x15')

	def __init__(self, port, protocol = 'DIN'):
		self.protocol = protocol
		if protocol == 'DIN':
			self.ser = serial.Serial(port, bytesize=7, parity=serial.PARITY_EVEN, stopbits=2, timeout=1.0)
		else:
			self.ser = serial.Serial(port, bytesize=7, parity=serial.PARITY_ODD, stopits=1, timeout=1.0)
			#auto address
			self.ser.write(b'1a')
			self.ser.write(b'0x0d')
		self.ser.resetInputBuffer()

	def _getBcc(self, s):
		bcc = 0
		for b in s:
			bcc = bcc ^ b
		bcc = bcc ^ 3
		bcc = bcc ^ 255
		return bytes([bcc])

	def _exception(self, s):
		raise Exception(str(datetime.datetime.now()) + s)

	def sendCmd(self, s):
		self.ser.resetInputBuffer()
		if self.protocol == 'DIN':
			self.ser.write(self.stx)
			self.ser.write(s)
			self.ser.write(self.etx)
			self.ser.write(self._getBcc(s))
			self.checkAck()
		else:
			self.ser.write(s)
			self.ser.write(b'0x0d') #CR
			self.checkAck()

	def selectDev(self, n):
		self.ser.resetInputBuffer()
		if self.protocol == 'DIN':
			self.ser.write(self.eot)
			adr = b'%02i'%n
			self.ser.write(adr)
			self.ser.write(self.enq)
			resp = self.ser.read(2)
			if resp != adr:
				self._exception('Addressing error: ' + adr.decode('ascii'))
			self.checkAck()
		else:
			a = bytes([96 + n])
			self.ser.write(a)

	def checkAck(self):
		resp = self.ser.read()
		if resp != self.ack:
			self._exception("No ackowledgement from device.")

	def readResp(self):
		if self.protocol == 'DIN':
			ans = self.ser.read()
			if (ans != self.stx) :
				self._exception('Response does not start with STX')
			resp = self.ser.read_until(self.etx)
			bcc = self.ser.read()
			if getBcc(resp) != ans:
				self._exception('Incorrect BBC in response')
			return s
		else:
			resp = self.ser.read_until(b'0x0d')
			return resp

	def setValvePosition(self, dev, pos):
		self.selectDev(dev)
		if self.protocol == 'DIN':
			self.sendCmd(b'Vn%i'%pos)
			self.sendCmd(b'Ur')
		else:
			self.sendCmd(b'LP0%iR'%pos)

	def getValvePosition(self, dev):
		self.selectDev(dev)
		if self.protocol = 'DIN':
			self.sendCmd('Ap')
			resp = self.readResp()
			return int(resp[2:])
		else:
			self.sendCmd('LQP')
			resp = self.readResp()
			return(int(resp))
