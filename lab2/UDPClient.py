import socket
import time

server_address = ('10.14.188.150', 12000)
num_pings = 10
timeout = 1.0

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(timeout)

rtt_times = []
lost_packets = 0

for sequence_number in range(1, num_pings + 1):
    send_time = time.time()
    ping_message = f'Ping {sequence_number} {send_time}'
    
    try:
        client_socket.sendto(ping_message.encode(), server_address)
        response, server = client_socket.recvfrom(1024)
        receive_time = time.time()
        rtt = receive_time - send_time
        rtt_times.append(rtt)
        print(f'Response from {server}: {response.decode()} | RTT: {rtt:.9f} seconds')
    except socket.timeout:
        print(f'Request timed out for sequence number {sequence_number}')
        lost_packets += 1

if rtt_times:
    min_rtt = min(rtt_times)
    max_rtt = max(rtt_times)
    avg_rtt = sum(rtt_times) / len(rtt_times)
    packet_loss_rate = (lost_packets / num_pings) * 100
    print(f'\nPing statistics:')
    print(f'Minimum RTT: {min_rtt:.9f} seconds')
    print(f'Maximum RTT: {max_rtt:.9f} seconds')
    print(f'Average RTT: {avg_rtt:.9f} seconds')
    print(f'Packet Loss Rate: {packet_loss_rate:.2f}%')
else:
    print('No responses received. All packets were lost.')

client_socket.close()
