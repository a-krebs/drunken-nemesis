from api import Vector2

class Defend(object):
    """
    Commands a bot to defend its current position.
    """

    def __init__(self, botId, facingDirection = None, description = ''):
        super(Defend, self).__init__()
        assert isinstance(botId, str)
        assert (facingDirection == None) or isinstance(facingDirection, Vector2)
        self.botId = botId
        """
        The name of the bot
        """
        self.facingDirection = facingDirection
        """
        The desired facing direction (Vector2) of the bot.
        """
        self.description = description
        """
        A description of the intention of the bot. This is displayed automatically if the commander sets self.verbose = True
        """

    def __str__(self):
        return "Defend {} facingDirection={} {}".format(self.botId, self.facingDirection, self.description)

class Move(object):
    """
    Commands a bot to run to a specified position without attacking visible enemies.
    """

    def __init__(self, botId, target, description = ''):
        super(Move, self).__init__()
        if isinstance(target, Vector2):
            target = [target];
        assert isinstance(botId, str)
        assert isinstance(target, list)
        for t in target: assert isinstance(t, Vector2)

        self.botId = botId
        """
        The name of the bot
        """
        self.target = target
        """
        The target destination (Vector2) or list of destination waypoints ([Vector2])
        """
        self.description = description
        """
        A description of the intention of the bot. This is displayed automatically if the commander sets self.verbose = True
        """

    def __str__(self):
        return "Move {} target={} {}".format(self.botId, self.target, self.description)


class Attack(object):
    """
    Commands a bot to attack a specified position. If an enemy bot is seen by this bot, it will be attacked.
    """

    def __init__(self, botId, target, lookAt = None, description = ''):
        super(Attack, self).__init__()
        if isinstance(target, Vector2):
            target = [target];
        assert isinstance(botId, str)
        assert isinstance(target, list)
        for t in target: assert isinstance(t, Vector2)
        assert lookAt == None or isinstance(lookAt, Vector2)
        self.botId = botId 
        """
        The name of the bot
        """
        self.target = target
        """
        The target destination (Vector2) or list of destination waypoints ([Vector2])
        """
        self.lookAt = lookAt
        """
        An optional position (Vector2) which the bot should look at while moving
        """
        self.description = description
        """
        A description of the intention of the bot. This is displayed automatically if the commander sets self.verbose = True
        """

    def __str__(self):
        return "Attack {} target={} lookAt={} {}".format(self.botId, self.target, self.lookAt, self.description)


class Charge(object):
    """
    Commands a bot to attack a specified position at a running pace. This is faster than Attack but incurs an additional firing delay penalty.
    """

    def __init__(self, botId, target, description = ''):
        super(Charge, self).__init__()
        if isinstance(target, Vector2):
            target = [target];
        assert isinstance(botId, str)
        assert isinstance(target, list)
        for t in target: assert isinstance(t, Vector2)

        self.botId = botId 
        """
        The name of the bot
        """
        self.target = target
        """
        The target destination (Vector2) or list of destination waypoints ([Vector2])
        """
        self.description = description
        """
        A description of the intention of the bot. This is displayed automatically if the commander sets self.verbose = True
        """

    def __str__(self):
        return "Charge {} target={} {}".format(self.botId, self.target, self.description)


def toJSON(python_object):
    if isinstance(python_object, Vector2):
        v = python_object
        return [v.x, v.y]

    if isinstance(python_object, Defend):
        command = python_object
        return {'__class__': 'Defend',
                '__value__': { 'bot': command.botId, 'facingDirection': command.facingDirection, 'description': command.description }}   

    if isinstance(python_object, Move):
        command = python_object
        return {'__class__': 'Move',
                '__value__': { 'bot': command.botId, 'target': command.target, 'description': command.description }}   

    if isinstance(python_object, Attack):
        command = python_object
        return {'__class__': 'Attack',
                '__value__': { 'bot': command.botId, 'target': command.target, 'lookAt': command.lookAt, 'description': command.description }}   

    if isinstance(python_object, Charge):
        command = python_object
        return {'__class__': 'Charge',
                '__value__': { 'bot': command.botId, 'target': command.target, 'description': command.description }}   

    raise TypeError(repr(python_object) + ' is not JSON serializable')

def toVector2List(list):
    if not list:
        return None

    result = []
    for i in list:
        result.append(toVector2(i))
    return result

def toVector2(list):
    if not list:
        return None
    assert len(list) == 2
    return Vector2(list[0], list[1])


def fromJSON(dct):
    if '__class__' in dct:
        if dct['__class__'] == 'Defend':
            value = dct['__value__']
            facingDirection = toVector2(value['facingDirection']) if value['facingDirection'] else None
            return Defend(value['bot'].encode('utf-8'), facingDirection, description = value['description'].encode('utf-8'))

        if dct['__class__'] == 'Move':
            value = dct['__value__']
            target = toVector2List(value['target'])
            return Move(value['bot'].encode('utf-8'), target, description = value['description'].encode('utf-8'))

        if dct['__class__'] == 'Attack':
            value = dct['__value__']
            target = toVector2List(value['target'])
            lookAt = toVector2(value['lookAt']) if value['lookAt'] else None
            return Attack(value['bot'].encode('utf-8'), target, lookAt = lookAt, description = value['description'].encode('utf-8'))

        if dct['__class__'] == 'Charge':
            value = dct['__value__']
            target = toVector2List(value['target'])
            return Charge(value['bot'].encode('utf-8'), target, description = value['description'].encode('utf-8'))

    return dct
