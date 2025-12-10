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
**General:**
- Application configuration ensuring one settings object across the system
- Logging where all parts write to the same log
- Cache management with a single shared storage

**IoT:**
- Modbus Master per process since only one can control the bus at a time
- Shared MQTT client pooling connections to avoid overhead
- Hardware bus controllers where I2C or SPI needs exclusive access

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
- Payment processing where type depends on user choice at checkout
- Document export when format is selected by user
- Notification delivery based on user preferences

**IoT:**
- Sensor drivers where hardware type is determined by configuration file
- Communication protocols selected at runtime based on network availability
- Data formatters chosen by the receiving system's requirements

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
- UI themes where all components must match visual style
- Cross-platform apps where widgets adapt to the operating system
- Database access where connection, commands, and transactions belong to the same vendor

**IoT:**
- Modbus RTU vs TCP families ensuring client and server use matching protocol
- Cloud service sets where storage and messaging come from one provider
- Sensor ecosystems where reader, calibrator, and logger work with the same data format

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
- Complex configuration objects avoiding constructors with many parameters
- Query building where clauses are added conditionally
- Test data creation with only relevant fields set

**IoT:**
- Modbus connection setup defining slave ID, baud rate, timeout, and retry logic
- Sensor configuration setting pin, threshold, sampling rate, and calibration values
- MQTT client builder specifying broker, credentials, QoS, and keepalive settings

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
- Game character creation by copying templates and customizing attributes
- Document generation from templates with specific data filled in
- Test fixtures where base objects are cloned for each test

**IoT:**
- Multiple sensor configurations starting from one base setup
- Modbus register maps copied and modified for different slave devices
- Network packet templates cloned for batch transmission with varying payloads

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
