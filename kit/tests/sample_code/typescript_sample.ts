export function greet(name: string): string {
  return `Hello ${name}`;
}

export class Greeter {
  constructor(private name: string) {}

  greet(): string {
    return `Hello ${this.name}`;
  }
} 