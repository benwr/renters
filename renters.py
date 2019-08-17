import itertools
import json
import sys


def happy_price(pref, housemates, myroom):
    if type(pref) == list:
        return pref[myroom]

    if pref["person"] in housemates:
        return happy_price(pref["in"], housemates, myroom)
    else:
        return happy_price(pref["out"], housemates, myroom)


def display(room_assignment, prices):
    result = []
    for room, (housemate, price) in enumerate(zip(room_assignment, prices)):
        result.append("  room {}: housemate {} for ${};".format(room, housemate, price))
    return "\n".join(result)


# choice should have num_rooms elements
def possible_room_assignments(rent, all_preferences, choice):
    choice_as_set = set(choice)
    for room_assignment in itertools.permutations(choice):
        prices = []
        total = 0
        for room, housemate in enumerate(room_assignment):
            p = happy_price(all_preferences[housemate], choice_as_set, room)
            total += p
            prices.append(p)
        if total >= rent:
            yield display(room_assignment, prices)


def find_all_covers(rent, housemate_preferences, num_rooms):
    for choice in itertools.combinations(range(len(housemate_preferences)), num_rooms):
        for res in  possible_room_assignments(rent, housemate_preferences, choice):
            yield res


def load_preferences():
    return json.load(sys.stdin)

# duck typing is for wimps!
def validate_individual_preference(num_people, pref, num_rooms=None, people_so_far=None):
    if type(pref) == list:
        if num_rooms is not None:
            assert num_rooms == len(pref)
        num_rooms = len(pref)
        for room_price in pref:
            assert type(room_price) == int or type(room_price) == float
            assert room_price >= 0
    else:
        assert type(pref) == dict
        assert "person" in pref
        assert "in" in pref
        assert "out" in pref
        if people_so_far is None:
            people_so_far = set()
        person = pref["person"]
        assert type(person) == int
        assert person not in people_so_far
        assert person < num_people and person >= 0
        new_num_rooms = validate_individual_preference(
                num_people,
                pref["in"],
                num_rooms=num_rooms,
                people_so_far=people_so_far.union({person}),
                )
        if num_rooms is not None:
            assert new_num_rooms == num_rooms
        num_rooms = validate_individual_preference(
                num_people,
                pref["out"],
                num_rooms=new_num_rooms,
                people_so_far=people_so_far.union({person})
                )
    return num_rooms


def validate_preferences(prefs):
    # prefs.json should have:
    # A list, with one item for each person
    #   For each person, a list of preference objects, forming a partition of
    #   the space of possible housemate sets (using a binary decision tree).
    #       Each of these preference objects has either:
    #           * a person index "person", a sub-preference-object "in", and
    #               a sub-preference-object "out"
    #           * or, a list of room prices describing the maximum rent amount
    #               willing to be paid, given the constraints on this situation.
    # That is, in haskell the preference objects are defined as approximately:
    # data Preference = Prices [Float] | Personal Person Preference Preference
    assert(type(prefs) == list)
    num_people = len(prefs)
    num_rooms = None
    for pref in prefs:
        new_num_rooms = validate_individual_preference(num_people, pref)
        if num_rooms is not None:
            assert num_rooms == new_num_rooms
        num_rooms = new_num_rooms
    assert num_people >= num_rooms
    print("your feelings are valid")
    return num_rooms

def main():
    rent = 8400
    preferences = load_preferences()
    num_rooms = validate_preferences(preferences)
    for cover in find_all_covers(rent, preferences, num_rooms):
        print("Found a cover: ")
        print(cover)

if __name__ == "__main__":
    main()
