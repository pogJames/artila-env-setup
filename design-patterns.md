# Creational Design Patterns

## Singleton

### Problem
You need exactly one instance of a class shared across the entire system.
> Multiple instances cause inconsistencies, resource conflicts, or waste. Like a government—a country needs one official government, not several competing ones.

### Solution
Make the class responsible for creating and managing its single instance.
> Use a private constructor and static method to access the instance. The class controls when and how it's instantiated.

### Code Examples

#### Python
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

#### Rust
```rust
use std::sync::{Arc, Mutex, Once};

struct DatabaseConnection {
    host: String,
    port: u16,
}

impl DatabaseConnection {
    fn instance() -> Arc<Mutex<DatabaseConnection>> {
        static mut INSTANCE: Option<Arc<Mutex<DatabaseConnection>>> = None;
        static ONCE: Once = Once::new();
        
        unsafe {
            ONCE.call_once(|| {
                let connection = DatabaseConnection {
                    host: "localhost".into(),
                    port: 5432,
                };
                INSTANCE = Some(Arc::new(Mutex::new(connection)));
            });
            INSTANCE.clone().unwrap()
        }
    }
    
    fn connect(&self) -> String {
        format!("Connected to {}:{}", self.host, self.port)
    }
}

// Usage
let db1 = DatabaseConnection::instance();
let db2 = DatabaseConnection::instance();

db1.lock().unwrap().host = "192.168.1.100".into();
println!("{}", db2.lock().unwrap().host);  // "192.168.1.100"
```

### Usage 
**General** 
- Global logger
- Configuration manager\
**Technical**
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

### Code Examples

#### Python
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

#### Rust
```rust
trait DataSource {
    fn read(&self) -> String;
}

struct FileSource;
impl DataSource for FileSource {
    fn read(&self) -> String { "Reading from file...".into() }
}

struct DatabaseSource;
impl DataSource for DatabaseSource {
    fn read(&self) -> String { "Reading from database...".into() }
}

struct DataProcessor;
impl DataProcessor {
    fn create_source(&self, source_type: &str) -> Box<dyn DataSource> {
        match source_type {
            "file" => Box::new(FileSource),
            "db" => Box::new(DatabaseSource),
            _ => panic!("Unknown source"),
        }
    }
}

// Usage
let processor = DataProcessor;
let source = processor.create_source("file");
let data = source.read();
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

### Code Examples

#### Python
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

#### Rust
```rust
trait Button { fn render(&self) -> String; }
trait Checkbox { fn render(&self) -> String; }

// Windows family
struct WindowsButton;
impl Button for WindowsButton {
    fn render(&self) -> String { "Windows button".into() }
}

struct WindowsCheckbox;
impl Checkbox for WindowsCheckbox {
    fn render(&self) -> String { "Windows checkbox".into() }
}

// Mac family
struct MacButton;
impl Button for MacButton {
    fn render(&self) -> String { "Mac button".into() }
}

struct MacCheckbox;
impl Checkbox for MacCheckbox {
    fn render(&self) -> String { "Mac checkbox".into() }
}

// Abstract factory
trait GUIFactory {
    fn create_button(&self) -> Box<dyn Button>;
    fn create_checkbox(&self) -> Box<dyn Checkbox>;
}

// Concrete factories
struct WindowsFactory;
impl GUIFactory for WindowsFactory {
    fn create_button(&self) -> Box<dyn Button> { Box::new(WindowsButton) }
    fn create_checkbox(&self) -> Box<dyn Checkbox> { Box::new(WindowsCheckbox) }
}

// Usage
let factory: &dyn GUIFactory = &WindowsFactory;
let button = factory.create_button();
let checkbox = factory.create_checkbox();
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

### Code Examples

#### Python
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

#### Rust
```rust
#[derive(Debug, Default)]
struct HttpRequest {
    method: String,
    url: String,
    headers: std::collections::HashMap<String, String>,
    timeout: u32,
}

struct HttpRequestBuilder {
    request: HttpRequest,
}

impl HttpRequestBuilder {
    fn new() -> Self {
        Self {
            request: HttpRequest {
                method: "GET".into(),
                timeout: 30,
                ..Default::default()
            }
        }
    }
    
    fn method(mut self, method: &str) -> Self {
        self.request.method = method.into();
        self
    }
    
    fn url(mut self, url: &str) -> Self {
        self.request.url = url.into();
        self
    }
    
    fn header(mut self, key: &str, value: &str) -> Self {
        self.request.headers.insert(key.into(), value.into());
        self
    }
    
    fn timeout(mut self, seconds: u32) -> Self {
        self.request.timeout = seconds;
        self
    }
    
    fn build(self) -> HttpRequest {
        self.request
    }
}

// Usage
let request = HttpRequestBuilder::new()
    .method("POST")
    .url("https://api.example.com/data")
    .header("Content-Type", "application/json")
    .timeout(10)
    .build();
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

### Code Examples

#### Python
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

#### Rust
```rust
#[derive(Clone, Debug)]
struct SensorConfig {
    pin: String,
    threshold: f32,
    calibration: Vec<f32>,
}

impl SensorConfig {
    fn new(pin: &str, threshold: f32) -> Self {
        Self {
            pin: pin.into(),
            threshold,
            calibration: Vec::new(),
        }
    }
}

// Usage
let mut base = SensorConfig::new("A0", 30.0);
base.calibration = vec![1.0, 1.1, 0.9];

let mut sensor1 = base.clone();
sensor1.pin = "A1".into();
sensor1.threshold = 25.0;

let sensor2 = base.clone();

// Independent copies
sensor1.calibration.push(1.2);
println!("{}", base.calibration.len());     // 3
println!("{}", sensor1.calibration.len());  // 4
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

# Structural Design Patterns

## Adapter

### Problem
You need to make incompatible interfaces work together.
> Like using a US plug in a European socket—you need an adapter to convert one interface to another. Without it, components can't communicate despite having the functionality you need.

### Solution
Create a wrapper that converts one interface into another that clients expect.
> The adapter translates calls from the client's expected interface to the adaptee's actual interface. Client code doesn't know about the adaptation.

### Code Examples

#### Python
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

#### Rust
```rust
// Existing struct with incompatible interface
struct LegacyTemperatureSensor;
impl LegacyTemperatureSensor {
    fn get_temp_fahrenheit(&self) -> f32 {
        77.0
    }
}

// Target trait
trait TemperatureSensor {
    fn read_celsius(&self) -> f32;
}

// Adapter
struct TemperatureAdapter {
    legacy_sensor: LegacyTemperatureSensor,
}

impl TemperatureSensor for TemperatureAdapter {
    fn read_celsius(&self) -> f32 {
        let fahrenheit = self.legacy_sensor.get_temp_fahrenheit();
        (fahrenheit - 32.0) * 5.0 / 9.0
    }
}

// Usage
let legacy = LegacyTemperatureSensor;
let sensor = TemperatureAdapter { legacy_sensor: legacy };
println!("{}", sensor.read_celsius());  // 25.0
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

### Code Examples

#### Python
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

#### Rust
```rust
// Implementation trait
trait DataTransport {
    fn send(&self, data: &str) -> String;
}

// Concrete implementations
struct SerialTransport;
impl DataTransport for SerialTransport {
    fn send(&self, data: &str) -> String {
        format!("Sending via Serial: {}", data)
    }
}

struct WiFiTransport;
impl DataTransport for WiFiTransport {
    fn send(&self, data: &str) -> String {
        format!("Sending via WiFi: {}", data)
    }
}

// Abstraction
struct DataLogger<T: DataTransport> {
    transport: T,
}

impl<T: DataTransport> DataLogger<T> {
    fn log(&self, message: &str) -> String {
        self.transport.send(message)
    }
}

// Usage
let logger = DataLogger { transport: SerialTransport };
println!("{}", logger.log("Temperature: 25°C"));

let wifi_logger = DataLogger { transport: WiFiTransport };
println!("{}", wifi_logger.log("Temperature: 25°C"));
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

### Code Examples

#### Python
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

#### Rust
```rust
// Component trait
trait SensorComponent {
    fn read(&self) -> String;
}

// Leaf
struct TemperatureSensor {
    name: String,
}

impl SensorComponent for TemperatureSensor {
    fn read(&self) -> String {
        format!("{}: 25°C", self.name)
    }
}

// Composite
struct SensorGroup {
    name: String,
    children: Vec<Box<dyn SensorComponent>>,
}

impl SensorGroup {
    fn new(name: &str) -> Self {
        Self {
            name: name.into(),
            children: Vec::new(),
        }
    }
    
    fn add(&mut self, component: Box<dyn SensorComponent>) {
        self.children.push(component);
    }
}

impl SensorComponent for SensorGroup {
    fn read(&self) -> String {
        let mut results = vec![format!("{}:", self.name)];
        for child in &self.children {
            results.push(format!("  {}", child.read()));
        }
        results.join("\n")
    }
}

// Usage
let mut floor1 = SensorGroup::new("Floor 1");
floor1.add(Box::new(TemperatureSensor { name: "Room A".into() }));
floor1.add(Box::new(TemperatureSensor { name: "Room B".into() }));

let mut building = SensorGroup::new("Building");
building.add(Box::new(floor1));
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

### Code Examples

#### Python
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

#### Rust
```rust
// Component trait
trait DataStream {
    fn write(&self, data: &str) -> String;
}

// Concrete component
struct FileStream;
impl DataStream for FileStream {
    fn write(&self, data: &str) -> String {
        format!("Writing to file: {}", data)
    }
}

// Decorators
struct EncryptedStream<T: DataStream> {
    stream: T,
}

impl<T: DataStream> DataStream for EncryptedStream<T> {
    fn write(&self, data: &str) -> String {
        let encrypted = format!("[ENCRYPTED({})]", data);
        self.stream.write(&encrypted)
    }
}

struct CompressedStream<T: DataStream> {
    stream: T,
}

impl<T: DataStream> DataStream for CompressedStream<T> {
    fn write(&self, data: &str) -> String {
        let compressed = format!("[COMPRESSED({})]", data);
        self.stream.write(&compressed)
    }
}

// Usage
let stream = FileStream;
let stream = EncryptedStream { stream };
let stream = CompressedStream { stream };
println!("{}", stream.write("sensor data"));
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

### Code Examples

#### Python
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

#### Rust
```rust
// Complex subsystem
struct ModbusConnection;
impl ModbusConnection {
    fn open_serial(&self, port: &str, baud: u32) -> String {
        "Serial opened".into()
    }
    fn set_timeout(&self, ms: u32) -> String {
        "Timeout set".into()
    }
}

struct ModbusProtocol;
impl ModbusProtocol {
    fn set_slave_id(&self, id: u8) -> String {
        "Slave ID set".into()
    }
    fn build_request(&self, reg: u16) -> String {
        format!("Request for register {}", reg)
    }
}

struct ModbusTransport;
impl ModbusTransport {
    fn send(&self, data: &str) -> String {
        format!("Sent: {}", data)
    }
    fn receive(&self) -> String {
        "Response received".into()
    }
}

// Facade
struct ModbusClient {
    connection: ModbusConnection,
    protocol: ModbusProtocol,
    transport: ModbusTransport,
}

impl ModbusClient {
    fn new() -> Self {
        Self {
            connection: ModbusConnection,
            protocol: ModbusProtocol,
            transport: ModbusTransport,
        }
    }
    
    fn read_register(&self, port: &str, slave_id: u8, register: u16) -> String {
        self.connection.open_serial(port, 9600);
        self.connection.set_timeout(1000);
        self.protocol.set_slave_id(slave_id);
        let request = self.protocol.build_request(register);
        self.transport.send(&request);
        self.transport.receive()
    }
}

// Usage
let client = ModbusClient::new();
let result = client.read_register("/dev/ttyUSB0", 1, 0);
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

### Code Examples

#### Python
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

#### Rust
```rust
use std::collections::HashMap;
use std::rc::Rc;

// Flyweight
struct SensorType {
    model: String,
    calibration: f32,
}

impl SensorType {
    fn read(&self, pin: &str) -> String {
        format!("{} on {}: {}°C", self.model, pin, self.calibration)
    }
}

// Flyweight factory
struct SensorFactory {
    types: HashMap<String, Rc<SensorType>>,
}

impl SensorFactory {
    fn new() -> Self {
        Self { types: HashMap::new() }
    }
    
    fn get_sensor_type(&mut self, model: &str, calibration: f32) -> Rc<SensorType> {
        let key = format!("{}-{}", model, calibration);
        self.types.entry(key).or_insert_with(|| {
            Rc::new(SensorType {
                model: model.into(),
                calibration,
            })
        }).clone()
    }
}

// Context
struct Sensor {
    sensor_type: Rc<SensorType>,
    pin: String,
}

// Usage
let mut factory = SensorFactory::new();
let dht22_type = factory.get_sensor_type("DHT22", 1.0);

let sensors = vec![
    Sensor { sensor_type: dht22_type.clone(), pin: "A0".into() },
    Sensor { sensor_type: dht22_type.clone(), pin: "A1".into() },
    Sensor { sensor_type: dht22_type.clone(), pin: "A2".into() },
];
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

### Code Examples

#### Python
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

#### Rust
```rust
// Subject trait
trait SensorReader {
    fn read(&self) -> String;
}

// Real subject
struct RemoteSensor {
    address: String,
}

impl RemoteSensor {
    fn new(address: &str) -> Self {
        println!("Connecting to sensor at {}...", address);
        Self { address: address.into() }
    }
}

impl SensorReader for RemoteSensor {
    fn read(&self) -> String {
        format!("Data from {}: 25°C", self.address)
    }
}

// Proxy
struct SensorProxy {
    address: String,
    sensor: Option<RemoteSensor>,
}

impl SensorProxy {
    fn new(address: &str) -> Self {
        Self {
            address: address.into(),
            sensor: None,
        }
    }
}

impl SensorReader for SensorProxy {
    fn read(&self) -> String {
        // Note: This is simplified. In real Rust, you'd use RefCell or Mutex
        println!("Access logged");
        format!("Proxy reading from {}", self.address)
    }
}

// Usage
let proxy = SensorProxy::new("192.168.1.10");
println!("{}", proxy.read());
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

# Behavioral Design Patterns - Quick Notes

## Chain of Responsibility
**Problem:** Pass request through handler chain until one handles it
> Like tech support—Level 1 → Level 2 → Level 3, each decides to handle or escalate

**Solution:** Link handlers together, each can process or pass to next
> Each handler has reference to next handler. If can't handle, forwards to next. Decouples sender from receiver—sender doesn't know who will handle it.

```python
class Handler:
    def __init__(self):
        self.next = None
    
    def set_next(self, handler):
        self.next = handler
        return handler
    
    def handle(self, request):
        if self.next:
            return self.next.handle(request)

class ValidationHandler(Handler):
    def handle(self, data):
        if not data:
            return "Invalid"
        print("Validated")
        return super().handle(data)

class FilterHandler(Handler):
    def handle(self, data):
        filtered = data.strip()
        print("Filtered")
        return super().handle(filtered)

# Usage
validator = ValidationHandler()
filter_h = FilterHandler()
validator.set_next(filter_h)
validator.handle("  data  ")
```

**Usage:**
- **Request pipelines**: HTTP middleware where each layer processes (auth → logging → routing)
- **Event handling**: GUI events bubble up until a handler catches it
- **Middleware chains**: Express.js style request processing

**IoT:**
- **Sensor validation**: Raw data → Range check → Calibration → Smoothing filter
- **Packet processing**: Receive → CRC check → Parse → Route → Execute
- **Error cascades**: Try serial → Try WiFi → Try cellular → Give up

---

## Command
**Problem:** Encapsulate requests as objects for queuing, logging, or undo
> Like restaurant orders—order slip is command object, can be queued, logged, or cancelled

**Solution:** Wrap requests in command objects with execute() method
> Separates "what to do" from "when/how to do it". Command stores receiver and action. Invoker just calls execute() without knowing details.

```python
class Command:
    def execute(self): pass

class Sensor:
    def start(self): return "Started"
    def stop(self): return "Stopped"

class StartCommand(Command):
    def __init__(self, sensor):
        self.sensor = sensor
    
    def execute(self):
        return self.sensor.start()

class StopCommand(Command):
    def __init__(self, sensor):
        self.sensor = sensor
    
    def execute(self):
        return self.sensor.stop()

# Invoker
class RemoteControl:
    def __init__(self):
        self.commands = []
    
    def add(self, cmd):
        self.commands.append(cmd)
    
    def execute_all(self):
        for cmd in self.commands:
            cmd.execute()

# Usage
sensor = Sensor()
remote = RemoteControl()
remote.add(StartCommand(sensor))
remote.add(StopCommand(sensor))
remote.execute_all()
```

**Usage:**
- **Undo/redo**: Each command knows how to undo itself (text editors, photo editors)
- **Transactions**: Group commands, execute atomically, rollback on failure
- **Job queues**: Commands stored in queue, workers execute later

**IoT:**
- **Device control**: Queue commands like "turn on LED", "read sensor", execute in order
- **Scheduled operations**: Store commands with timestamps, execute at specific times
- **Batch tasks**: Group multiple sensor reads into single command batch

---

## Iterator
**Problem:** Access collection elements sequentially without exposing structure
> Like TV remote—iterate channels without knowing how list is stored

**Solution:** Provide iterator that maintains position and traverses collection
> Iterator hides collection's internal structure (array, linked list, tree). Client uses uniform next() interface regardless of underlying storage.

```python
class SensorReadings:
    def __init__(self):
        self.readings = []
    
    def add(self, reading):
        self.readings.append(reading)
    
    def __iter__(self):
        return SensorIterator(self.readings)

class SensorIterator:
    def __init__(self, readings):
        self.readings = readings
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index < len(self.readings):
            result = self.readings[self.index]
            self.index += 1
            return result
        raise StopIteration

# Usage
readings = SensorReadings()
readings.add(25.0)
readings.add(26.5)
for temp in readings:
    print(temp)
```

**Usage:**
- **Collection traversal**: Iterate arrays, trees, graphs with same interface
- **Custom iteration**: Traverse in specific order (reverse, filtered, sorted)
- **Data structure abstraction**: Change internal structure without breaking client code

**IoT:**
- **Sensor buffers**: Iterate through circular buffer of recent readings
- **Device lists**: Traverse registered devices without exposing storage
- **Circular buffers**: Read oldest-to-newest in ring buffer

---

## Mediator
**Problem:** Reduce chaotic dependencies by centralizing communication
> Like air traffic control—all planes talk through tower, not each other

**Solution:** Objects communicate through mediator instead of directly
> Mediator encapsulates how objects interact. Objects only know mediator, not each other. Reduces coupling from N×N to N×1.

```python
class SensorMediator:
    def __init__(self):
        self.sensors = []
    
    def register(self, sensor):
        self.sensors.append(sensor)
        sensor.mediator = self
    
    def notify(self, sender, event):
        if event == "high_temp":
            for s in self.sensors:
                if s != sender:
                    s.receive(f"Alert from {sender.name}")

class Sensor:
    def __init__(self, name):
        self.name = name
        self.mediator = None
    
    def check(self, temp):
        if temp > 30:
            self.mediator.notify(self, "high_temp")
    
    def receive(self, msg):
        print(f"{self.name}: {msg}")

# Usage
mediator = SensorMediator()
temp1 = Sensor("Sensor1")
temp2 = Sensor("Sensor2")
mediator.register(temp1)
mediator.register(temp2)
temp1.check(35)  # Sensor2 gets notified
```

**Usage:**
- **GUI dialogs**: Buttons, text fields coordinate through dialog controller
- **Chat rooms**: Users send messages through room, room broadcasts
- **Component coordination**: Multiple UI components update based on others' changes

**IoT:**
- **Sensor coordination**: Temperature spike triggers fan, alerts display, logs event
- **Device orchestration**: Master device coordinates multiple slaves' behavior
- **Event distribution**: Central hub routes events to appropriate handlers

---

## Memento
**Problem:** Save and restore object state without breaking encapsulation
> Like game save points—captures exact state for later restoration

**Solution:** Memento stores state, Originator creates/restores, Caretaker manages
> Memento is opaque—only Originator can read it. Caretaker stores mementos without peeking inside. Preserves encapsulation.

```python
class SensorMemento:
    def __init__(self, state):
        self._state = state
    
    def get_state(self):
        return self._state

class Sensor:
    def __init__(self):
        self.readings = []
    
    def add(self, value):
        self.readings.append(value)
    
    def save(self):
        return SensorMemento(self.readings.copy())
    
    def restore(self, memento):
        self.readings = memento.get_state()

class History:
    def __init__(self):
        self.mementos = []
    
    def save(self, memento):
        self.mementos.append(memento)
    
    def undo(self):
        if self.mementos:
            return self.mementos.pop()

# Usage
sensor = Sensor()
history = History()

sensor.add(25.0)
history.save(sensor.save())  # Checkpoint

sensor.add(26.0)
sensor.add(27.0)

print(sensor.readings)  # [25.0, 26.0, 27.0]
sensor.restore(history.undo())
print(sensor.readings)  # [25.0]
```

**Usage:**
- **Undo/redo**: Save states before each operation, restore on undo
- **Transaction rollback**: Save state before transaction, restore on failure
- **Snapshot management**: Periodic snapshots for recovery

**IoT:**
- **Config snapshots**: Save working config, try new settings, rollback if issues
- **Sensor checkpoints**: Save sensor state, restore if calibration fails
- **System recovery**: Periodic state saves for crash recovery

---

## Observer
**Problem:** Notify multiple objects when another object changes
> Like YouTube subscriptions—when video uploads, all subscribers notified

**Solution:** Subject maintains observers list, notifies all on state change
> Defines one-to-many dependency. Observers register with subject. When subject changes, it calls notify() on all observers automatically.

```python
class Subject:
    def __init__(self):
        self._observers = []
        self._state = None
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def set_state(self, state):
        self._state = state
        self.notify()
    
    def notify(self):
        for obs in self._observers:
            obs.update(self._state)

class Display:
    def __init__(self, name):
        self.name = name
    
    def update(self, state):
        print(f"{self.name}: {state}")

# Usage
sensor = Subject()
display1 = Display("LCD")
display2 = Display("Log")

sensor.attach(display1)
sensor.attach(display2)

sensor.set_state("Temp: 25°C")
# Both displays update automatically
```

**Usage:**
- **Event systems**: DOM events, button clicks notify registered listeners
- **Model-View**: Model changes, all views update automatically (MVC pattern)
- **Pub/sub**: Publishers broadcast, subscribers receive without direct coupling

**IoT:**
- **Sensor broadcasting**: Temperature sensor updates display, logger, cloud uploader
- **Device monitoring**: Monitor device state, notify dashboard, alerting system
- **Alert systems**: Critical event triggers multiple notification channels

---

## State
**Problem:** Object behavior changes with internal state
> Like TCP connection—behaves differently when Listening, Established, or Closed

**Solution:** Encapsulate state-specific behavior in state objects
> Each state is a class. Context delegates to current state object. Changing state = changing the state object. Eliminates huge if/else blocks.

```python
class State:
    def handle(self): pass

class IdleState(State):
    def handle(self):
        return "Sensor idle"

class ReadingState(State):
    def handle(self):
        return "Sensor reading"

class ErrorState(State):
    def handle(self):
        return "Sensor error"

class Sensor:
    def __init__(self):
        self.state = IdleState()
    
    def set_state(self, state):
        self.state = state
    
    def request(self):
        return self.state.handle()

# Usage
sensor = Sensor()
print(sensor.request())  # Sensor idle

sensor.set_state(ReadingState())
print(sensor.request())  # Sensor reading

sensor.set_state(ErrorState())
print(sensor.request())  # Sensor error
```

**Usage:**
- **Workflow engines**: Document states (Draft → Review → Approved → Published)
- **Connection management**: Network states (Connecting → Connected → Disconnected)
- **UI state machines**: App states (Loading → Ready → Processing → Error)

**IoT:**
- **Device lifecycle**: Boot → Initializing → Ready → Operating → Sleeping → Shutdown
- **Protocol states**: Modbus (Idle → Sending → Waiting Response → Processing → Error)
- **Sensor modes**: Continuous → OnDemand → PowerSave → Calibration

---

## Strategy
**Problem:** Define interchangeable algorithm families
> Like navigation—choose fastest, shortest, or avoid highways

**Solution:** Encapsulate algorithms, make them interchangeable
> Algorithm interface defines contract. Concrete strategies implement variations. Context uses strategy interface, switches at runtime.

```python
class CompressionStrategy:
    def compress(self, data): pass

class ZipCompression(CompressionStrategy):
    def compress(self, data):
        return f"ZIP: {data}"

class GzipCompression(CompressionStrategy):
    def compress(self, data):
        return f"GZIP: {data}"

class DataTransmitter:
    def __init__(self, strategy):
        self.strategy = strategy
    
    def send(self, data):
        compressed = self.strategy.compress(data)
        return f"Sending {compressed}"

# Usage
tx = DataTransmitter(ZipCompression())
print(tx.send("sensor data"))

tx.strategy = GzipCompression()  # Switch algorithm
print(tx.send("sensor data"))
```

**Usage:**
- **Sorting algorithms**: Choose QuickSort, MergeSort, HeapSort based on data
- **Payment methods**: Credit card, PayPal, crypto—same checkout, different processing
- **Validation rules**: Different validation strategies per field type

**IoT:**
- **Compression methods**: ZIP for text data, JPEG for images, choose based on type
- **Encryption algorithms**: AES, RSA—choose based on security requirements
- **Calibration strategies**: Linear, polynomial—choose based on sensor type

---

## Template Method
**Problem:** Define algorithm skeleton, let subclasses override steps
> Like making coffee—process is same (boil, brew, pour, add), but brewing differs

**Solution:** Base class defines structure, subclasses override hook methods
> Template method calls abstract methods (hooks). Subclasses implement hooks. Algorithm structure stays in base class—prevents duplication.

```python
class DataProcessor:
    def process(self):  # Template method
        data = self.read_data()
        data = self.transform(data)
        self.send(data)
    
    def read_data(self): pass  # Hook
    def transform(self, data): pass  # Hook
    
    def send(self, data):  # Concrete
        print(f"Sending: {data}")

class SensorProcessor(DataProcessor):
    def read_data(self):
        return "sensor reading"
    
    def transform(self, data):
        return data.upper()

class FileProcessor(DataProcessor):
    def read_data(self):
        return "file content"
    
    def transform(self, data):
        return data.lower()

# Usage
proc = SensorProcessor()
proc.process()  # Read, transform, send

proc = FileProcessor()
proc.process()  # Different read/transform, same flow
```

**Usage:**
- **Framework workflows**: Django views (setup → process → render → cleanup)
- **Data pipelines**: ETL (extract → transform → load), transform differs
- **Test fixtures**: setUp → test → tearDown, test body varies

**IoT:**
- **Sensor protocols**: Initialize → Read → Validate → Store, read step varies
- **Transmission flows**: Connect → Authenticate → Send → Disconnect, auth differs
- **Initialization**: Power on → Configure → Calibrate → Ready, configure varies

---

## Visitor
**Problem:** Add operations to class hierarchy without modifying classes
> Like tax calculation—different items taxed differently, without changing item classes

**Solution:** Represent operations as visitor objects, elements accept visitors
> Double dispatch: element.accept(visitor) calls visitor.visit(element). New operation = new visitor class. Elements unchanged.

```python
class Sensor:
    def accept(self, visitor): pass

class TempSensor(Sensor):
    def __init__(self, value):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_temp(self)

class HumiditySensor(Sensor):
    def __init__(self, value):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_humidity(self)

class Visitor:
    def visit_temp(self, sensor): pass
    def visit_humidity(self, sensor): pass

class DisplayVisitor(Visitor):
    def visit_temp(self, s):
        return f"Temp: {s.value}°C"
    
    def visit_humidity(self, s):
        return f"Humidity: {s.value}%"

class ExportVisitor(Visitor):
    def visit_temp(self, s):
        return f"temp,{s.value}"
    
    def visit_humidity(self, s):
        return f"humidity,{s.value}"

# Usage
sensors = [TempSensor(25), HumiditySensor(60)]

display = DisplayVisitor()
for s in sensors:
    print(s.accept(display))

export = ExportVisitor()
for s in sensors:
    print(s.accept(export))
```

**Usage:**
- **AST traversal**: Compiler visits syntax tree nodes, performs operations
- **Report generation**: Visit different data types, format each for report
- **Serialization**: Visit objects, serialize each to JSON/XML/Binary

**IoT:**
- **Multi-format export**: Visit sensors, export as JSON, CSV, Protobuf
- **Data aggregation**: Visit sensor network, calculate stats per type
- **Device inventory**: Visit devices, collect info for different reports
