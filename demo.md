# Demo App

### App summary

1. A vibration sensor (accelerometer) streams 3-axis motion data over a serial cable (Modbus RTU).
2. The gateway's NPU (AI chip) runs an AI model that classifies the motion.
3. A live web dashboard shows it all: waveform, frequency spectrum, sensor metrics, and the predicted motion class (e.g. steady, shake, circle).

Everything runs on the Matrix800 — no cloud, no PC.

> *Key idea: The AI model is trained once on a PC and never retrained by the user. Instead, the user records a few seconds of each motion, and the app builds a small classifier "head" in seconds, on the device — making the demo fully interactive.*
> 

### Architecture

Sensor → Modbus `read input` → Decode Modbus  → Accumulate sample batch `2604, 3` → NPU backbone `128-d vectors inference`→ CPU head `fingerprint classification` → Calculate last `N` results vote → Snapshot Bus → SSE push → Browser dashboard

#### Full Architecture

```
┌─ HARDWARE ─────────────────────────────────────────────────────────────────────┐
│  Tri-axial accelerometer  ──RS485 / Modbus RTU @ 3 Mbps──>  USB-serial adapter │
│  samples X,Y,Z @ ~7500 Hz                                    /dev/ttyUSB0..3   │
└────────────────────────────────────────────────────────────────────────────────┘
│
════════════════ MATRIX800 GATEWAY (ARM Linux, Python + NPU) ════════════════════
│
┌─ W1  sensor_reader.py — ONE PROCESS PER SENSOR (own GIL, SCHED_FIFO) ──────────┐
│                                                                                │
│   fast_modbus.py  (custom ~100-line client, CRC-checked)                       │
│     • on connect: write sample-rate reg 0x01  → resets sensor FIFO             │
│     • loop: FC04 read reg 0x02  → "N waiting" + N raw uint16                   │
│     • decode: uint16 → int16 → × (1/8192) → float32 G, reshape (-1,3)          │
│                                                                                │
│           ┌───────────────┬──────────────────┬──────────────────┐              │
│           ↓               ↓                  ↓                  ↓              │
│     recorder.feed()   accumulate         accumulate         FC03 metrics       │
│     (local disk,      2604-sample        217-sample         (RMS,kurtosis…)    │
│      no IPC)          window, hop=1302   chunk              slow, 1-at-a-time  │
│           │               │                  │                  │              │
│      data/*.bin      window_queue        raw_queue         metrics_queue       │
│      float32 XYZ     (~6/s, drop-old)    (~36/s)           (every 2–5 s)       │
└───────────────────────────┼──────────────────┼──────────────────┼──────────────┘
       cross-process mp.Queue (spawn)          │                  │
                            ↓                  ↓                  ↓
┌─ MAIN PROCESS (threads share model + state) ───────────────────────────────────┐
│                                                                                │
│  W2 InferenceWorker (1 thread)         raw-drain thread        metrics-drain   │
│  ┌──────────────────────────────┐    ┌───────────────────┐   ┌──────────────┐  │
│  │ get window (2604,3)          │    │ WaveformAggregator│   │ per-port     │  │
│  │ quantize int8 (clip+cast)    │    │  ring buffer ~2 s │   │ LatestSlot   │  │
│  │ ── BACKBONE on NPU ──────────│    │  .append(chunk)   │   │ (metrics)    │  │
│  │   [libteflon.so] delegate    │    └─────────┬─────────┘   └──────┬───────┘  │
│  │ → 128-d embedding            │     waveform_tick (30 Hz):        │          │
│  │ ── HEAD on CPU ──────────────│     raw scroll + FFT (~6 Hz)      │          │
│  │   cosine sim vs prototypes   │              │                    │          │
│  │ → class_id, confidence       │         WaveformBus          MetricsBus      │
│  └──────────┬───────────────────┘              │                    │          │
│             ↓                                  │                    │          │
│      RollingPredictions (deque=7)              │                    │          │
│      majority vote; latch every 2 pushes       │                    │          │
│             │                                  │                    │          │
│         SnapshotBus.bump()                     │                    │          │
│             │                                  │                    │          │
│  ┌──────────┴──────────────────────────────────┴────────────────────┴───────┐  │
│  │  W3  [app.py] — Flask. SSE endpoints push the instant a bus bumps:       │  │
│  │   /api/stream (predictions) · /api/waveform_stream · /api/metrics_stream │  │
│  └───────────────────────────────────┬──────────────────────────────────────┘  │
│                                      │                                         │
│   [trainer.py]: borrows W2's interpreter → embeds recordings → writes          │
│   classifier_head.json → W2.reload_head() (hot swap, no restart)               │
└──────────────────────────────────────┼─────────────────────────────────────────┘
               Server-Sent Events (one open HTTP conn, server push)
═══════════════════════════════════════┼═════════════════════════════════════════
                                       ↓
┌─ BROWSER (dashboard.html + app.js, uPlot) ─────────────────────────────────────┐
│  /waveform+FFT  ·  /inference  ·  /metrics  ·  /record  ·  /train  ·  /settings│
└────────────────────────────────────────────────────────────────────────────────┘
```

### NPU part

Model is divided into 2 pieces:

1. Backbone `*_int8.tflite` — frozen CNN on the NPU
    1. Input: Sample batch `2604, 3` → 2604 samples on 3 axis `x, y, z`
    2. Output: 128-dimension vectors of the motion → `fingerprint` 
2. Head `.json` — tiny, on CPU. 
    1. Stores an average `fingerprint` per class
    2. classify by cosine similarity to the nearest `fingerprint`

Heavy math is fixed on the NPU, "training" is just averaging vectors

# Useful notes

### Talking to the sensor (Modbus RTU)

1. **Serial:** 3 Mbps, 8N1. Raw streaming needs 3 Mbps (115200 only does slow metric reads)
2. **On connect:** write sample rate to reg 0x01 (FC06) — this also resets the sensor's FIFO, so you start with fresh data 
3. **Packet cap:** a single Modbus read maxes out at 125 registers (~123 = 41 XYZ triplets), but the sensor pumps ~23,400 regs/s. So you can't read a whole window at once — poll in small packets and recombine
4. **Read count:** register 0 of every FC04 reply is the fresh "samples waiting" count — use it to size your next read (cap the read at 123)
5. **Decode:** uint16 → int16 → ÷ 8192 → G
6. **Computed metric**s**:** FC03 — Slow (up to seconds) and each must be read one address at a time (a block read returns garbage)
7. Python Library: on 1 sensor read, `pymodbus` is fine. But for 4 sensors, use `pyserial`.

### Running your model on the NPU (the deployment mechanics)

Whatever model you bring, the steps to get it onto the NPU are always these:

```python
from ai_edge_litert.interpreter import Interpreter, load_delegate

delegate = load_delegate("/usr/local/lib/aarch64-linux-gnu/libteflon.so")  # the NPU
interp   = Interpreter(model_path="a_model.tflite", experimental_delegates=[delegate])
interp.allocate_tensors()

# per input: quantize → set_tensor → invoke → get_tensor → dequantize
```

Your `.tflite` must be fully int8 (input and output tensors, not just weights). If using NXP’s path, model must be vela compiled.    

### Gateway system setup (deployment checklist)

- [ ]  **NPU delegate:** located at either `/usr/local/lib/aarch64-linux-gnu/libteflon.so` or `/usr/lib/libethosu_delegate.so`
- [ ]  **Ports:** sensors appear as `/dev/ttyUSB0..3` — needs root for serial + NPU
- [ ]  **Serial latency tuning:** drop USB latency from 16ms to 1ms or you can't sustain 7812 Hz:

```python
echo 1 > /sys/bus/usb-serial/devices/ttyUSB*/latency_timer
```

- [ ]  **Bundle your dependencies with the app:** Ship the pip-installed libraries (pymodbus, pyserial, etc.) alongside your code — either a `venv` on the device, or a plain local `site-packages/` folder you add to `sys.path` (The embedded Python doesn't have them system-wide)

# Python ↔ Modbus Sensor

1. Open the serial port (USB-RS485 adapter)

```python
import serial, struct, time, numpy as np

ser = serial.Serial('/dev/ttyUSB0', baudrate=3000000, 
                       bytesize=8, parity='N', 
                       stopbits=1, timeout=0.05)
```

2. CRC-16 (Modbus RTU) — build the table once

```python
_CRC = []
for i in range(256):
    c = i
    for _ in range(8):
        c = (c >> 1) ^ 0xA001 if c & 1 else c >> 1
    _CRC.append(c)

def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc = (crc >> 8) ^ _CRC[(crc ^ b) & 0xFF]
    return crc
```

3. Modbus RTU read/write = [slave, func, addr, count] + CRC-16

```python
def modbus_read(func, addr, count):
      # Registers are big-endian (>H); the CRC on the wire is little-endian (<H).
      req  = struct.pack('>BBHH', 1, func, addr, count)     # slave id = 1
      req += struct.pack('<H', crc16(req))
      ser.reset_input_buffer()
      ser.write(req)
      resp = ser.read(5 + 2 * count)                        # slave+func+len + data + crc(2)
      if len(resp) != 5 + 2 * count:                        # short read → caller resyncs
          raise IOError(f"short read: {len(resp)}/{5 + 2*count} bytes")
      if crc16(resp[:-2]) != (resp[-1] << 8 | resp[-2]):    # CRC little-endian on wire
          raise IOError("CRC mismatch")
      return list(struct.unpack(f'>{count}H', resp[3:3 + 2*count]))   # uint16s

  def modbus_write(addr, value):
      req  = struct.pack('>BBHH', 1, 6, addr, value & 0xFFFF)
      req += struct.pack('<H', crc16(req))
      ser.reset_input_buffer()
      ser.write(req)
      ser.read(8)                                           # response echoes the request

```

4. Set sample rate (FC06) — also resets the sensor FIFO

```python
modbus_write(0x01, 7812)
```

5. Stream raw XYZ — read in packets, recombine into windows

```python
MAX_PACKET  = 41 * 3
WINDOW_SIZE = 2604
HOP_SIZE    = 1302

def resync():
    old, ser.timeout = ser.timeout, 0.03
    while ser.read(256):
        pass
    ser.timeout = old
    ser.reset_input_buffer()

buffer   = np.empty((0, 3), np.float32)
data_len = modbus_read(4, 0x02, 1)[0]

while True:
    try:
        # Three-branch read, driven by how many samples are waiting.
        if data_len >= MAX_PACKET:
            regs = modbus_read(4, 0x02, 1 + MAX_PACKET)
        elif data_len <= 6:
            time.sleep(0.001)
            data_len = modbus_read(4, 0x02, 1)[0]
            continue
        else:
            regs = modbus_read(4, 0x02, 1 + data_len)
    except IOError:
        resync()
        continue

    data_len = regs[0]

    # Decode: uint16 → int16 (bit reinterpret, NOT astype) → ÷8192 → G, shape (-1,3)
    raw     = np.array(regs[1:], dtype=np.uint16).view(np.int16)
    samples = (raw / 8192.0).reshape(-1, 3).astype(np.float32)
    buffer  = np.vstack((buffer, samples))

    # Recombine: emit fixed WINDOW_SIZE windows with 50 % overlap, keep the tail.
    while buffer.shape[0] >= WINDOW_SIZE:
        window = buffer[:WINDOW_SIZE]                # → feed to the NPU backbone
        print("window", window.shape)
        buffer = buffer[HOP_SIZE:]                   # drop oldest HOP_SIZE, keep overlap
```
