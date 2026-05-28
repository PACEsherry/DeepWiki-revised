export function greet(name) {
  return `Hello ${name}`;
}

export class Greeter {
  constructor(name) {
    this.name = name;
  }

  greet() {
    return `Hello ${this.name}`;
  }
} 