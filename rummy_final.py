#!/usr/bin/python3

import random

"""
Author: Vinitha Gadiraju
This program is for the card game Rummy.
MIT License

Rules:
- Rummy is a card game based on making sets.
- From a stash(or hand) of 13 cards, 4 sets must be created (3 sets of 3, 1 set of 4).
- A valid set can either be a run or a book.
- One set must be a run WITHOUT using a joker.
- A run is a sequence of numbers in a row, all with the same suit.
	For example: 4 of Hearts, 5 of Hearts, and 6 of Hearts
- A book is a set in which the cards all have the same rank but must have different suits.
	For example: 3 of Diamonds, 3 of Spades, 5 of Clubs
- A joker is a card randomly picked from the deck at the start of the game.
- All jokers are considered free cards and can be used to complete sets.
- During each player's turn, the player may take a card from the pile or a card from the deck to help create sets.
  Immediately after, the player must drop a card into the pile so as not go over the 14 card limit.
- When a player has created all the sets, select the close game option and drop the excess card into the pile.
- Card with Rank 10 is represented as Rank T
"""
#constants to be used for the cards used in the game
SYMBOLS = ['♠', '♢', '♡', '♣']
SUIT = ['Hearts', 'Clubs', 'Spades', 'Diamonds']
RANK = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
RANK_VALUE = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13}
SUIT_SYMBOLS = {'Hearts': '♡', 'Clubs': '♣', 'Spades': '♠', 'Diamonds': '♢'}

class Card:
	""" Card Class - Models a single Playing Card """

	def __init__(self, rank, suit):
		""" Class Constructor
		Args:
			rank: A valid RANK value - a single char
			suit: A valid SUIT value - a string
		Returns:
			No return value
		"""
		self.rank = rank
		self.suit = suit
		self.isjoker = False

	def __str__(self):
		""" Helper for builtin __str__ function
		Args:
			no args.
		Returns:
			string representation of the Card.  For Joker a "-J" is added.
			for example for 4 of Hearts, returns 4♡ 
				and if it is a Joker returns 4♡-J
		"""
		if self.isjoker:
			return (self.rank + SUIT_SYMBOLS[self.suit] + '-J')
		return (self.rank + SUIT_SYMBOLS[self.suit])

	def is_joker(self):
		"""Status check to see if this Card is a Joker
		Args:
			no arguments
		Returns:
			True or False
		"""
		return self.isjoker

class Deck:
	""" Deck Class - Models the card Deck """

	def __init__(self, packs):
		""" Class Constructor
		Args:
			packs: Number of packs used to create the Deck - int value
		Returns:
			No return value
		"""
		self.packs = packs
		self.cards = []
		self.joker = None

		# Create all cards in the Deck
		for i in range(packs):
			for s in SUIT:
				for r in RANK:
					self.cards.append(Card(r, s))

	def shuffle(self):
		""" Shuffle the Deck, so that cards are ordered in a random order
		Args:
			No args
		Returns:
			No return value
		"""
		random.shuffle(self.cards)

	def draw_card(self):
		""" Draw a card from the top of the Deck
		Args:
			No args
		Returns:
			a Card Object
		"""
		a = self.cards[0]
		self.cards.pop(0)
		return a

	def set_joker(self):
		""" Set the Joker Cards in the Deck
		A Card is selected at random from the deck as Joker.
		All cards with the same Rank as the Joker are also set to Jokers.
		Args:
			No args
		Returns:
			No returns
		"""
		self.joker = random.choice(self.cards)

		# remove the Joker from Deck and display on Table for Players to see
		self.cards.remove(self.joker)

		for card in self.cards:
			if self.joker.rank == card.rank:
				card.isjoker = True

class Player:
	""" Player Class - Models Players Hand and play actions """

	def __init__(self, name, deck, game):
		""" Class Constructor
		Args:
			name: Name of the Player - string
			deck: Reference to the Deck Object that is part of the Game
			game: Reference to the Game object that is being played now
		Returns:
			No return value
		"""
		self.stash = []	# Stash represents the hand of the Player.
		self.name = name
		self.deck = deck
		self.game = game

	def deal_card(self, card):
		""" Deal a Card to the Player
		Args:
			card:  The Card object provided to Player as part of the deal
		Returns:
			No returns
		"""
		try:
			self.stash.append(card)
			if len(self.stash) > 14:
				raise ValueError('ERROR: Player cannot have more than 14 cards during turn')
		except ValueError as err:
			print(err.args)

	def drop_card(self, card):
		""" Drop Card operation by the Player
		Args:
			card: The player input representation of the Card object 
				that needs to be dropped.  For example: AC for Ace of Clubs
		Returns:
			No returns
		"""
		# Get the actual card object from string representation
		card = get_object(self.stash, card)

		# Cannot drop a card if it is already not in stash
		if card not in self.stash:
			return False

		self.stash.remove(card)

		# Player dropped card goes to Pile
		self.game.add_pile(card)

		return True


	def close_game(self):
		""" Close Game operation by the Player
		Args:
			No args
		Returns:
			Success or Failure as True/False
		"""
		# Divide the stash into 4 sets, 3 sets of 3 cards and 1 set of 4 cards
		set_array = [self.stash[:3], self.stash[3:6], self.stash[6:9], self.stash[9:]]

		# Need to count the number of sets that are runs without a joker.
		# 	There must be at least one run with out a joker
		count = 0
		for s in set_array:
			if is_valid_run(s):
				count += 1
		if count == 0:
			return False

		# Check if each of the sets is either a run or a book
		for s in set_array:
			if is_valid_run(s) == False and is_valid_book(s) == False and is_valid_run_joker(s) == False:
				return False

		return True

	def play(self):
		""" Play a single turn by the Player
		Args:
			No args
		Returns:
			Success or Failure as True/False
		"""
		# Stay in a loop until the Player drops a card or closes the game.
		while True:
			# clear screen to remove the output of previous Player action
			print(chr(27)+"[2J")
			print("***",self.name,"your cards are:")
			print(print_cards(self.stash))
			self.game.display_pile()

			# Get Player Action
			action = input("*** " + self.name + ", What would you like to do? ***, \n(M)ove Cards, (P)ick from pile, (T)ake from deck, (D)rop, (S)ort, (C)lose Game, (R)ules: ")

			# Move or Rearrange Cards in the stash
			if action == 'M' or action == 'm':
				# Get the Card that needs to moved.
				move_what = input("Enter which card you want to move. \nEnter Rank followed by first letter of Suit. i.e. 4H (4 of Hearts): ")
				move_what.strip()
				if get_object(self.stash, move_what.upper()) not in self.stash:
					input("ERROR: That card is not in your stash.  Enter to continue")
					continue

				# Get the Card where the move_what needs to moved.
				move_where = input("Enter where you want move card to (which card the moving card will go before) Enter Space to move to end \nEnter Rank followed by first letter of Suit. i.e. 4H (4 of Hearts):" )
				move_where.strip()
				if move_where != "" and get_object(self.stash, move_where.upper()) not in self.stash:
					input("ERROR: This is an invalid location.  Enter to continue")
					continue

				# Perform the Move Operation
				move_what = get_object(self.stash, move_what.upper())
				if move_where != "":
					move_where = get_object(self.stash, move_where.upper())
					location = self.stash.index(move_where)
					if location > self.stash.index(move_what):
						location = location - 1
					self.stash.remove(move_what)
					self.stash.insert(location, move_what)
				else:
					# If the move_where was not specified by the User then,
					#		the card to the end of the stash
					self.stash.remove(move_what)
					self.stash.append(move_what)

			# Pick card from Pile
			if action == 'P' or action == 'p':
				if len(self.stash) < 14:
					c = self.game.draw_pile()
					self.stash.append(c)
				else:
					input("ERROR: You have " + str(len(self.stash)) + " cards. Cannot pick anymore. Enter to continue")

			# Take Card from Deck
			if action == 'T' or action == 't':
				if len(self.stash) < 14:
					c = self.deck.draw_card()
					self.stash.append(c)
				else:
					input("ERROR: You have " + str(len(self.stash)) + " cards. Cannot take anymore. Enter to continue")

			# Drop card to Pile
			if action == 'D' or action == 'd':
				if len(self.stash) == 14:
					drop = input("Which card would you like to drop? \nEnter Rank followed by first letter of Suit. i.e. 4H (4 of Hearts): ")
					drop = drop.strip()
					drop = drop.upper()
					if self.drop_card(drop):
						# return False because Drop Card does not end the game
						return False
					else:
						input("ERROR: Not a valid card, Enter to continue")
				else:
					input("ERROR: Cannot drop a card. Player must have 13 cards total. Enter to continue")

			# Sort cards in the stash
			if action == 'S' or action == 's':
				sort_sequence(self.stash)

			# Close the Game
			if action == 'C' or action == 'c':

				if len(self.stash) == 14:
					drop = input("Which card would you like to drop? \nEnter Rank followed by first letter of Suit. i.e. 4H (4 of Hearts): ")
					drop = drop.strip()
					drop = drop.upper()
					if self.drop_card(drop):
						if self.close_game():
							print(print_cards(self.stash))
							# Return True because Close ends the Game.
							return True
						else:
							input("ERROR: The game is not over. Enter to Continue playing.")
							# if this Close was false alarm then discarded Card will
							#		have to be put back into the stash for the Player to continue.
							self.stash.append(self.game.draw_pile())
					else:
						input("ERROR: Not a valid card, Enter to continue")
				else:
					input("ERROR: You do not have enough cards to close the game. Enter to Continue playing.")

			# Show Rules of the game
			if action == 'R' or action == 'r':
				print("------------------ Rules --------------------",
					"\n- Rummy is a card game based on making sets.",
					"\n- From a stash of 13 cards, 4 sets must be created (3 sets of 3, 1 set of 4).",
					"\n- The set of 4 must always be at the end"
					"\n- A valid set can either be a run or a book.",
					"\n- One set must be a run WITHOUT using a joker."
					"\n- A run is a sequence of numbers in a row, all with the same suit. ",
					"\n \tFor example: 4 of Hearts, 5 of Hearts, and 6 of Hearts",
					"\n- A book of cards must have the same rank but may have different suits.",
					"\n \tFor example: 3 of Diamonds, 3 of Spades, 3 of Clubs",
					"\n- Jokers are randomly picked from the deck at the start of the game.",
					"\n- Joker is denoted by '-J' and can be used to complete sets.",
					"\n- During each turn, the player may take a card from the pile or from the deck.",
					"Immediately after, the player must drop any one card into the pile so as not go over the 13 card limit.",
					"\n- When a player has created all the sets, select Close Game option and drop the excess card into the pile.",
					"\n- Card with Rank 10 is represented as Rank T"
					"\n--------------------------------------------" )
				input("Enter to continue ....")

class Game:
	""" Game Class - Models a single Game """ 

	def __init__(self, hands, deck):
		""" Class Constructor 
			Args:
				hands:  represents the number of players in the game - an int
				deck: Reference to Deck Object
			Returns:
				No returns
		"""
		self.pile = []
		self.players = []

		for i in range(hands):
			name = input("Enter name of Player " + str(i) + ": ")
			self.players.append(Player(name, deck, self))

	def display_pile(self):
		""" Displays the top of the Pile.
			Args:
				No args.
			Returns:
				No returns
		"""
		if len(self.pile) == 0:
			print("Empty pile.")
		else:
			print("The card at the top of the pile is: ", self.pile[0])

	def add_pile(self, card):
		""" Adds card to the top of the Pile.
			Args:
				card:  The card that is added to top of the Pile
			Returns:
				No returns
		"""
		self.pile.insert(0, card)

	def draw_pile(self):
		""" Draw the top card from the Pile.
			Args:
				No args
			Returns:
				Returns the top Card from the Pile - Card Object
		"""
		if len(self.pile) != 0:
			return self.pile.pop(0)
		else:
			return None

	def play(self):
		""" Play the close_game.
			Args:
				No args
			Returns:
				No returns
		"""
		i = 0
		while self.players[i].play() == False:
			print(chr(27)+"[2J")
			i += 1
			if i == len(self.players):
				i = 0
			print("***", self.players[i].name, "to play now.")
			input(self.players[i].name + " hit enter to continue...")

		# Game Over
		print("*** GAME OVER ***")
		print("*** ", self.players[i].name, " Won the game ***")


#global nonclass functions
def is_valid_book(sequence):
	""" Check if the sequence is a valid book.
		Args:
			sequence: an array of Card objects.  Array will have either 3 ro 4 cards
		Returns:
			Success or Failure as True/False
	"""
	# Move all Jokers to the end of the sequence
	while(sequence[0].isjoker == True):
		sequence.append(sequence.pop(0))

	# Compare Cards in sequnce with 0th Card, except for Jokers.
	for card in sequence:
		if card.is_joker() == True:
			continue
		if card.rank != sequence[0].rank:
			return False

	return True

def is_valid_run(sequence):
	""" Check if the sequence is a valid run.
		Args:
			sequence: an array of Card objects.  Array will have either 3 ro 4 cards
		Returns:
			Success or Failure as True/False
	"""
	RANK_VALUE["A"] = 1 #resetting value of A (may have been set to 14 in previous run)

	# Order the Cards in the sequence
	sort_sequence(sequence)

	# Check to see if all Cards in the sequence have the same SUIT
	for card in sequence:
		if card.suit != sequence[0].suit:
			return False

	# this is to sort a sequence that has K, Q and A
	if sequence[0].rank == "A":
		if sequence[1].rank == "Q" or sequence[1].rank == "J" or sequence[1].rank == "K":
			RANK_VALUE[sequence[0].rank] = 14
			sort_sequence(sequence)

	# Rank Comparison
	for i in range(1,len(sequence)):
		if RANK_VALUE[sequence[i].rank] != RANK_VALUE[(sequence[i-1].rank)]+1:
			return False

	return True

def is_valid_run_joker(sequence):
	""" Check if the sequence with Jokers is a valid run.
		Args:
			sequence: an array of Card objects.  Array will have either 3 ro 4 cards
		Returns:
			Success or Failure as True/False
	"""

	RANK_VALUE["A"] = 1 #resetting value of A (may have been set to 14 in previous run)

	# Order the Cards in the sequence
	sort_sequence(sequence)

	# Push all Jokers to the end and count the number of Jokers
	push_joker_toend(sequence)
	joker_count = 0
	for card in sequence:
		if card.is_joker() == True:
			joker_count += 1

	# Make sure the Suit Match except for Jokers.
	for card in sequence:
		if card.is_joker() == True:
			continue
		if card.suit != sequence[0].suit:
			return False

	# This is to cover for K, Q and A run with Jokers
	if sequence[0].rank == "A":
		if sequence[1].rank == "Q" or sequence[1].rank == "J" or sequence[1].rank == "K":
			RANK_VALUE[sequence[0].rank] = 14
			sort_sequence(sequence)
			push_joker_toend(sequence)

	rank_inc = 1
	for i in range(1,len(sequence)):
		if sequence[i].is_joker() == True:
			continue
		# Compare RANK values with accomodating for Jokers.
		while (RANK_VALUE[sequence[i].rank] != RANK_VALUE[(sequence[i-1].rank)]+rank_inc):
			# Use Joker Count for missing Cards in the run
			if joker_count > 0:
				rank_inc += 1
				joker_count -= 1
				continue
			else:
				# if No more Jokers left, then revert to regular comparison
				if RANK_VALUE[sequence[i].rank] != RANK_VALUE[(sequence[i-1].rank)]+1:
					return False
				else:
					break
	return True

def push_joker_toend(sequence):
	""" Push the Joker to the end of the sequence.
		Args:
			sequence: sequence of Card Objects.
		Returns:
			no return
	"""
	sort_sequence(sequence)
	joker_list = []
	for card in sequence:
		if card.is_joker()== True:
			sequence.remove(card)
			joker_list.append(card)
	sequence += joker_list
	return sequence

def get_object(arr, str_card):
	""" Get Card Object using its User Input string representation
	Args:
		arr: array of Card objects
		str_card: Card descriptor as described by user input, that is a 2 character
			string of Rank and Suit of the Card.  For example, KH for King of Hearts.
	Returns:
		object pointer corresponding to string, from the arr
	"""
	# Make sure the str_card has only a RANK letter and SUIT letter
	#		for example KH for King of Hearts.
	if len(str_card) != 2:
		return None

	for item in arr:
		if item.rank == str_card[0] and item.suit[0] == str_card[1]:
			return item

	return None

def print_cards(arr):
	""" Print Cards in a single line
		Args:
			arr: array of Card Objects
		Returns:
			a displayable string representation of the Cards in the arr
	"""
	s = ""
	for card in arr:
		s = s + " " + str(card)
	return s

def sort_sequence(sequence):
	""" Sort the Cards in the sequence in the incresing order of RANK values
		Args:
			sequence: array of Card objects
		Returns:
			sorted sequence.
	"""
	is_sort_complete = False

	while is_sort_complete == False:
		is_sort_complete = True
		for i in range(0, len(sequence)-1):
			if RANK_VALUE[sequence[i].rank] > RANK_VALUE[sequence[i+1].rank]:
				a = sequence[i+1]
				sequence[i+1] = sequence[i]
				sequence[i] = a
				is_sort_complete = False
	return sequence

def unit_tests():
	""" Unit Tests for Checking various aspects of the program
		Args:
			No args
		Returns:
			no returns.
	"""

	print("Running Unit Tests")
	"""
	#test 1 - check players deal card exception handling
	player = Player("Vinitha", None, None)
	player.deal_card(Card("4", "Hearts"))
	player.deal_card(Card("5", "Hearts"))
	player.deal_card(Card("6", "Hearts"))
	player.deal_card(Card("5", "Spades"))
	player.deal_card(Card("5", "Diamonds"))
	player.deal_card(Card("5", "Clubs"))
	player.deal_card(Card("J", "Clubs"))
	player.deal_card(Card("7", "Diamonds"))
	player.deal_card(Card("8", "Spades"))
	player.deal_card(Card("3", "Diamonds"))
	player.deal_card(Card("A", "Spades"))
	player.deal_card(Card("2", "Clubs"))
	player.deal_card(Card("A", "Hearts"))
	player.deal_card(Card("9", "Spades"))
	player.deal_card(Card("9", "Hearts"))

	"""

	#test 2 - check close game
	player1 = Player("Vinitha", None, None)
	player1.deal_card(Card("4", "Hearts"))
	player1.deal_card(Card("5", "Hearts"))
	player1.deal_card(Card("6", "Hearts"))
	player1.deal_card(Card("5", "Spades"))
	player1.deal_card(Card("5", "Diamonds"))
	player1.deal_card(Card("5", "Clubs"))
	player1.deal_card(Card("J", "Clubs"))
	player1.deal_card(Card("J", "Hearts"))
	player1.deal_card(Card("J", "Spades"))
	player1.deal_card(Card("5", "Diamonds"))
	player1.deal_card(Card("2", "Diamonds"))
	player1.deal_card(Card("3", "Diamonds"))
	player1.deal_card(Card("4", "Diamonds"))
	assert (player1.close_game() == True)


	player2 = Player("Varun", None, None)
	player2.deal_card(Card("2", "Diamonds"))
	player2.deal_card(Card("3", "Hearts"))
	player2.deal_card(Card("4", "Hearts"))
	player2.deal_card(Card("4", "Clubs"))
	player2.deal_card(Card("4", "Diamonds"))
	player2.deal_card(Card("8", "Clubs"))
	player2.deal_card(Card("9", "Clubs"))
	player2.deal_card(Card("T", "Clubs"))
	player2.deal_card(Card("J", "Clubs"))
	player2.deal_card(Card("K", "Spades"))
	player2.deal_card(Card("A", "Hearts"))
	player2.deal_card(Card("K", "Hearts"))
	player2.deal_card(Card("K", "Spades"))
	assert (player2.close_game() == False)

	"""
	#test 3 - testing ace values
	player3 = Player("Narm", None, None)
	player3.deal_card(Card("K", "Diamonds"))
	player3.deal_card(Card("Q", "Diamonds"))
	player3.deal_card(Card("J", "Diamonds"))
	player3.deal_card(Card("A", "Diamonds"))
	sort_sequence(player3.stash)
	print(print_cards(player3.stash))


	#test 4 - testing joker in a book
	player4 = Player("Vatsala", None, None)
	player4.deal_card(Card("A", "Spades"))
	player4.deal_card(Card("6", "Diamonds"))
	player4.deal_card(Card("6", "Clubs"))
	player4.deal_card(Card("6", "Hearts"))
	player4.stash[0].isjoker=True
	assert (is_valid_book(player4.stash) == True)

	#test 5 - testing joker in a run
	player5 = Player("Tom", None, None)
	player5.deal_card(Card("3", "Diamonds"))
	player5.deal_card(Card("A", "Diamonds"))
	player5.deal_card(Card("7", "Hearts"))
	player5.deal_card(Card("4", "Diamonds"))
	#player5.stash[0].isjoker=True
	player5.stash[2].isjoker=True
	print(print_cards(player5.stash))
	assert (is_valid_run_joker(player5.stash) == True)

	#test 6 - testing is_valid_run
	player6 = Player("Tom", None, None)
	player6.deal_card(Card("J", "Diamonds"))
	player6.deal_card(Card("A", "Diamonds"))
	player6.deal_card(Card("Q", "Diamonds"))
	player6.deal_card(Card("K", "Diamonds"))
	print(print_cards(player6.stash))
	assert (is_valid_run(player6.stash) == True)


	#test 7 - testing push_joker_toend function
	player7 = Player("Tom", None, None)
	player7.deal_card(Card("A", "Spades"))
	player7.deal_card(Card("6", "Diamonds"))
	player7.deal_card(Card("7", "Hearts"))
	player7.deal_card(Card("9", "Diamonds"))
	player7.stash[0].isjoker=True
	player7.stash[2].isjoker=True
	print(print_cards(player7.stash))
	push_joker_toend(player7.stash)
	print(print_cards(player7.stash))
	"""

def main():
	""" Main Program """

	# Create Deck with 2 Packs
	deck = Deck(2)
	deck.shuffle()

	# Joker Logic is disabled currently.
	# deck.set_joker()

	# New game with 2 players
	g = Game(2, deck)

	# Deal Cards
	for i in range(13):
		for hand in g.players:
			card = deck.draw_card()
			hand.deal_card(card)

	# Create Pile
	first_card = deck.draw_card()
	g.add_pile(first_card)

	# Now let the Players begin
	g.play()

if __name__ == "__main__":
    main()
   	# unit_tests()





