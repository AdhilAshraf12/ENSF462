import Network
import argparse
from time import sleep, time
import hashlib

class Packet:
    seq_num_S_length = 10
    length_S_length = 10
    checksum_length = 32
    
    def __init__(self, seq_num, msg_S):
        self.seq_num = seq_num
        self.msg_S = msg_S
    
    @classmethod
    def from_byte_S(self, byte_S):
        if byte_S == '':
            return None
        if Packet.corrupt(byte_S):
            raise RuntimeError("Cannot initialize Packet: byte_S is corrupt")
        
        seq_num = int(byte_S[Packet.length_S_length:Packet.length_S_length + Packet.seq_num_S_length])
        msg_S = byte_S[Packet.length_S_length + Packet.seq_num_S_length + Packet.checksum_length:]
        return self(seq_num, msg_S)

    def get_byte_S(self):
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        length_S = str(self.length_S_length + len(seq_num_S) + self.checksum_length + len(self.msg_S)).zfill(self.length_S_length)
        checksum = hashlib.md5((length_S + seq_num_S + self.msg_S).encode("utf-8"))
        checksum_S = checksum.hexdigest()
        return length_S + seq_num_S + checksum_S + self.msg_S

    @staticmethod
    def corrupt(byte_S):
        length_S = byte_S[0:Packet.length_S_length]
        seq_num_S = byte_S[Packet.length_S_length:Packet.seq_num_S_length + Packet.seq_num_S_length]
        checksum_S = byte_S[Packet.seq_num_S_length + Packet.seq_num_S_length:Packet.seq_num_S_length + Packet.length_S_length + Packet.checksum_length]
        msg_S = byte_S[Packet.seq_num_S_length + Packet.seq_num_S_length + Packet.checksum_length:]

        checksum = hashlib.md5(str(length_S + seq_num_S + msg_S).encode("utf-8"))
        computed_checksum_S = checksum.hexdigest()
        return checksum_S != computed_checksum_S

class RDT:
    seq_num = 1
    prev_ack_pkt = Packet(0, "")
    byte_buffer = ""

    def __init__(self, role_S, receiver_S, port):
        self.network = Network.NetworkLayer(role_S, receiver_S, port)

    def disconnect(self):
        self.network.disconnect()

    def rdt_3_0_send(self, msg_S):
        timeout = 3
        seq_num = self.seq_num                
        p = Packet(seq_num, msg_S)
        self.network.udt_send(p.get_byte_S())
        waiting = True
        start_time = time()

        while waiting:  
            try:
                ack_byte_S = self.network.udt_receive()               
                    
                if ack_byte_S == '':
                    if timeout + start_time >= time():
                        continue
                    else: 
                        raise TimeoutError
                
                if Packet.corrupt(ack_byte_S):
                    print(f"Corruption detected in ACK. Resend message {p.seq_num}")
                    self.network.udt_send(p.get_byte_S())
                    start_time = time()
                    continue
                
                ack_packet = Packet.from_byte_S(ack_byte_S) 
                
                if ack_packet.seq_num != self.prev_ack_pkt.seq_num:
                    self.prev_ack_pkt = ack_packet
                    waiting = False
                    self.seq_num += 1
                    start_time = time()
                    return ack_packet.msg_S
                else:
                    print(f"Ignore duplicate or out-of-sequence ACK. Resend message {p.seq_num}")
                    self.network.udt_send(p.get_byte_S())
                    start_time = time()
            except TimeoutError:
                print(f"Timeout! Resend message seq_num {seq_num}")
                self.network.udt_send(p.get_byte_S())
                start_time = time()
        self.seq_num += 1

    def rdt_3_0_receive(self):
        start_time = time()
        timeout = 10
        while True:
            try:
                msg_byte_S = self.network.udt_receive()
                            
                if msg_byte_S == '': 
                    if start_time + timeout >= time():
                        continue
                    else:
                        raise TimeoutError
                
                if Packet.corrupt(msg_byte_S):
                    if self.prev_ack_pkt.seq_num == 0:
                        print("Corruption detected! Send ACK 1")
                        self.network.udt_send(Packet(1, "").get_byte_S())
                    else:
                        print(f"Corruption detected! Send ACK {self.prev_ack_pkt.seq_num}")
                        self.network.udt_send(Packet(self.prev_ack_pkt.seq_num, "").get_byte_S())
                    start_time = time()
                    continue
                else:
                    msg_packet = Packet.from_byte_S(msg_byte_S) 
                    ack_packet = Packet(msg_packet.seq_num, " ")
            
                if ack_packet.seq_num != self.prev_ack_pkt.seq_num:
                    self.network.udt_send(ack_packet.get_byte_S())
                    self.prev_ack_pkt = ack_packet
                    start_time = time()
                    return msg_packet
                else:
                    print(f"Ignore duplicate ACK. Resend ACK {self.prev_ack_pkt.seq_num}")
                    self.network.udt_send(self.prev_ack_pkt.get_byte_S())
                    start_time = time()
            except TimeoutError:
                print(f"Timeout! Resend message {msg_byte_S}")
                self.network.udt_send(msg_byte_S)
                start_time = time()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RDT implementation.")
    parser.add_argument(
        "role",
        help="Role is either sender or receiver.",
        choices=["sender", "receiver"],
    )
    parser.add_argument("receiver", help="receiver.")
    parser.add_argument("port", help="Port.", type=int)
    args = parser.parse_args()

    rdt = RDT(args.role, args.receiver, args.port)
    if args.role == "sender":
        rdt.rdt_3_0_send("MSG_FROM_SENDER")
        sleep(2)
        print(rdt.rdt_3_0_receive())
        rdt.disconnect()
    else:
        sleep(1)
        print(rdt.rdt_3_0_receive())
        rdt.rdt_3_0_send("MSG_FROM_RECEIVER")
        rdt.disconnect()
