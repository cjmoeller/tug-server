import struct
f = open('yolo.file', 'wb')
f.write(struct.pack('i',(6442450946)))
f.close()