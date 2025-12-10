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

## Quick Comparison

| Pattern | Purpose | Key Benefit |
|---------|---------|-------------|
| **Adapter** | Make incompatible interfaces work | Integration with existing code |
| **Bridge** | Decouple abstraction from implementation | Independent variation |
| **Composite** | Treat objects and compositions uniformly | Hierarchical structures |
| **Decorator** | Add responsibilities dynamically | Flexible feature addition |
| **Facade** | Simplify complex subsystem | Easier API |
| **Flyweight** | Share common data efficiently | Memory optimization |
| **Proxy** | Control access to objects | Lazy loading, access control |
