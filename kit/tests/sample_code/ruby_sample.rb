def greet(name)
  "Hello #{name}"
end

class Greeter
  def initialize(name)
    @name = name
  end

  def greet
    "Hello #{@name}"
  end
end 