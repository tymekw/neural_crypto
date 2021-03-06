import math
import socket
import pickle
import threading

import bits
import numpy as np
import TPM


class AliceServer:
    def __init__(self):
        self.N = 10
        self.K = 5
        self.L = 2
        self.HOST = '127.0.0.1'
        self.PORT = 65432
        self.s = None
        self.conn = None
        self.addr = None
        self.machine_conf = None
        self.W = None
        self.aliceTPM = None
        self.X = None
        self.bits = bits.Bits(self.L)
        self.seed = 1
        self.bits_length = 1000

    def set_bits_length(self, length):
        self.bits_length = length

    def set_seed(self, seed):
        self.seed = seed

    def set_N(self, N):
        self.N = N

    def set_K(self, K):
        self.K = K

    def set_L(self, L):
        self.L = L
        self.bits.change_L(self.L)

    def choose_machine_details(self, N, K, L):
        self.N = N
        self.K = K
        self.L = L

    def bind(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("before bind")
        self.s.bind((self.HOST, self.PORT))
        print("bind")

        self.s.listen()
        self.conn, self.addr = self.s.accept()
        print("binded")
        return True

    def generate_bits(self):
        self.bits.generate_bits(self.seed, self.bits_length)

    def get_possible_N_K(self, w_len):
        factors = self.get_factors_list(w_len)
        return self.get_best_pair(factors)
        # return factors


    def get_factors_list(self, w_len=0):
        if w_len == 0:
            w_len = len(self.bits.bits_to_w())
        factors = []
        for i in range(1, w_len + 1):
            if w_len % i == 0:
                factors.append((i, int(w_len / i)))
        return factors

    # def get_factors_list(self, w_len):
    #     factors = []
    #     for i in range(1, w_len + 1):
    #         if w_len % i == 0:
    #             factors.append((i, int(w_len / i)))
    #     return factors

    def get_best_pair(self, factors):
        best_pair = None
        tmp = math.inf
        # print(factors)
        for factor_pair in factors:
            dif = max(factor_pair) - min(factor_pair)
            if tmp > dif:
                best_pair = factor_pair
                tmp = dif
        return best_pair

    # def check_N_K(self, N, K, bits_len):
    #     return N * K < bits_len

    def create_machine(self):
        W_len = len(self.bits.bits_to_w())
        # self.N, self.K = self.get_possible_N_K(W_len)
        self.W = self.bits.bits_to_arr(self.K, self.N)
        self.aliceTPM = TPM.Tpm(self.N, self.K, self.L, self.W)

    def send_machine_config(self):
        self.machine_conf = [self.N, self.K, self.L, self.seed, self.bits_length]
        data = pickle.dumps(self.machine_conf)
        self.conn.sendall(data)
        rec = self.conn.recv(1024)
        if pickle.loads(rec) == 'OK':
            return True

    def run_machine(self):
        print("waits")
        print(self.W)
        print(self.aliceTPM.W)
        for i in range(0, 150):
            print("inside loop")
            bob_tau = None
            self.aliceTPM.tau = 1
            while self.aliceTPM.tau != bob_tau:
                print("choose X")
                try:
                    self.s.listen()
                    self.conn, self.addr = self.s.accept()
                except:
                    print("socket error")

                self.X = np.random.choice([-1,1], size=(self.K, self.N))
                self.aliceTPM.calculate_tau(self.X)
                print("sending X")
                data = pickle.dumps(self.X)
                self.conn.sendall(data)
                print("X send")
                rec_tau = self.conn.recv(1000000)
                bob_tau = pickle.loads(rec_tau)

                if self.aliceTPM.tau == bob_tau:
                    data = pickle.dumps(1)
                    self.conn.sendall(data)
                    print("X chosen")
                else:
                    data = pickle.dumps(0)
                    self.conn.sendall(data)
                    print("X not chosen")
            print(i)
            self.W = self.aliceTPM.update_weights(self.X)

        print("outside loop")

        #ToDo check if W are the same
        bob_w = self.conn.recv(1000000)
        bob_wei = pickle.loads(bob_w)
        if np.array_equal(self.aliceTPM.W, bob_wei):
            print('dziala')

        print("done")

        print(self.aliceTPM.W)
        self.bits.bits = self.bits.arr_to_bits(self.aliceTPM.W, self.bits_length)
