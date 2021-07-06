import math

def to_cents(amount):
  """
  to_cents converts an integer amount into cents

  :param amount: The integer amount to be converted.
  """
  return math.ceil(float(amount) * 100)