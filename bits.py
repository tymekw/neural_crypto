import random
import numpy as np
import math

class Bits:
    def __init__(self, L):
        self.bits = None
        self.BER = 3
        self.type = 'random'
        self.L = L
        self.max_val = 2 * self.L

    def change_L(self, L):
        self.L = L
        self.max_val = 2 * self.L

    def generate_bits(self, seed, length):
        myrandom = random.Random(seed)
        b = myrandom.getrandbits(length)
        b = b
        b = bin(b)
        b = b[2:]
        if len(b) != length:
            b = '0' * (length - len(b)) + b
        self.bits = b

    def create_BER(self):
        b_list = [i for i in self.bits]
        if self.type == 'random':
            errors = int(len(b_list) * 0.01*self.BER)
            indexes = random.sample(range(0, len(b_list) - 1), errors)
            for i in indexes:
                if b_list[i] == "1":
                    b_list[i] = "0"
                else:
                    b_list[i] = "1"

        elif self.type == 'block':
            how_many_to_change = int(len(b_list) * 0.01*self.BER)
            start_idx = random.randint(0, len(b_list)- 1 - how_many_to_change)
            for i in range(how_many_to_change):
                if b_list[start_idx+i] == "1":
                    b_list[start_idx + i] = "0"
                else:
                    b_list[start_idx + i] = "1"

        self.bits = "".join(b_list)

    def bits_to_w(self):
        min_req_bits = math.ceil(math.log2(self.L + 1)) + 1
        bits_list = [self.bits[i:i + min_req_bits] for i in range(0, len(self.bits), min_req_bits)]
        if len(bits_list[-1]) < min_req_bits:
            bits_list[-1] = '0' * (min_req_bits - len(bits_list[-1])) + bits_list[-1]
        nums = []
        for number in bits_list:
            sign = 1 if number[0] == 0 else -1
            nums.append(sign*int("0b" +str(number[1:]),2))
        self.first_bin = None
        self.next_new = None
        nums = self.handle_bits_outside_range(nums)
        arr = np.array(nums)
        return arr


    def bits_to_arr(self, K, N):
        return np.reshape(self.bits_to_w(), (K, N))

    def handle_bits_outside_range(self, nums):
        for i, element in enumerate(nums):
            if element > self.L or element < -self.L :
                if not self.first_bin:
                    self.first_bin = bin(abs(element))
                    self.next_new = int('0b' + self.first_bin[3:], 2)
                else:
                    self.next_new = self.next_new + 1 if self.next_new < self.L else -self.L
                nums[i] = self.next_new
        return nums


    def arr_to_bits(self, arr, length):
        number_list = [i for sublists in arr.tolist() for i in sublists]
        result_bits  = ["1"+bin(int(i))[3:] if int(i)<0  else "0"+bin(int(i))[2:] for i in number_list]
        max_len = len(max(result_bits, key=len))
        b = ['0' * (max_len - len(bit)) + bit for bit in result_bits]
        b = ''.join(b)
        return b[:length]


