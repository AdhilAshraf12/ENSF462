import argparse
import RDT
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quotation sender talking to a receiver.")
    parser.add_argument("receiver", help="receiver.")
    parser.add_argument("port", help="Port.", type=int)
    
    msg_L = [
        "sending message - 1",
        "sending message - 2",
        "sending message - 3",
        "sending message - 4",
        "sending message - 5",
        "sending message - 6",
        "sending message - 7",
        "sending message - 8",
        "sending message - 9",
        "sending message - 10",
    ]

    timeout = 2
    time_of_last_data = time.time()

    rdt = RDT.RDT("sender", "localhost", "5678")
    for msg_S in msg_L:
        print("Sent Message:", msg_S)

        msg_ack = rdt.rdt_3_0_send(msg_S)
        if msg_ack is None:
            while time_of_last_data + timeout >= time.time():
                msg_ack = rdt.rdt_3_0_send(msg_S)
                if msg_ack is not None:
                    print(f"Receive ACK {msg_ack}. Message successfully sent!")
                    time_of_last_data = time.time()
                    break
            else:
                raise TimeoutError()
        else:
            print(f"Receive ACK {msg_ack}. Message successfully sent!")
            time_of_last_data = time.time()

    rdt.disconnect()
