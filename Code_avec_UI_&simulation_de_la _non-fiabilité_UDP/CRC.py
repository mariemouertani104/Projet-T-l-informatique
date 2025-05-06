def to_bin(data):
    # Convert data to binary string
    return ''.join(format(byte, '08b') for byte in data)


class CRC:
    def __init__(self):
        self.G="1101" # Generator polynomial representation X^3 + X^2 + 1
        
    def generate(self, data):
        data=to_bin(data)
        # Append 3 zeros to data
        P = data + '000'
        # Convert data to list of integers
        P = [int(bit) for bit in P]
        # Convert generator polynomial to list of integers
        G = [int(bit) for bit in self.G]
        # Perform division
        for i in range(len(P) - len(G) + 1):
            if P[i] == 1:
                for j in range(len(G)):
                    P[i + j] ^= G[j]
        
        new_data = data+(''.join(map(str, P[-len(G) + 1:])))
        
        # Convert binary string to bytes
        new_data = int(new_data, 2).to_bytes((len(new_data) + 7) // 8, byteorder='big')
        
        return new_data  
    def check(self, data):
        # Convert data to binary string
        data = to_bin(data)
        # Convert data to list of integers
        P = [int(bit) for bit in data]
        # Convert generator polynomial to list of integers
        G = [int(bit) for bit in self.G]
        # Perform division
        for i in range(len(P) - len(G) + 1):
            if P[i] == 1:
                for j in range(len(G)):
                    P[i + j] ^= G[j]
        # Check if the remainder is zero
        return all(bit == 0 for bit in P[-len(G) + 1:])
        
    def get_data(self, generated_data):
        binary_data = to_bin(generated_data)
        # Remove the CRC bits (last 3 bits) from the binary data
        new_data = binary_data[:-3]
        # Convert binary string to bytes
        new_data = int(new_data, 2).to_bytes((len(new_data) + 7) // 8, byteorder='big')
        return new_data

if __name__ == "__main__":
    crc=CRC()
    data = "hello" 
    print("Data:",data) 
    print("Binary of Data:",to_bin(data.encode()))
    data = data.encode()
    generated_data = crc.generate(data)
    print("Generated Data:", generated_data.decode())
    if crc.check(generated_data):
        print("Data is valid")
        print("Original Data:", crc.get_data(generated_data).decode())
    else:
        print("Data is corrupted")

