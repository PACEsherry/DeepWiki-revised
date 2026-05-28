pub fn greet(name: &str) -> String {
    format!("Hello {}", name)
}

pub struct Greeter<'a> {
    pub name: &'a str,
}

impl<'a> Greeter<'a> {
    pub fn greet(&self) -> String {
        format!("Hello {}", self.name)
    }
} 