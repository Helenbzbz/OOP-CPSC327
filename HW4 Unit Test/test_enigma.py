import unittest
from components import Rotor, ROTOR_WIRINGS, ROTOR_NOTCHES, ALPHABET

class TestRotor(unittest.TestCase):

    def test_valid_initialization(self):
        rotor = Rotor('I', 'A')
        self.assertEqual(rotor.rotor_num, 'I')
        self.assertEqual(rotor.window, 'A')
        self.assertEqual(rotor.offset, 0)  # A is the 0th letter in the alphabet.
        self.assertEqual(rotor.wiring, ROTOR_WIRINGS['I'])
        self.assertEqual(rotor.notch, ROTOR_NOTCHES['I'])

    def test_repr(self):
        rotor = Rotor('II', 'B')
        expected_repr = f"Wiring:\n{ROTOR_WIRINGS['II']}\nWindow: B"
        self.assertEqual(repr(rotor), expected_repr)

    def test_invalid_rotor_number(self):
        with self.assertRaises(ValueError):
            Rotor('VI', 'A')

    def test_step(self):
        rotor = Rotor('I', 'Q')  # Q is the notch for rotor I.
        rotor.step()
        self.assertEqual(rotor.window, 'R')
        self.assertEqual(rotor.offset, 17)

    def test_step_with_next_rotor(self):
        next_rotor = Rotor('II', 'A')
        rotor = Rotor('I', 'Q', next_rotor=next_rotor)  # Set up next rotor.
        rotor.step()
        self.assertEqual(rotor.window, 'R')
        self.assertEqual(next_rotor.window, 'B')  # Next rotor should step as well.

    def test_double_step(self):
        next_rotor = Rotor('III', 'V')  # V is the notch for rotor III.
        mid_rotor = Rotor('II', 'E', next_rotor=next_rotor)  # E is the notch for rotor II.
        rotor = Rotor('I', 'Q', next_rotor=mid_rotor)  # Setup chain.
        rotor.step()
        self.assertEqual(mid_rotor.window, 'F')  # Mid rotor should double step.
        self.assertEqual(next_rotor.window, 'W')  # Next rotor should step due to double step.

    def test_encode_letter_forward(self):
        rotor = Rotor('I', 'A')  # Initial setting at A.
        output = rotor.encode_letter('A', forward=True, return_letter=True)
        self.assertEqual(output, 'E')  # Based on 'I' wiring forward.

    def test_encode_letter_backward(self):
        rotor = Rotor('I', 'A')
        index = ALPHABET.index('E')  # Find index of 'E', the output of 'A' through rotor 'I'.
        output = rotor.encode_letter(index, forward=False, return_letter=True)
        self.assertEqual(output, 'A')  # Reverse transformation should yield 'A'.

    def test_encode_letter_chain_forward(self):
        rotor1 = Rotor('I', 'A')
        rotor2 = Rotor('II', 'A', prev_rotor=rotor1)
        rotor1.next_rotor = rotor2
        output = rotor1.encode_letter('A', forward=True, return_letter=True)
        # Expected result is specific to wiring configurations.
        self.assertEqual(output, 'J')  # Expected output based on wiring and initial settings.

    def test_encode_letter_chain_backward(self):
        rotor1 = Rotor('I', 'A')
        rotor2 = Rotor('II', 'A', prev_rotor=rotor1)
        rotor1.next_rotor = rotor2
        # Reverse transformation should yield original input.
        index = ALPHABET.index('J')  # Result of forward transformation in the previous test.
        output = rotor2.encode_letter(index, forward=False, return_letter=True)
        self.assertEqual(output, 'A')

    def test_change_setting(self):
        rotor = Rotor('I', 'A')
        rotor.change_setting('M')
        self.assertEqual

if __name__ == '__main__':
    unittest.main()






