import argparse
import RDT
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Uppercase conversion receiver.")
    parser.add_argument("port", help="Port.", type=int)
    
    timeout = 10
    time_of_last_data = time.time()

    rdt = RDT.RDT("receiver", None, "5678")
    while True:
        msg_S = rdt.rdt_3_0_receive()
        if msg_S is None:
            if time_of_last_data + timeout < time.time():
                break
            else:
                continue
        print(f"Receive message {msg_S.msg_S}. Send ACK {msg_S.seq_num}")

    rdt.disconnect()
