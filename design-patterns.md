# Creational Design Patterns - Quick Notes

## Singleton

### Problem
You need exactly one instance of a class shared across the entire system.
> Multiple instances cause inconsistencies, resource conflicts, or waste. Like a government—a country needs one official government, not several competing ones.

### Solution
Make the class responsible for creating and managing its single instance.
> Use a private constructor and static method to access the instance. The class controls when and how it's instantiated.

```python
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.host = "localhost"
            cls._instance.port = 5432
        return cls._instance
    
    def connect(self):
        return f"Connected to {self.host}:{self.port}"

# Usage - always returns same instance
db1 = DatabaseConnection()
db2 = DatabaseConnection()

print(db1 is db2)  # True
db1.host = "192.168.1.100"
print(db2.host)    # "192.168.1.100"
```

### Usage 
**General:**
- Global logger
- Configuration manager

**IoT:**
- One Modbus Master per process
- Shared MQTT client or cloud connection pool

---

## Factory Method

### Problem
You need to create objects but don't know the exact type until runtime.
> Hardcoding object creation makes code rigid—adding new types requires modifying existing code everywhere. Like ordering "a vehicle" without specifying car, truck, or motorcycle until delivery.

### Solution
Define an interface for creating objects, but let subclasses decide which class to instantiate.
> The creator class works with the product interface, while concrete creators return specific implementations. Client code stays the same when new types are added.

```python
from abc import ABC, abstractmethod

class DataSource(ABC):
    @abstractmethod
    def read(self): pass

class FileSource(DataSource):
    def read(self):
        return "Reading from file..."

class DatabaseSource(DataSource):
    def read(self):
        return "Reading from database..."

# Factory
class DataProcessor:
    def create_source(self, source_type: str) -> DataSource:
        if source_type == "file":
            return FileSource()
        elif source_type == "db":
            return DatabaseSource()
        raise ValueError(f"Unknown source: {source_type}")

# Usage
processor = DataProcessor()
source = processor.create_source("file")
data = source.read()
```

### Usage
**General:**
- Payment processing systems
- Document exporters
- Notification delivery

**IoT:**
- Sensor driver selection
- Protocol switching at runtime
- Data formatter selection

---

## Abstract Factory

### Problem
You need to create families of related objects that must work together.
> Creating incompatible combinations leads to errors. Like mixing furniture styles—a Windows button with Mac scrollbar looks wrong and may not work properly.

### Solution
Provide an interface for creating families of related objects.
> Each concrete factory produces a complete set of compatible products. Switch factories to switch entire product families at once.

```python
from abc import ABC, abstractmethod

# Abstract products
class Button(ABC):
    @abstractmethod
    def render(self): pass

class Checkbox(ABC):
    @abstractmethod
    def render(self): pass

# Windows family
class WindowsButton(Button):
    def render(self): return "Windows button"

class WindowsCheckbox(Checkbox):
    def render(self): return "Windows checkbox"

# Mac family
class MacButton(Button):
    def render(self): return "Mac button"

class MacCheckbox(Checkbox):
    def render(self): return "Mac checkbox"

# Abstract factory
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: pass
    @abstractmethod
    def create_checkbox(self) -> Checkbox: pass

# Concrete factories
class WindowsFactory(GUIFactory):
    def create_button(self): return WindowsButton()
    def create_checkbox(self): return WindowsCheckbox()

class MacFactory(GUIFactory):
    def create_button(self): return MacButton()
    def create_checkbox(self): return MacCheckbox()

# Usage
factory = WindowsFactory()
button = factory.create_button()
checkbox = factory.create_checkbox()
```

### Usage
**General:**
- UI theme components
- Cross-platform widget sets
- Database driver families

**IoT:**
- Modbus RTU vs TCP protocol stacks
- Cloud provider service sets
- Sensor ecosystem components

---

## Builder

### Problem
Creating complex objects with many optional parameters leads to unreadable constructors.
> The telescoping constructor problem makes code hard to read and error-prone. Like ordering a custom sandwich—easier to say "add this, add that" than listing everything upfront.

### Solution
Construct objects step-by-step using a builder interface.
> Build only what you need, in any order, with readable method chaining. Each method returns the builder for fluent interface.

```python
class HttpRequest:
    def __init__(self):
        self.method = "GET"
        self.url = ""
        self.headers = {}
        self.timeout = 30

class HttpRequestBuilder:
    def __init__(self):
        self._request = HttpRequest()
    
    def method(self, method: str):
        self._request.method = method
        return self
    
    def url(self, url: str):
        self._request.url = url
        return self
    
    def header(self, key: str, value: str):
        self._request.headers[key] = value
        return self
    
    def timeout(self, seconds: int):
        self._request.timeout = seconds
        return self
    
    def build(self) -> HttpRequest:
        return self._request

# Usage - fluent interface
request = (HttpRequestBuilder()
           .method("POST")
           .url("https://api.example.com/data")
           .header("Content-Type", "application/json")
           .timeout(10)
           .build())
```

### Usage
**General:**
- Complex configuration objects
- SQL query builders
- Test data creation

**IoT:**
- Modbus connection configuration
- Sensor setup and calibration
- MQTT client initialization

---

## Prototype

### Problem
Creating new objects from scratch is expensive when initialization is complex.
> Recreating objects with database queries, file loading, or heavy computation wastes resources. Like photocopying—faster to copy than retype the entire document.

### Solution
Clone existing objects instead of creating new ones.
> Objects implement their own cloning logic, including deep copies of internal state. Modify the clone without affecting the original.

```python
from copy import deepcopy

class SensorConfig:
    def __init__(self, pin, threshold):
        self.pin = pin
        self.threshold = threshold
        self.calibration = []
    
    def clone(self):
        return deepcopy(self)

# Usage
base = SensorConfig(pin="A0", threshold=30)
base.calibration = [1.0, 1.1, 0.9]

sensor1 = base.clone()
sensor1.pin = "A1"
sensor1.threshold = 25

sensor2 = base.clone()
sensor2.pin = "A2"

# Independent copies
sensor1.calibration.append(1.2)
print(len(base.calibration))     # 3
print(len(sensor1.calibration))  # 4
```

### Usage
**General:**
- Game character templates
- Document templates
- Test fixture cloning

**IoT:**
- Sensor configuration templates
- Modbus register map copying
- Network packet templates

---

## Quick Comparison

| Pattern | Creates | When to Use |
|---------|---------|-------------|
| **Factory Method** | One type at a time | Type varies at runtime |
| **Abstract Factory** | Related families | Need compatible sets |
| **Builder** | Complex objects | Many optional parameters |
| **Prototype** | By cloning | Creation is expensive |
| **Singleton** | Exactly one | Need single shared instance |

## Pattern Selection Guide

**Choose based on your problem:**

- Need one global instance? → **Singleton**
- Creating from scratch is slow? → **Prototype**  
- Many optional parameters? → **Builder**
- Need compatible sets? → **Abstract Factory**
- Type determined at runtime? → **Factory Method**

---

# Structural Design Patterns - Quick Notes

## Adapter

### Problem
You need to make incompatible interfaces work together.
> Like using a US plug in a European socket—you need an adapter to convert one interface to another. Without it, components can't communicate despite having the functionality you need.

### Solution
Create a wrapper that converts one interface into another that clients expect.
> The adapter translates calls from the client's expected interface to the adaptee's actual interface. Client code doesn't know about the adaptation.

```python
# Existing class with incompatible interface
class LegacyTemperatureSensor:
    def get_temp_fahrenheit(self):
        return 77.0

# Target interface we want
class TemperatureSensor:
    def read_celsius(self):
        pass

# Adapter
class TemperatureAdapter(TemperatureSensor):
    def __init__(self, legacy_sensor):
        self.legacy_sensor = legacy_sensor
    
    def read_celsius(self):
        fahrenheit = self.legacy_sensor.get_temp_fahrenheit()
        return (fahrenheit - 32) * 5/9

# Usage
legacy = LegacyTemperatureSensor()
sensor = TemperatureAdapter(legacy)
print(sensor.read_celsius())  # 25.0
```

### Usage
**General:**
- Third-party library integration
- Legacy code modernization
- API version compatibility

**IoT:**
- Sensor protocol conversion
- Modbus to MQTT gateway
- Unit conversion wrappers

---

## Bridge

### Problem
You need to decouple abstraction from implementation so both can vary independently.
> Like a remote control and TV—you want any remote to work with any TV brand. Without Bridge, you'd need RemoteSony, RemoteSamsung, RemoteLG multiplied by BasicRemote, AdvancedRemote.

### Solution
Separate the abstraction hierarchy from the implementation hierarchy.
> Abstraction contains a reference to implementation. Changes to either don't affect the other.

```python
# Implementation interface
class DataTransport:
    def send(self, data): pass

# Concrete implementations
class SerialTransport(DataTransport):
    def send(self, data):
        return f"Sending via Serial: {data}"

class WiFiTransport(DataTransport):
    def send(self, data):
        return f"Sending via WiFi: {data}"

# Abstraction
class DataLogger:
    def __init__(self, transport: DataTransport):
        self.transport = transport
    
    def log(self, message):
        return self.transport.send(message)

# Extended abstraction
class SecureDataLogger(DataLogger):
    def log(self, message):
        encrypted = f"[ENCRYPTED]{message}"
        return self.transport.send(encrypted)

# Usage
logger = DataLogger(SerialTransport())
print(logger.log("Temperature: 25°C"))

secure = SecureDataLogger(WiFiTransport())
print(secure.log("Temperature: 25°C"))
```

### Usage
**General:**
- GUI frameworks with multiple platforms
- Database drivers with multiple backends
- Media players with various codecs

**IoT:**
- Data loggers with multiple transports
- Sensor readers with various protocols
- Display systems with different screens

---

## Composite

### Problem
You need to treat individual objects and compositions uniformly.
> Like a file system—folders contain files AND other folders. You want to perform operations on both without checking types.

### Solution
Create a tree structure where individual objects and compositions share the same interface.
> Clients treat single objects and compositions identically. Operations cascade down the tree.

```python
from abc import ABC, abstractmethod

# Component interface
class SensorComponent(ABC):
    @abstractmethod
    def read(self): pass

# Leaf
class TemperatureSensor(SensorComponent):
    def __init__(self, name):
        self.name = name
    
    def read(self):
        return f"{self.name}: 25°C"

# Composite
class SensorGroup(SensorComponent):
    def __init__(self, name):
        self.name = name
        self.children = []
    
    def add(self, component):
        self.children.append(component)
    
    def read(self):
        results = [f"{self.name}:"]
        for child in self.children:
            results.append(f"  {child.read()}")
        return "\n".join(results)

# Usage
floor1 = SensorGroup("Floor 1")
floor1.add(TemperatureSensor("Room A"))
floor1.add(TemperatureSensor("Room B"))

floor2 = SensorGroup("Floor 2")
floor2.add(TemperatureSensor("Room C"))

building = SensorGroup("Building")
building.add(floor1)
building.add(floor2)

print(building.read())
```

### Usage
**General:**
- File system hierarchies
- UI component trees
- Organization structures

**IoT:**
- Sensor network topologies
- Device group management
- Hierarchical configuration systems

---

## Decorator

### Problem
You need to add responsibilities to objects dynamically without affecting other objects.
> Like adding toppings to pizza—each topping wraps the pizza and adds cost/features. Creating PizzaWithCheese, PizzaWithCheeseAndMushrooms, etc. would explode into too many classes.

### Solution
Wrap objects in decorator objects that add new behavior.
> Decorators have the same interface as wrapped objects. Multiple decorators can be stacked.

```python
# Component interface
class DataStream:
    def write(self, data): pass

# Concrete component
class FileStream(DataStream):
    def write(self, data):
        return f"Writing to file: {data}"

# Decorators
class EncryptedStream(DataStream):
    def __init__(self, stream: DataStream):
        self.stream = stream
    
    def write(self, data):
        encrypted = f"[ENCRYPTED({data})]"
        return self.stream.write(encrypted)

class CompressedStream(DataStream):
    def __init__(self, stream: DataStream):
        self.stream = stream
    
    def write(self, data):
        compressed = f"[COMPRESSED({data})]"
        return self.stream.write(compressed)

# Usage
stream = FileStream()
stream = EncryptedStream(stream)
stream = CompressedStream(stream)
print(stream.write("sensor data"))
# Writing to file: [COMPRESSED([ENCRYPTED(sensor data)])]
```

### Usage
**General:**
- I/O stream processing
- GUI component styling
- Logging with filters

**IoT:**
- Data encryption layers
- Protocol wrapping
- Sensor data filtering

---

## Facade

### Problem
You need a simple interface to a complex subsystem.
> Like a car's steering wheel—it hides the complexity of steering mechanism, power steering, wheel alignment. You just turn the wheel.

### Solution
Provide a unified interface to a set of interfaces in a subsystem.
> Facade defines a higher-level interface that makes the subsystem easier to use. It doesn't hide the subsystem, just simplifies access.

```python
# Complex subsystem
class ModbusConnection:
    def open_serial(self, port, baud): return "Serial opened"
    def set_timeout(self, ms): return "Timeout set"

class ModbusProtocol:
    def set_slave_id(self, id): return "Slave ID set"
    def build_request(self, reg): return f"Request for register {reg}"

class ModbusTransport:
    def send(self, data): return f"Sent: {data}"
    def receive(self): return "Response received"

# Facade
class ModbusClient:
    def __init__(self):
        self.connection = ModbusConnection()
        self.protocol = ModbusProtocol()
        self.transport = ModbusTransport()
    
    def read_register(self, port, slave_id, register):
        self.connection.open_serial(port, 9600)
        self.connection.set_timeout(1000)
        self.protocol.set_slave_id(slave_id)
        request = self.protocol.build_request(register)
        self.transport.send(request)
        return self.transport.receive()

# Usage - simple interface
client = ModbusClient()
result = client.read_register("/dev/ttyUSB0", 1, 0)
```

### Usage
**General:**
- Library wrappers
- API simplification
- Framework initialization

**IoT:**
- Modbus client libraries
- Sensor initialization sequences
- Cloud service SDKs

---

## Flyweight

### Problem
You need to support large numbers of fine-grained objects efficiently.
> Like rendering text—storing font, size, color for each character wastes memory. Better to share common properties (intrinsic state) and store only position (extrinsic state).

### Solution
Share common data between multiple objects instead of storing it in each object.
> Split object state into intrinsic (shared) and extrinsic (unique). Factory ensures flyweights are shared properly.

```python
# Flyweight
class SensorType:
    def __init__(self, model, calibration):
        self.model = model
        self.calibration = calibration
    
    def read(self, pin):
        return f"{self.model} on {pin}: {self.calibration}°C"

# Flyweight factory
class SensorFactory:
    def __init__(self):
        self._types = {}
    
    def get_sensor_type(self, model, calibration):
        key = (model, calibration)
        if key not in self._types:
            self._types[key] = SensorType(model, calibration)
        return self._types[key]

# Context
class Sensor:
    def __init__(self, sensor_type, pin):
        self.sensor_type = sensor_type  # Shared
        self.pin = pin  # Unique

# Usage
factory = SensorFactory()
dht22_type = factory.get_sensor_type("DHT22", 1.0)

sensors = [
    Sensor(dht22_type, "A0"),
    Sensor(dht22_type, "A1"),
    Sensor(dht22_type, "A2"),
]

for sensor in sensors:
    print(sensor.sensor_type.read(sensor.pin))
```

### Usage
**General:**
- Text rendering systems
- Game particle systems
- Cached database rows

**IoT:**
- Large sensor networks with few types
- Network packet pools
- Configuration sharing across devices

---

## Proxy

### Problem
You need to control access to an object or add functionality without changing it.
> Like a credit card—it's a proxy for your bank account. It adds access control, logging, lazy loading without changing the bank account itself.

### Solution
Provide a surrogate that controls access to the real object.
> Proxy has the same interface as the real object. It can add pre/post processing, lazy initialization, access control, or logging.

```python
# Subject interface
class SensorReader:
    def read(self): pass

# Real subject
class RemoteSensor(SensorReader):
    def __init__(self, address):
        self.address = address
        print(f"Connecting to sensor at {address}...")
    
    def read(self):
        return f"Data from {self.address}: 25°C"

# Proxy
class SensorProxy(SensorReader):
    def __init__(self, address):
        self.address = address
        self._sensor = None
    
    def read(self):
        if self._sensor is None:  # Lazy initialization
            self._sensor = RemoteSensor(self.address)
        print("Access logged")
        return self._sensor.read()

# Usage
proxy = SensorProxy("192.168.1.10")  # No connection yet
print(proxy.read())  # Connects now
print(proxy.read())  # Uses existing connection
```

### Usage
**General:**
- Lazy loading
- Access control
- Logging and caching

**IoT:**
- Remote sensor access
- Network connection pooling
- Resource-intensive device initialization

---
# BEHAVIORAL PATTERNS

## Strategy

### Problem  
You have one piece of code that needs to do the same job in different ways depending on the situation, and you want to be able to switch the way instantly — even while the program is running.  
> Example: the same shopping cart must calculate shipping as “ground”, “air”, or “express” and the customer can change their mind right before paying.

### Solution  
Create a separate small class for each way of doing the job. The main class only keeps a reference to “the current way” and asks it to do the work. You can replace that reference anytime.

```python
class ShippingMethod:
    def cost(self, weight): ...

class Ground(ShippingMethod):
    def cost(self, weight): return weight * 2

class Air(ShippingMethod):
    def cost(self, weight): return weight * 10 + 50

class ShoppingCart:
    def __init__(self, method: ShippingMethod):
        self.method = method                     # holds the current strategy
    
    def switch_to(self, new_method: ShippingMethod):
        self.method = new_method                 # change behavior at any time
    
    def total(self, weight):
        return 100 + self.method.cost(weight)

# Usage – switch whenever you want
cart = ShoppingCart(Ground())
print(cart.total(10))           # 120
cart.switch_to(Air())
print(cart.total(10))           # 250
```

### Usage (you’ll see this every week)
- Payment methods (card / PayPal / crypto)  
- Modbus RTU vs TCP vs BLE  
- Choosing CPU / GPU / TinyML inference

---

## Observer (Pub/Sub)

### Problem  
When one object changes (e.g. a sensor gets a new reading), many other objects (display, cloud, alarm, logger) need to react immediately, but you don’t want them glued together forever.  
> Example: a fire alarm goes off → every siren, phone, and sprinkler must react at once.

### Solution  
Let objects register (“subscribe”) with the source. Whenever the source changes, it calls a method on every registered object automatically.

```python
class Sensor:
    def __init__(self):
        self._listeners = []          # list of subscribers
        self._value = None
    
    def subscribe(self, listener):
        self._listeners.append(listener)   # add new listener
    
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, new_value):
        self._value = new_value
        for listener in self._listeners:
            listener.update(new_value)         # notify everyone

def show_on_screen(temp):
    print(f"Screen shows: {temp}°C")

def upload_to_cloud(temp):
    print(f"Cloud received: {temp}°C")

# Usage
temp_sensor = Sensor()
temp_sensor.subscribe(show_on_screen)
temp_sensor.subscribe(upload_to_cloud)
temp_sensor.value = 26.3   # both functions run instantly
```

### Usage
- Sensor → dashboard / cloud / buzzer  
- MQTT message callbacks  
- Button clicks in apps

---

## Decorator (Wrapper)

### Problem  
You want to add helpful extras (logging, automatic retry, caching, authentication) to an existing object, and you want any combination of those extras without creating dozens of new classes.  
> Example: you want a Modbus client that can retry, log every call, and measure time — and you want to turn each feature on or off independently.

### Solution  
Create tiny wrapper classes. Each wrapper holds the original object and adds one extra feature. You can stack them like layers of an onion.

```python
class ModbusDevice:
    def read(self, addr):
        print(f"Reading register {addr}")
        return 999

class RetryWrapper:
    def __init__(self, device): self.device = device
    def read(self, addr):
        for i in range(3):
            try:
                return self.device.read(addr)
            except:
                if i == 2: raise
                print("Retrying...")

class LogWrapper:
    def __init__(self, device): self.device = device
    def read(self, addr):
        print(f"→ Calling read({addr})")
        result = self.device.read(addr)
        print(f"← Got {result}")
        return result

# Stack in any order you like
device = LogWrapper(RetryWrapper(ModbusDevice()))
device.read(40001)
```

### Usage
- Automatic retry + logging for network calls  
- Adding metrics or caching to any function  
- Web middleware stacks

---

## Command

### Problem  
You need to represent “do this action” as something you can save, delay, queue, undo, or send over the network.  
> Example: every button on a smart-home remote must remember exactly what it should do when pressed.

### Solution  
Turn each action into its own tiny object that knows everything needed to perform it.

```python
class Light:
    def turn_on(self):  print("Light is ON")
    def turn_off(self): print("Light is OFF")

class Command:
    def execute(self): ...

class TurnOn(Command):
    def __init__(self, light): self.light = light
    def execute(self): self.light.turn_on()

class TurnOff(Command):
    def __init__(self, light): self.light = light
    def execute(self): self.light.turn_off()

class RemoteButton:
    def __init__(self): self.command = None
    def set_command(self, cmd): self.command = cmd
    def press(self):
        if self.command: self.command.execute()

# Usage
light = Light()
button = RemoteButton()
button.set_command(TurnOn(light))
button.press()   # Light is ON
button.set_command(TurnOff(light))
button.press()   # Light is OFF
```

### Usage
- Physical or touchscreen remote controls  
- Undo/redo in editors  
- Queuing commands when device is offline

---

## Template Method

### Problem  
You have a process that always follows the same big steps, but a few of those steps are done differently depending on the device or file type.  
> Example: every firmware update does connect → erase → write → verify → reboot, but the erase and write steps are different for each chip family.

### Solution  
Write the fixed steps once in a parent class. Leave the steps that change as empty methods that each child class must fill in.

```python
class FirmwareFlasher:
    def flash(self):
        self.connect()
        self.erase()
        self.write()
        self.verify()
        self.reboot()
        print("Flash complete")

    def connect(self): print("Connected to bootloader")
    def reboot(self):  print("Device restarted")
    
    def erase(self):   ...  # child must implement
    def write(self):   ...
    def verify(self):  ...

class Nrf52Flasher(FirmwareFlasher):
    def erase(self):   print("Erasing all flash")
    def write(self):   print("Writing via nRF Connect")
    def verify(self):  print("CRC check OK")
```

### Usage
- Device flashing / provisioning  
- Data import/export (CSV / JSON / XML)  
- Test case base class (setup → run → cleanup)
