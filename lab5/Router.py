import sys
import threading
import socket
import time
import json

class MyRouter:
    def __init__(self, router_id, router_port, config_file):
        self.router_id = router_id
        self.router_port = router_port
        self.neighbor_info = {}
        self.forwarding_table = {}
        self.distance_table = {}
        self.previous_nodes = {}
        self.running = True
        self.udp_socket = None

        self.read_config(config_file)
        self.udp_socket = self.setup_udp_socket(self.router_port)

    def read_config(self, file_name):
        with open(file_name, 'r') as file:
            lines = file.readlines()
            for line in lines[1:]:
                parts = line.strip().split()
                if len(parts) == 4:
                    neighbor_label, neighbor_id, link_cost, neighbor_port = parts
                    self.neighbor_info[int(neighbor_id)] = {
                        'label': neighbor_label,
                        'cost': int(link_cost),
                        'port': int(neighbor_port)
                    }

    def compute_dijkstra(self):
        self.distance_table = {node: float('inf') for node in self.neighbor_info.keys()}
        self.distance_table[self.router_id] = 0
        self.previous_nodes = {node: None for node in self.neighbor_info.keys()}
        known_nodes = set()

        while len(known_nodes) < len(self.distance_table):
            current_node = min(
                (node for node in self.distance_table if node not in known_nodes),
                key=self.distance_table.get
            )
            known_nodes.add(current_node)
            for neighbor, info in self.neighbor_info.items():
                if neighbor in self.distance_table and neighbor not in known_nodes:
                    distance = self.distance_table[current_node] + info['cost']
                    if distance < self.distance_table[neighbor]:
                        self.distance_table[neighbor] = distance
                        self.previous_nodes[neighbor] = current_node

        self.forwarding_table = self.build_forwarding_table(self.previous_nodes)
        self.print_routing_info()
        self.print_forwarding_table()

    def build_forwarding_table(self, previous_nodes):
        forwarding_table = {}
        for dest_node in self.neighbor_info.keys():
            if dest_node == self.router_id or dest_node not in previous_nodes:
                continue

            next_hop = dest_node
            path = [next_hop]
            while next_hop in previous_nodes and previous_nodes[next_hop] is not None:
                next_hop = previous_nodes[next_hop]
                path.append(next_hop)
                try:
                    first_hop = path[-2] if len(path) > 1 else None
                    if first_hop in self.neighbor_info:
                        next_hop_label = self.neighbor_info[first_hop]['label']
                        forwarding_table[dest_node] = next_hop_label
                    else:
                        forwarding_table[dest_node] = 'N/A'
                except KeyError as e:
                    print(f"KeyError: {e} for dest_node: {dest_node}, path: {path}")
        return forwarding_table

    def print_routing_info(self):
        print("Destination_Routerid Distance Previous_node_id")
        for destination, distance in self.distance_table.items():
            if destination == self.router_id:
                continue
            previous_node = self.previous_nodes.get(destination, 'N/A')
            print(f"{destination} {distance} {previous_node}")

    def print_forwarding_table(self):
        print("The forwarding table is displayed as shown below:")
        print("Destination_Routerid Next_hop_routerlabel")
        for destination, next_hop_label in self.forwarding_table.items():
            print(f"{destination} {next_hop_label}")

    def setup_udp_socket(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', port))
        return sock

    def send_link_state(self):
        while self.running:
            for neighbor_id, info in self.neighbor_info.items():
                try:
                    message = f"Link state from {self.router_id}"
                    self.udp_socket.sendto(
                        message.encode(), ('localhost', info['port'])
                    )
                except Exception as e:
                    print(f"Error sending message to router {neighbor_id} on port {info['port']}: {e}")
            time.sleep(1)

    def receive_and_broadcast(self):
        while self.running:
            try:
                message, address = self.udp_socket.recvfrom(1024)
                for neighbor_id, info in self.neighbor_info.items():
                    if info['port'] != address[1]:
                        self.udp_socket.sendto(message, ('localhost', info['port']))
            except ConnectionResetError:
                pass

    def run(self):
        send_thread = threading.Thread(target=self.send_link_state)
        receive_thread = threading.Thread(target=self.receive_and_broadcast)
        dijkstra_thread = threading.Thread(target=self.compute_dijkstra)

        send_thread.start()
        receive_thread.start()
        dijkstra_thread.start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            self.udp_socket.close()
            print("Shutting down router...")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python Router.py <routerid> <routerport> <configfile>")
        sys.exit(1)

    router = MyRouter(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
    router.run()
